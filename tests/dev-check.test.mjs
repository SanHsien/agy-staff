import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEV_CHECK = path.join(HERE, '..', 'tools', 'dev_check.ps1');

// The gate is documented as `powershell -File tools\dev_check.ps1` (Windows PowerShell 5.1) and
// CI runs it under pwsh 7. Both must be able to stop a timed-out batch.
const SHELLS = ['powershell.exe', 'pwsh'].filter(
  shell => !spawnSync(shell, ['-NoProfile', '-Command', 'exit 0'], { windowsHide: true }).error,
);

// A "test file" that never finishes and leaves a grandchild behind, reporting every pid it knows.
const HANGING_TEST = `
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import test from 'node:test';
const grandchild = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], { stdio: 'ignore', windowsHide: true });
fs.writeFileSync(process.env.HANG_PID_FILE, JSON.stringify([process.ppid, process.pid, grandchild.pid]));
test('never finishes', () => new Promise(() => {}));
`;

// Loads Invoke-FreshBatch (and its Stop-ProcessTree helper) out of dev_check.ps1 by parsing it (running the script would start the
// whole gate), calls it with a 3 second budget, then reports which of the pids are still alive.
const HARNESS = `
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile($env:DEV_CHECK, [ref]$null, [ref]$null)
foreach ($name in 'Stop-ProcessTree', 'Invoke-FreshBatch') {
  $fn = $ast.Find({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name }, $true)
  if ($fn) { Invoke-Expression $fn.Extent.Text }
}
$repoRoot = $env:FIXTURE_DIR
$result = Invoke-FreshBatch -BatchName 'hang' -Files @('hang.test.mjs') -TimeoutSeconds 3
Start-Sleep -Seconds 2
$pids = Get-Content -Raw -LiteralPath $env:HANG_PID_FILE | ConvertFrom-Json
$alive = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
Write-Output ('RESULT=' + (@{ status = $result.Status; alive = $alive } | ConvertTo-Json -Compress))
`;

function killTree(pids) {
  for (const pid of pids) spawnSync('taskkill.exe', ['/PID', String(pid), '/T', '/F'], { windowsHide: true });
}

for (const shell of SHELLS) {
  test(
    `${shell}: a timed-out batch is stopped together with every process it started`,
    { skip: process.platform !== 'win32' && 'dev_check.ps1 is the Windows gate' },
    t => {
      const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'agy-devcheck-'));
      const pidFile = path.join(dir, 'pids.json');
      t.after(() => {
        if (fs.existsSync(pidFile)) killTree(JSON.parse(fs.readFileSync(pidFile, 'utf8')));
        fs.rmSync(dir, { recursive: true, force: true });
      });
      fs.writeFileSync(path.join(dir, 'hang.test.mjs'), HANGING_TEST);
      const harness = path.join(dir, 'harness.ps1');
      fs.writeFileSync(harness, HARNESS);

      // Inside `node --test`, NODE_TEST_CONTEXT makes a nested `node --test` refuse to run files.
      const { NODE_TEST_CONTEXT: _outer, ...baseEnv } = process.env;
      // Output goes to a file, not a pipe: a leaked grandchild inherits the pipe and would keep
      // spawnSync waiting forever, turning the failure this test reports into a hang.
      const outFile = path.join(dir, 'harness.out');
      const out = fs.openSync(outFile, 'w');
      try {
        spawnSync(shell, ['-NoProfile', '-NonInteractive', '-File', harness], {
          stdio: ['ignore', out, out],
          windowsHide: true,
          timeout: 60_000,
          env: { ...baseEnv, DEV_CHECK, FIXTURE_DIR: dir, HANG_PID_FILE: pidFile },
        });
      } finally {
        fs.closeSync(out);
      }
      const stdout = fs.readFileSync(outFile, 'utf8');
      const line = stdout.split(/\r?\n/).find(l => l.startsWith('RESULT='));
      assert.ok(line, `harness gave no result:\n${stdout}`);
      const outcome = JSON.parse(line.slice('RESULT='.length));
      assert.equal(outcome.status, 'TIMEOUT');
      assert.deepEqual([].concat(outcome.alive), [], 'processes left running after the timeout');
    },
  );
}
