import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const dest = resolve(process.argv[2]);
const read = name => JSON.parse(readFileSync(resolve(dest,name)));
const root = 'engine-certified-return/';
const {catalogue,preset} = read(root+'recorded.json');
assert.equal(read('certified-recorded.json'),preset.model);
assert.deepEqual(catalogue.models,[read(root+'model.json')]);
const create = (await import(pathToFileURL(resolve(dest,root+'certified-return.mjs')))).default;
const engine = await create({printErr() {}});
const {replayRecorded} = await import(pathToFileURL(resolve(dest,'recorded-worker.mjs')));
const expected = JSON.parse(readFileSync(new URL('../docs/ingestion/extended-mohr-coulomb-2013/certified-public-backend-v1/recorded-wasm.json',import.meta.url)));
assert.deepEqual(replayRecorded(engine,preset,catalogue),expected);
console.log('Certified recorded package matches the reviewed Wasm response.');
