import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root='/private/tmp/atlas-vibe2026-controlled-time-v1';
const evidence=path.dirname(new URL(import.meta.url).pathname);
const {ControlledTimeEngine,canonical}=await import(pathToFileURL(root+'/web/controlled-time-engine.mjs'));
const read=p=>fs.readFileSync(p),json=p=>JSON.parse(read(p));
const hash=p=>createHash('sha256').update(read(p)).digest('hex');
const build=root+'/.local/vibe-wasm-model-v1';
const {default:create}=await import(pathToFileURL(build+'/atlas_controlled_time_capability.mjs'));
const module=await create({wasmBinary:read(build+'/atlas_controlled_time_capability.wasm'),print:()=>{},printErr:()=>{}});
const definition=json(root+'/models/research/vibe/vibe-2026-explicit-appendix-a.json');
const engine=await ControlledTimeEngine.create(module,read(build+'/generated/controlled_time_catalogue.json'),definition);
const examples=json(root+'/docs/ingestion/vibe-2026/public-examples-v1/examples.json');
const cases=examples.map(e=>{const result=json(evidence+'/wasm-vibe-results/'+e.id+'.json');assert.equal(canonical(result.request),canonical(e.request));return {id:e.id,request:e.request,result};});
const failures=[];
for(const suction of [0,-1]){
 const request=structuredClone(examples[0].request);request.context.controls.suction=suction;
 const before=canonical(request);let error;
 try{engine.run(request);}catch(e){error=e.message;}
 assert.ok(error,'Expected suction refusal');assert.equal(canonical(request),before);
 const recovered=engine.run(examples[0].request);assert.equal(canonical(recovered),canonical(cases[0].result));
 failures.push({id:suction===0?'zero-suction':'negative-suction',request,error,recovery_example:examples[0].id});
}
const output=root+'/docs/ingestion/vibe-2026/public-qualification-v1';fs.mkdirSync(output);
const results={kind:'controlled-time-actual-public-results-v1',cases,failures};
fs.writeFileSync(output+'/expected-results.json',JSON.stringify(results,null,2)+'\n',{flag:'wx'});
const receipt={status:'pass',model:definition.id,cases:cases.length,failures:failures.length,inputs:{module_sha256:hash(build+'/atlas_controlled_time_capability.mjs'),wasm_sha256:hash(build+'/atlas_controlled_time_capability.wasm'),examples_sha256:hash(root+'/docs/ingestion/vibe-2026/public-examples-v1/examples.json'),native_summary_sha256:hash(evidence+'/native-vibe-results/summary.json'),wasm_summary_sha256:hash(evidence+'/wasm-vibe-results/summary.json')},results_sha256:hash(output+'/expected-results.json'),note:'All8 results copied byte-values from actual qualified Wasm histories. Public zero and negative suction requests were actually refused and each followed by exact valid-example recovery; model CABI raw refusals are separately retained in original E4 journal.'};
fs.writeFileSync(output+'/actual-public-receipt.json',JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(receipt));
