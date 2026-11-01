import test from 'node:test';
import assert from 'node:assert/strict';
import {MODEL,MODEL_SHA256,SETTINGS,MAX_ROWS,preset,validateRequest,validateIdentity,parseNumbers,parsePath,parseRunJSON,runPath,replayRequest,verifyReplay,wire} from '../web/orthotropic-contract.mjs';
const identity={model:MODEL,model_sha256:MODEL_SHA256,...Object.fromEntries(['catalogue_hash','catalogue_sha256','module_sha256','wasm_sha256','approval_sha256','review_sha256','review_html_sha256'].map(k=>[k,'1'.repeat(64)]))};
const settings=Object.fromEntries(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'].map((k,i)=>[k,SETTINGS[i]]));
// Transport-only mock, deliberately no constitutive physics.
const response=(w,ok=true)=>({ok,message:ok?'':'synthetic rejection',catalogue_hash:identity.catalogue_hash,model:MODEL,parameters:w.args[1].split(',').map(Number),initial:w.args[2].split(',').map(Number),strain:w.args[3].split(',').map(Number),state:w.args[2].split(',').map(Number),integration_settings:{version:'incremental-settings-0.1',norm:'scaled_component_max',...settings},diagnostics:{increment_fractions:[1],substeps:1}});
test('full nine-constant request, coupled admissibility and six-state contract',()=>{
 const good=preset();assert.deepEqual(validateRequest(good),good);
 for(const mutate of [r=>r.parameters[0]=0,r=>r.parameters[5]=-1,r=>r.parameters[8]=11,r=>r.parameters[6]=1,r=>r.parameters[7]=.9,r=>r.parameters.pop(),r=>r.initial.push(0),r=>r.initial[1]=NaN,r=>r.increments=[],r=>r.increments=Array(MAX_ROWS+1).fill(Array(6).fill(0)),r=>r.increments[0][0]=Infinity,r=>r.increments[0].pop(),r=>r.settings[3]=1,r=>r.model='other',r=>r.duration=1,r=>r.increments=[[1e308,0,0,0,0,0],[1e308,0,0,0,0,0]]]){const r=structuredClone(good);mutate(r);assert.throws(()=>validateRequest(r));}
 const custom=preset();custom.initial=[1,-2,3,4,-5,6];custom.parameters[6]=-.2;assert.deepEqual(validateRequest(custom),custom);
 assert.throws(()=>validateIdentity({...identity,model_sha256:'0'.repeat(64)}));assert.throws(()=>validateIdentity({...identity,extra:1}));assert.deepEqual(validateIdentity(identity),identity);
 for(const input of ['','1,2,3,4,5,','1,2,3,4,5,Infinity','1,2,3,4,5,NaN'])assert.throws(()=>parseNumbers(input,6));
 assert.deepEqual(parsePath('0,0,0,0,0,0\n1,2,3,4,5,6'),[Array(6).fill(0),[1,2,3,4,5,6]]);
 assert.deepEqual(wire(good,good.initial,good.increments[0]).types,Array(5).fill('string'));
});
test('strict JSON rejects nested duplicate/escaped keys, nonfinite and lossy integers',()=>{
 for(const text of ['{"a":1,"a":2}','{"a":{"x":1,"\\u0078":2}}','[1e400]','{"a":9007199254740993}','{"a":NaN}','[1,]'])assert.throws(()=>parseRunJSON(text));
 const good={s:'commas,:{}[] and "escaped"',a:[{x:1},{x:2}]};assert.deepEqual(parseRunJSON(JSON.stringify(good)),good);
});
test('immutable request, committed prefix, failure rollback and recovery',async()=>{
 const input=preset();let count=0;
 const run=await runPath(w=>{count++;input.increments[0][0]=123;return response(w);},input,identity);assert.equal(count,3);assert.equal(run.points.length,4);assert.equal(run.request.increments[0][0],.001);assert.equal(run.ok,true);
 count=0;const failed=await runPath(w=>response(w,++count!==2),preset(),identity);assert.equal(failed.ok,false);assert.equal(failed.failedRow,2);assert.equal(failed.points.length,2);assert.deepEqual(failed.points.at(-1).state,failed.records[1].response.initial);
 const recovered=await runPath(w=>response(w),preset(),identity);assert.deepEqual(recovered,await runPath(w=>response(w),preset(),identity));
 let calls=0;await assert.rejects(runPath(w=>{calls++;return response(w);},preset(),identity,{beforeStep:()=>{throw Error('superseded');}}));assert.equal(calls,0);
});
test('malformed responses never commit and failures must return complete incoming state',async()=>{
 for(const mutate of [r=>r.catalogue_hash='0'.repeat(64),r=>r.parameters[0]=1,r=>r.initial[0]=1,r=>r.strain[0]=1,r=>r.state.pop(),r=>r.state[0]=Infinity,r=>r.integration_settings.max_depth=1,r=>r.diagnostics.increment_fractions=[.5,.5],r=>{r.ok=false;r.state[0]=1;}]){const rejected=await runPath(w=>{const r=response(w);mutate(r);return r;},preset(),identity);assert.equal(rejected.ok,false);assert.equal(rejected.points.length,1);assert.match(rejected.message,/Engine response rejected/);}
});
test('fresh full-document replay rejects finite state, record, request and metadata tampering',async()=>{
 const result=await runPath(w=>response(w),preset(),identity);
 assert.deepEqual(replayRequest(result,identity),preset());assert.deepEqual(verifyReplay(await runPath(w=>response(w),replayRequest(result,identity),identity),result),result);
 for(const mutate of [r=>r.points[2].state[4]+=1,r=>r.records[1].response.state[5]+=1,r=>r.points[1].strain[0]+=.1,r=>r.records[0].wire.args[2]='1,2,3,4,5,6',r=>r.ok=false,r=>r.extra=1]){const saved=structuredClone(result);mutate(saved);assert.throws(()=>verifyReplay(result,saved));}
 for(const bad of [{...result,format:'other'},{...result,provenance:{...identity,wasm_sha256:'0'.repeat(64)}},{...result,provenance:{...identity,extra:1}},{...result,request:{...preset(),initial:[1]}}])assert.throws(()=>replayRequest(bad,identity));
 const reordered=Object.fromEntries(Object.entries(result).reverse());assert.deepEqual(verifyReplay(result,reordered),result);
});
