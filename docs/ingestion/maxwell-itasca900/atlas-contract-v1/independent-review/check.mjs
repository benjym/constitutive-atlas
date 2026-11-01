// Review-only saved-wire probes; never loads a compiled engine.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('../../../../../',import.meta.url);
const {modelId,modelSha256,request,verifyResult,verifyReplay,exportRun,importRun,parseRunJSON}=await import(new URL('web/maxwell-atlas-contract.mjs',root));
const keys=['schema_version','units','model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments','solver'];
let count=0,restarts=0;let chosen;
for(const backend of ['native','wasm'])for(const suffix of ['raw','transactions-raw']){
 const rows=JSON.parse(readFileSync(new URL(`docs/ingestion/maxwell-itasca900/integration-v1/${backend}-${suffix}.json`,root)));
 for(const row of rows)for(const call of row.calls){const r=JSON.parse(call.stdout);if(!r.ok||!r.points||row.id==='refine-coarse')continue;
  const c=Object.fromEntries(keys.map(k=>[k,structuredClone(r[k])])),identity={model:modelId,model_sha256:modelSha256,catalogue_hash:r.catalogue_hash,release_revision:'independent-saved-fixture'};
  verifyResult(r,identity,c);const restored=importRun(JSON.stringify(exportRun(c,r,identity)),identity);verifyReplay(restored.result,r);
  const args=request(c,identity),expected=[modelId,c.parameters.join(','),c.initial.join(','),c.initial_strain.join(','),c.initial_strain_rate.join(','),c.segments.flatMap(s=>[s.duration,s.samples,...s.controls.flatMap(v=>[v.quantity==='stress'?1:0,v.kind==='rate'?1:0,v.value??0])]).join(','),c.segments.map(s=>s.id).join(','),c.start_time,1e-8,1e-11,1e-12,1e6,100000,1e-10,40];assert.deepEqual(args,expected);
  count++;if(row.id.startsWith('restart-'))restarts++;if(row.id==='load-hold-reverse')chosen={r,c,identity};
 }
}
assert.equal(count,32);assert.equal(restarts,8);
for(const mutate of [r=>r.extra=1,r=>r.points[2].extra=1,r=>delete r.points[2].strain_rate[0]]){const r=structuredClone(chosen.r);mutate(r);assert.throws(()=>verifyResult(r,chosen.identity,chosen.c));}
for(const text of ['{"x":1,"\\u0078":2}','[{"x":null,"x":false}]','{"n":9007199254740993}','{"n":1e999}'])assert.throws(()=>parseRunJSON(text));
const altered=structuredClone(chosen.r);altered.points[2].strain[5]+=1e-9;assert.throws(()=>verifyReplay(altered,chosen.r));
console.log(JSON.stringify({passed:true,successful_saved_schedule_responses:count,restart_schedule_responses:restarts,resolved_findings:['exact result and point keys','sparse strain-rate rejection','durable restart fixture coverage'],abi_arguments:15,compiled_calls:0,builds:0,browser_approval:false},null,2));
