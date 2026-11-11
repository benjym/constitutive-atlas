// Exercise the live ordinary catalogue through the same scoped API as the lab.
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {bundle} from './build_laboratory_examples.mjs';
import {prepareExample} from '../web/laboratory-examples.mjs';
import {laboratoryStress,runScopedLaboratory} from '../web/laboratory-scope.mjs';
import {laboratoryExample} from '../web/state-contract.mjs';
import {normalizeSettings} from '../web/numerics.mjs';
import {createLoading} from '../web/loading.mjs';

const [nativePath, wasmPath] = process.argv.slice(2);
assert.ok(nativePath && wasmPath, 'Usage: node tools/test_current_catalogue.mjs NATIVE WASM_DIR');
const native = resolve(nativePath), wasm = resolve(wasmPath);
const root = fileURLToPath(new URL('..', import.meta.url));
const read = path => JSON.parse(readFileSync(path, 'utf8'));
const catalogue = read(join(wasm, 'generated/models.json'));
const definitionFiles = new Map(catalogue.models.map(m => ['./models/' + m.id + '.json', join(root, 'models', m.id + '.json')]));
assert.ok(catalogue.models.length, 'Empty compiled catalogue');
const engine = await (await import(pathToFileURL(join(wasm, 'atlas.js')))).default();
const temp = mkdtempSync(join(tmpdir(), 'atlas-current-catalogue-'));
try {
  const index = await bundle(root, temp, catalogue);
  const fetcher = async url => ({
    ok: true,
    text: async () => readFileSync(definitionFiles.get(url) ?? resolve(temp, url), 'utf8'),
  });
  const nativeEngine = {
    ccall(name, type, types, args) {
      let command = ['--describe'];
      if (name !== 'atlas_describe') {
        const [model, parameters, initial, protocol] = args;
        command = ['--response-contract', 'stress-scope-0.1', '--model', model, '--parameters', parameters,
          '--initial', initial, '--protocol', String(protocol)];
        if (name === 'atlas_run_controls_scope_with_settings') {
          const loading = join(temp, 'controls.csv');
          writeFileSync(loading, args[4]);
          command.push('--mode', 'run-controls', '--laboratory-controls-file', loading, '--integration-settings', args[5]);
        } else {
          assert.equal(name, 'atlas_run_scope_with_settings');
          command.push('--target', String(args[4]), '--steps', String(args[5]), '--cycles', String(args[6]),
            '--integration-settings', args[7]);
        }
      }
      const result = spawnSync(native, command, {encoding: 'utf8', timeout: 30000, maxBuffer: 16 * 1024 * 1024});
      if (result.error) throw result.error;
      assert.equal(result.signal, null);
      assert.equal(result.stderr, '', 'native stderr');
      assert.equal(result.status, JSON.parse(result.stdout).ok === false ? 1 : 0, 'native exit code');
      return result.stdout;
    },
  };
  let count = 0;
  for (const model of catalogue.models) {
    const entries = index.examples.filter(entry => entry.model === model.id);
    const cases = [];
    if (entries.length) {
      for (const entry of entries) {
        const {specification} = await prepareExample(entry, index, catalogue, {fetcher});
        cases.push([entry.id, specification]);
      }
    } else {
      const {parameters, initial} = laboratoryExample(model);
      const spec = {response_contract: 'stress-scope-0.1', stress_scope: laboratoryStress(model).scope,
        model: model.id, parameters, initial, protocol: 1, target: .01, steps: 100, cycles: 0,
        integration_settings: normalizeSettings()};
      spec.loading = createLoading(spec);
      cases.push(['default drained compression', spec]);
    }
    for (const [label, spec] of cases) {
      const context = model.id + ' / ' + label;
      try {
        const a = runScopedLaboratory(nativeEngine, spec, catalogue);
        const b = runScopedLaboratory(engine, spec, catalogue);
        assert.ok(a.ok, 'native: ' + a.message);
        assert.ok(b.ok, 'Wasm: ' + b.message);
        assert.equal(a.points.length, spec.steps + 1, 'native committed points');
        assert.equal(b.points.length, a.points.length, 'Wasm committed points');
        for (let i = 0; i < a.points.length; i++) {
          for (const key of ['state', 'strain', 'p', 'q', 'q_signed', 'u']) {
            const expected = [a.points[i][key]].flat(), actual = [b.points[i][key]].flat();
            assert.equal(actual.length, expected.length, 'point ' + i + ' ' + key + ' width');
            for (let j = 0; j < expected.length; j++) {
              const x = expected[j], y = actual[j], location = 'point ' + i + ' ' + key + '[' + j + ']';
              if (x === null || y === null) assert.equal(y, x, location);
              else assert.ok(Number.isFinite(x) && Number.isFinite(y) &&
                Math.abs(x - y) <= 1e-7 * Math.max(1, Math.abs(x), Math.abs(y)), location + ': ' + x + ' vs ' + y);
            }
          }
        }
        console.log('PASS ' + context);
        count++;
      } catch (error) {
        throw new Error(context + ': ' + error.message, {cause: error});
      }
    }
  }
  console.log('Current catalogue: ' + count + ' successful examples across ' + catalogue.models.length + ' models.');
} finally {
  rmSync(temp, {recursive: true, force: true});
}
