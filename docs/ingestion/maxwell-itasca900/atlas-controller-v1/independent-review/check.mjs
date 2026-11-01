import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const root=new URL('../../../../../',import.meta.url);
const {createMaxwellRunner}=await import(new URL('web/maxwell-atlas-runner.mjs',root));
const {modelId,modelSha256,request,exportRun}=await import(new URL('web/maxwell-atlas-contract.mjs',root));
const rows=JSON.parse(readFileSync(new URL('docs/ingestion/maxwell-itasca900/integration-v1/native-raw.json',root))),result=JSON.parse(rows.find(r=>r.id==='load-hold-reverse').calls[0].stdout);
const controls=Object.fromEntries(['schema_version','units','model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments','solver'].map(k=>[k,structuredClone(result[k])]));
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:result.catalogue_hash,module_sha256:'a'.repeat(64),wasm_sha256:'b'.repeat(64),release_revision:'independent-mocked-probe'};
const workers=[],events=[],timers=new Map(),retained=[];let next=0;
const runner=createMaxwellRunner({createWorker(){const w={postMessage(d){this.sent=d;},terminate(){this.terminated=true;}};workers.push(w);return w;},notify:e=>events.push(e),setTimer:cb=>{retained.push(cb);timers.set(++next,cb);return next;},clearTimer:id=>timers.delete(id)});
const reply=w=>w.onmessage({data:{id:w.sent.id,result:structuredClone(result),identity:structuredClone(identity),args:request(controls,identity)}});
runner.run(controls);const old=workers[0],staleTimer=retained[0];runner.run(controls);const current=workers[1],before=events.length;
staleTimer();reply(old);old.onerror({message:'late error'});assert.equal(events.length,before);assert.equal(current.terminated,undefined);reply(current);assert.equal(events.at(-1).state,'complete');assert.equal(timers.size,0);const saved=runner.last;
staleTimer();assert.deepEqual(runner.last,saved);
for(const field of ['module_sha256','wasm_sha256']){const imported=exportRun(controls,result,identity);imported.provenance[field]='c'.repeat(64);runner.run(controls,{expected:imported});reply(workers.at(-1));assert.equal(events.at(-1).state,'error');assert.equal(runner.last,null);assert.equal(timers.size,0);}
runner.run(controls);reply(workers.at(-1));assert.equal(events.at(-1).state,'complete');runner.cancel();assert.equal(runner.last,null);
console.log(JSON.stringify({passed:true,stale_timer_message_error_callbacks_ignored:true,imported_module_and_wasm_provenance_rejected:true,recovery_and_cancel_clear_results:true,compiled_calls:0,builds:0,real_browser:false},null,2));
