import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, '..');
const BASELINE_PATH = path.join(ROOT, 'tools', 'upstream_baseline.json');
const CHECKER_PATH = path.join(ROOT, 'tools', 'check_upstream_updates.py');
const LINK_CHECKER_PATH = path.join(ROOT, 'tools', 'check_links.py');

test('upstream_baseline.json contains required watermarks and valid format', () => {
  assert.ok(fs.existsSync(BASELINE_PATH), 'upstream_baseline.json should exist');
  const baseline = JSON.parse(fs.readFileSync(BASELINE_PATH, 'utf8'));

  assert.equal(baseline.repo, 'https://github.com/keli-wen/agy-staff.git');
  assert.equal(baseline.branch, 'master');
  assert.match(baseline.reviewed_through, /^[0-9a-f]{40}$/);
  assert.match(baseline.reviewed_release, /^v\d+\.\d+\.\d+$/);
  assert.match(baseline.reviewed_date, /^\d{4}-\d{2}-\d{2}$/);
  assert.ok(typeof baseline.reviewed_pr_through === 'number');
  assert.ok(typeof baseline.reviewed_issue_through === 'number');
  assert.equal(baseline.track, 'release');
});

test('check_upstream_updates.py runs cleanly against current baseline', () => {
  const result = spawnSync('python', [CHECKER_PATH], {
    cwd: ROOT,
    encoding: 'utf8',
    env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /Upstream review report/);
});

test('check_links.py finds zero broken relative links', () => {
  const result = spawnSync('python', [LINK_CHECKER_PATH], {
    cwd: ROOT,
    encoding: 'utf8',
    env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /0\s*份有缺檔|0.*failed/i);
});
