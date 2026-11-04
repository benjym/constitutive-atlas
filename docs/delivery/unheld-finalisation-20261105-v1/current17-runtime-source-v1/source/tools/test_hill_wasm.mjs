#!/usr/bin/env node
// Portable fresh-build qualification. Never writes reviewed execution evidence.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const evidence = fs.realpathSync(path.join(root, 'docs/ingestion/hill-abaqus2025/execution-v1'));
const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  assert(['--module', '--output'].includes(key) && process.argv[i + 1] && !options[key], 'use --module PATH --output DIR');
  options[key] = process.argv[i + 1];
}
assert(options['--module'] && options['--output'], 'use --module PATH --output DIR');
const modulePath = fs.realpathSync(options['--module']);
const outputRequested = path.resolve(options['--output']);
// Resolve each existing parent to prevent symlink aliases into immutable evidence.
let ancestor = outputRequested;
while (!fs.existsSync(ancestor)) ancestor = path.dirname(ancestor);
const resolvedOutput = path.resolve(fs.realpathSync(ancestor), path.relative(ancestor, outputRequested));
assert(resolvedOutput !== evidence && !resolvedOutput.startsWith(evidence + path.sep), 'output must not be inside immutable execution-v1');
fs.mkdirSync(resolvedOutput, { recursive: true });
const output = fs.realpathSync(resolvedOutput);
const save = (name, value) => fs.writeFileSync(path.join(output, name), JSON.stringify(value, null, 2) + '\n');
const read = name => JSON.parse(fs.readFileSync(path.join(evidence, name), 'utf8'));
const hash = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const refs = read('references.json'), negatives = read('negative-requests.json');
const frozen = JSON.parse(fs.readFileSync(path.join(evidence, '../ci-v1/frozen-inputs.json'), 'utf8'));
for (const [name, expected] of Object.entries(frozen)) assert.equal(hash(path.join(root, name)), expected, `immutable qualifier input changed: ${name}`);
assert.equal(refs.cases.length, 31);
assert.equal(refs.cases.reduce((n, c) => n + c.increments.length, 0), 41);
const modelPath = path.join(root, 'models/research/hill', refs.model + '.json');
assert.equal(hash(modelPath), refs.model_sha256, 'source model differs from frozen references');
const engine = await (await import(pathToFileURL(modulePath).href)).default();
const calls = [];
const call = (parameters, initial, strain, settings = refs.settings) => {
  const request = [refs.model, parameters.join(','), initial.join(','), strain.join(','), settings];
  const text = engine.ccall('atlas_integrate_with_settings', 'string', Array(5).fill('string'), request);
  calls.push({ request, response: text }); save('wasm-calls.json', calls);
  return JSON.parse(text);
};
const raw = [];
let worstStress = 0, worstMultiplier = 0, physicalCalls = 0;
for (const c of refs.cases) {
  const runs = [];
  for (let repeat = 0; repeat < 2; repeat++) {
    let state = c.initial;
    const rows = [];
    for (const de of c.increments) {
      const row = call(c.parameters, state, de); rows.push(row);
      if (row.ok !== true) break;
      state = row.state;
    }
    runs.push(rows);
  }
  raw.push({ id: c.id, runs }); save('wasm-raw.json', raw);
  assert.deepEqual(runs[0], runs[1], `${c.id}: exact repeat failed`);
  for (const rows of runs) {
    assert.equal(rows.length, c.expected.length);
    let parent = c.initial;
    for (let j = 0; j < rows.length; j++) {
      const row = rows[j], expected = c.expected[j];
      assert.equal(row.ok, true, c.id);
      assert.deepEqual(row.initial, parent); assert.deepEqual(row.parameters, c.parameters);
      assert.deepEqual(row.strain, c.increments[j]); assert.equal(row.state.length, 7);
      for (let k = 0; k < 7; k++) {
        assert(Number.isFinite(row.state[k]));
        const error = Math.abs(row.state[k] - expected[k]);
        const limit = k < 6 ? .01 + 1e-10 * Math.abs(expected[k]) : 1e-9;
        assert(error <= limit, `${c.id}, component${k}, error${error}, limit${limit}`);
        if (k < 6) worstStress = Math.max(worstStress, error);
        else worstMultiplier = Math.max(worstMultiplier, error);
      }
      parent = row.state; physicalCalls++;
    }
  }
}
const good = refs.cases.find(c => c.id === 'elastic-0--1');
const valid = () => call(good.parameters, good.initial, good.increments[0]);
const baseline = valid(); assert.equal(baseline.ok, true);
const negativeRows = [];
for (const c of negatives.cases) {
  const failed = call(c.parameters, c.initial, c.strain), recovered = valid();
  negativeRows.push({ id: c.id, failed, recovered }); save('wasm-negative-raw.json', negativeRows);
  assert.equal(failed.ok, false);
  if (c.id === 'outside-yield') assert.deepEqual(failed.state, c.initial);
  else assert(!Object.hasOwn(failed, 'state'), 'parameter prevalidation must reject before state response');
  assert.deepEqual(recovered, baseline, 'post-rejection recovery differs');
}
const plastic = refs.cases.find(c => c.id === 'mixed-nonproportional');
const invoke = settings => call(plastic.parameters, plastic.initial, plastic.increments[0], settings);
const before = invoke(refs.settings), failed = invoke('1e-11,1e-6,1,0,1,0'), after = invoke(refs.settings);
save('wasm-rollback-raw.json', { before, failed, after });
assert.equal(before.ok, true); assert.equal(failed.ok, false);
assert.deepEqual(failed.state, plastic.initial); assert.deepEqual(after, before);
const report = { passed: true, qualification: 'fresh-build bounded behavior; not new scientific approval',
  cases: refs.cases.length, increments: refs.cases.reduce((n, c) => n + c.increments.length, 0), calls: physicalCalls,
  max_stress_error_Pa: worstStress, max_multiplier_error: worstMultiplier,
  negative_cases: negativeRows.length, full_state_rollback: true, exact_recovery: true,
  module_sha256: hash(modulePath), model_sha256: hash(modelPath),
  references_sha256: hash(path.join(evidence, 'references.json')),
  policy_sha256: hash(path.join(evidence, 'POLICY.md')),
  negative_requests_sha256: hash(path.join(evidence, 'negative-requests.json')) };
save('report.json', report); console.log(JSON.stringify(report, null, 2));
