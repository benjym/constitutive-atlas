import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {replayRecorded} from '../web/recorded-worker.mjs';
import {createRecordedDocument,parseRecordedDocument,recordedDocumentCSV} from '../web/recorded-document.mjs';

const [engineDirectory,fixtureFile,expectedFile] = process.argv.slice(2);
assert.ok(engineDirectory && fixtureFile && expectedFile,
  'Supply the engine directory, fixed catalogue/preset and frozen expected result.');
const read = async path => JSON.parse(await readFile(path,'utf8'));
const {catalogue,preset} = await read(fixtureFile);
const expected = await read(expectedFile);
const create = (await import(pathToFileURL(resolve(engineDirectory,'weighted-history.mjs')))).default;
const engine = await create();
const result = replayRecorded(engine,preset,catalogue);
assert.equal(result.ok,true);
assert.equal(result.points.length,33);
assert.deepEqual(result.points,expected.points);
assert.deepEqual(result.state,expected.state);
const saved = createRecordedDocument(preset,result,catalogue);
assert.deepEqual(parseRecordedDocument(JSON.stringify(saved),catalogue).result,result);
const csv = recordedDocumentCSV(preset,result,catalogue);
assert.equal(csv.split('\n').length,34);
assert.match(csv.split('\n')[0],/effective_stress_xx_Pa/);
assert.throws(() => replayRecorded(engine,{...preset,stress_scope:'total'},catalogue),/scope\/model binding mismatch/);
assert.deepEqual(replayRecorded(engine,preset,catalogue).points,result.points);
console.log(JSON.stringify({pass:true,model:result.model,catalogue_hash:result.catalogue_hash,observations:result.points.length,roundTrip:true,invalidScopeRecovery:true}));
