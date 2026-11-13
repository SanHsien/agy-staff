import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sandbox, run, agyCalls, jobIdOf } from './helpers.mjs';

test('explicit model families normalize and continuation preserves legacy Flash', () => {
  const sb = sandbox('model-families');
  for (const [model, effort, expected] of [
    ['carbon', 'high', 'gemini-4-carbon-high'],
    ['argon', 'low', 'gemini-4-argon-low'],
    ['hydrogen', 'xhigh', 'gemini-4-hydrogen-xhigh'],
    ['gemini-4-carbon', 'medium', 'gemini-4-carbon-medium'],
    ['gemini-4-argon-high', 'low', 'gemini-4-argon-high'],
    ['flash', 'low', 'gemini-3.8-flash-low'],
  ]) {
    const result = run(sb, ['ask', '--model', model, '--effort', effort, '--prompt', 'check']);
    assert.equal(result.code, 0, result.stderr);
    const argv = agyCalls(sb).at(-1);
    assert.equal(argv[argv.indexOf('--model') + 1], expected);
  }
  const first = run(sb, ['ask', '--model', 'flash', '--prompt', 'legacy']);
  assert.equal(first.code, 0, first.stderr);
  const continued = run(sb, ['continue', '--job', jobIdOf(first.stderr), '--prompt', 'follow up']);
  assert.equal(continued.code, 0, continued.stderr);
  const argv = agyCalls(sb).at(-1);
  assert.equal(argv[argv.indexOf('--model') + 1], 'gemini-3.8-flash-medium');
});

test('explicit Carbon failure recommends Argon without retrying', () => {
  const sb = sandbox('explicit-carbon');
  const result = run(sb, ['ask', '--model', 'carbon', '--prompt', 'check'], {
    FAKE_AGY_STATUS: 'ERROR', FAKE_AGY_RESPONSE: '',
    FAKE_AGY_ERROR: 'unknown model: gemini-4-carbon-medium',
    FAKE_AGY_MODELS_OUTPUT: 'gemini-4-argon-medium\tArgon\ngemini-4-hydrogen-medium\tHydrogen',
  });
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /recommendation: --model gemini-4-argon-medium/);
  assert.equal(agyCalls(sb).filter(args => args.includes('-p')).length, 1);
});

for (const error of ['429 Resource exhausted: quota exceeded', '401 Unauthorized: Invalid credentials', '403 Permission denied: caller does not have access to workspace']) {
  test(`model errors never retry or query a replacement on ${error}`, () => {
    const sb = sandbox('no-model-retry');
    const result = run(sb, ['ask', '--model', 'carbon', '--prompt', 'check'], {
      FAKE_AGY_STATUS: 'ERROR', FAKE_AGY_RESPONSE: '', FAKE_AGY_ERROR: error,
    });
    assert.notEqual(result.code, 0);
    assert.equal(agyCalls(sb).length, 1);
    assert.doesNotMatch(result.stderr, /compatible recommendation/);
  });
}
