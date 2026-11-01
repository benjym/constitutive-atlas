// Saved exports and pure transport functions only. Never loads an engine/worker.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';
const root=process.argv[2],base=path.join(root,'docs/ingestion/maxwell-itasca900/atlas-integration-v1'),load=p=>JSON.parse(fs.readFileSync(p,'utf8')),site=load(path.join(base,'package-manifest-v1.json')).package;
const c=await import(pathToFileURL(path.join(site,'maxwell-atlas-contract.mjs'))),identity=load(path.join(site,'engine-maxwell/identity.json')),dir=path.join(base,'browser-exports');let checked=0;
for(const n of fs.readdirSync(dir).filter(n=>n.startsWith('browser-')&&n.endsWith('.json'))){const text=fs.readFileSync(path.join(dir,n),'utf8'),run=load(path.join(dir,n)),imported=c.importRun(text,identity);c.verifyResult(run.result,identity,run.controls);assert.deepEqual(imported.controls,run.controls);assert.deepEqual(c.exportRun(run.controls,run.result,identity),run);checked++;}
for(const n of c.presetNames){const run=load(path.join(dir,`browser-${n}.json`));assert.deepEqual(run.controls,c.preset(n));}
const baseline=load(path.join(dir,'browser-relaxation.json')),replayed=load(path.join(dir,'browser-replayed.json'));c.verifyReplay(baseline,replayed);
const badIdentity=fs.readFileSync(path.join(dir,'bad-identity.json'),'utf8');assert.throws(()=>c.importRun(badIdentity,identity),/exact Maxwell package/);
const bad=load(path.join(dir,'bad-result.json'));c.importRun(JSON.stringify(bad),identity);assert.throws(()=>c.verifyReplay(baseline,bad),/differs/);
assert.notDeepEqual(bad.result,baseline.result);assert.deepEqual(bad.result.points.at(-1).state,bad.result.points.at(-1).observables);
console.log(JSON.stringify({passed:true,complete_export_identity_request_result_checks:checked,four_source_presets:true,full_replay_exact:true,identity_tamper_rejected:true,structurally_consistent_result_tamper_requires_recompute:true,compiled_calls:0},null,2));
