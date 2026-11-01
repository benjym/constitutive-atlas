// Pure JavaScript contract checks against saved data; no Wasm/compiled calls.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dirname,resolve,join} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const {defaults,request,validateControls,importRun,verifyResult}=await import(pathToFileURL(join(root,'web/timed-contract.mjs')));
const calls=JSON.parse(readFileSync(join(root,'docs/ingestion/burgers-itasca900/delivery-v1/release-build-v2/wasm/calls.json')));
const descriptor=calls.find(x=>x.label==='descriptor').response;
const identity={model:defaults.model??'burgers-itasca900-dry-zero-spin-ode',catalogue_hash:descriptor.sha256,
 model_sha256:'1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c',module_sha256:'a'.repeat(64),wasm_sha256:'b'.repeat(64),approval_sha256:'c'.repeat(64),review_sha256:'d'.repeat(64)};
const clone=structuredClone;
let passed=0;
for(const mode of ['relaxation','creep']){
 const c={...clone(defaults),mode},r=calls.find(x=>x.label===mode).response;
 assert.equal(verifyResult(r,identity,c),r);passed++;
 const doc={kind:'atlas-timed-hold-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args:request(c,identity)},result:r};
 assert.deepEqual(importRun(JSON.stringify(doc),identity),c);passed++;
 for(const [key,value]of [['duration',0],['duration',101],['samples',0],['samples',201],['samples',1.5],['start',-1],['parameters',[1,2,3,4,0]],['initial',Array(12).fill(1)],['strain',[0,0]],['rate',[0,0,0,0,0,Infinity]]]){
  assert.throws(()=>validateControls({...c,[key]:value}));passed++;
 }
 for(const key of ['model','model_sha256','catalogue_hash','module_sha256','wasm_sha256','approval_sha256','review_sha256']){
  assert.throws(()=>importRun(JSON.stringify({...doc,provenance:{...identity,[key]:'different'}}),identity));passed++;
 }
 const bad=clone(doc);bad.request.args[8]=1e-3;
 assert.throws(()=>importRun(JSON.stringify(bad),identity));passed++;
 assert.throws(()=>importRun(JSON.stringify(doc).replace('"kind":','"kind":"duplicate","kind":'),identity));passed++;
 assert.throws(()=>importRun(JSON.stringify(doc).replace('"kind":','"unused":1e999,"kind":'),identity));passed++;
 for(const mutate of [x=>x.catalogue_hash='wrong',x=>x.points[2].state[0]=NaN,x=>x.points[2].observables[0]++,x=>x.points[2].strain_rate.fill(null),x=>x.points[1].state[0]++,x=>x.points.at(-1).time++,x=>x.solver.relative_tolerance=1e-3,x=>x.units='kPa',x=>x.schema_version='0.3',x=>x.parameters[0]++,x=>x.points[2].side='right',x=>x.points[2].segment=1]){
  const corrupt=clone(r);mutate(corrupt);assert.throws(()=>verifyResult(corrupt,identity,c));passed++;
 }
}
// Follow-up regression probes for the two hardening changes reported by review.
const c=clone(defaults),r=clone(calls.find(x=>x.label==='relaxation').response);
let unknownAccepted=false,offGridAccepted=false;
try{validateControls({...c,unsupported_temperature:100});unknownAccepted=true;}catch{}
r.points[2].time=(r.points[1].time+r.points[2].time)/2;
try{verifyResult(r,identity,c);offGridAccepted=true;}catch{}
assert.equal(unknownAccepted,false);assert.equal(offGridAccepted,false);passed+=2;
console.log(JSON.stringify({pure_contract_assertions:passed,compiled_calls:0,
 unknown_control_field_accepted:unknownAccepted,off_grid_interior_time_accepted:offGridAccepted,
 diagnostic_scope:'hardening probes; no assertion that the identified engine emits these mutations'},null,2));
