import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, '..');

test('dependency freshness checker contract tests pass (offline)', () => {
  const result = spawnSync('python', ['-m', 'unittest', 'tests/test_dependency_freshness.py'], {
    cwd: ROOT,
    encoding: 'utf8',
    env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
  });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
});
