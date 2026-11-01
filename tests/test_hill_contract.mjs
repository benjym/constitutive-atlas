import assert from 'node:assert/strict';
import {MODEL,MODEL_SHA256,SETTINGS,MAX_ROWS,preset,validateRequest,validateIdentity,parseNumbers,parsePath,runPath,replayRequest,wire} from '../web/hill-contract.mjs';
const identity={model:MODEL,model_sha256:MODEL_SHA256,...Object.fromEntries(['catalogue_hash','catalogue_sha256','module_sha256','wasm_sha256','approval_sha256','review_sha256'].map(k=>[k,'1'.repeat(64)]))};
let assertions=0;
// Initial-state admission checks exercise the physical-shear to Mandel mapping.
for (const [index,weight] of [[0,.5+.3],[1,.7+.3],[2,.7+.5],[3,2],[4,1.2],[5,1.7]]) {
 const r=preset();r.initial[index]=r.parameters[3]/Math.sqrt(weight)*(1-1e-8);
 assert.doesNotThrow(()=>validateRequest(r));
 r.initial[index]=r.parameters[3]/Math.sqrt(weight)*(1+1e-8);
 assert.throws(()=>validateRequest(r));assertions+=2;
}
const hydro=preset();hydro.initial=[1e12,1e12,1e12,0,0,0,0];assert.doesNotThrow(()=>validateRequest(hydro));assertions++;
for(let i=4;i<10;i++)for(const value of [0,-1,1e-7,101,Infinity,NaN]){const r=preset();r.parameters[i]=value;assert.throws(()=>validateRequest(r));assertions++;}

const good=preset();assert.deepEqual(validateRequest(good),good);assertions++;
for(const mutate of [r=>r.parameters[0]=0,r=>r.parameters[2]=-1,r=>r.parameters[4]=-1,r=>r.parameters.pop(),r=>r.initial[6]=-1,r=>r.initial[6]=1,r=>r.initial[3]=1e9,r=>r.initial.pop(),r=>r.increments=[],r=>r.increments=Array(MAX_ROWS+1).fill(Array(6).fill(0)),r=>r.increments[0][0]=Infinity,r=>r.increments[0].pop(),r=>r.settings[0]=1e-5,r=>r.parameters[0]=NaN,r=>r.model='other',r=>r.duration=1,r=>r.increments=[[1e308,0,0,0,0,0],[1e308,0,0,0,0,0]]]){const r=structuredClone(good);mutate(r);assert.throws(()=>validateRequest(r));assertions++;}
for(const input of ['','1,2,3,4,5,','1,2,3,4,5,Infinity','1,2,3,4,5,NaN']){assert.throws(()=>parseNumbers(input,6));assertions++;}
assert.deepEqual(parsePath('0,0,0,0,0,0\n1,2,3,4,5,6'),[Array(6).fill(0),[1,2,3,4,5,6]]);assertions++;
assert.throws(()=>validateIdentity({...identity,model_sha256:'0'.repeat(64)}));assertions++;
const settings=Object.fromEntries(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'].map((k,i)=>[k,SETTINGS[i]]));
const response=(w,ok=true)=>({ok,message:ok?'':'synthetic rejection',catalogue_hash:identity.catalogue_hash,model:MODEL,parameters:w.args[1].split(',').map(Number),initial:w.args[2].split(',').map(Number),strain:w.args[3].split(',').map(Number),state:w.args[2].split(',').map(Number),integration_settings:{version:'incremental-settings-0.1',norm:'scaled_component_max',...settings},diagnostics:{increment_fractions:[1],substeps:1}});
const input=preset();let count=0;
const run=await runPath(w=>{count++;input.increments[0][0]=123;return response(w);},input,identity);assert.equal(count,3);assert.equal(run.points.length,4);assert.equal(run.request.increments[0][0],.003);assert.equal(run.ok,true);assertions+=4;
const failed=await runPath(w=>response(w,++count!==5),good,identity);assert.equal(failed.ok,false);assert.equal(failed.failedRow,2);assert.equal(failed.points.length,2);assert.equal(failed.records.length,2);assert.deepEqual(failed.points.at(-1).state,failed.records[1].response.initial);assertions+=5;
const recovered=await runPath(w=>response(w),good,identity);assert.deepEqual(recovered,await runPath(w=>response(w),good,identity));assertions++;
assert.deepEqual(replayRequest(recovered,identity),good);assert.deepEqual(replayRequest({...recovered,result:'untrusted'},identity),good);assertions+=2;
for(const bad of [{...recovered,format:'other'},{...recovered,provenance:{...identity,wasm_sha256:'0'.repeat(64)}},{...recovered,provenance:{...identity,extra:1}},{...recovered,request:{...good,initial:[1]}}]){assert.throws(()=>replayRequest(bad,identity));assertions++;}
for(const mutate of [r=>r.catalogue_hash='0'.repeat(64),r=>r.parameters[0]=1,r=>r.initial[0]=1,r=>r.strain[0]=1,r=>r.state.pop(),r=>r.state.push(0),r=>r.state[0]=Infinity,r=>r.integration_settings.max_depth=1,r=>r.diagnostics.increment_fractions=[.5,.5],r=>{r.ok=false;r.state[0]=1;}]){const rejected=await runPath(w=>{let r=response(w);mutate(r);return r;},good,identity);assert.equal(rejected.ok,false);assert.equal(rejected.points.length,1);assert.match(rejected.message,/Engine response rejected/);assertions++;}
assert.deepEqual(wire(good,good.initial,good.increments[0]).types,Array(5).fill('string'));assertions++;
let calls=0;await assert.rejects(runPath(w=>{calls++;return response(w);},good,identity,{beforeStep:()=>{throw Error('superseded');}}));assert.equal(calls,0);assertions++;
// Late completion after a changed selection is rejected before another engine call.
let superseded=false,latestCalls=0;
await assert.rejects(runPath(w=>{latestCalls++;superseded=true;return response(w);},good,identity,{beforeStep:()=>{if(superseded)throw Error('Superseded inputs.');}}));
assert.equal(latestCalls,1);assertions++;
console.log(JSON.stringify({passed:true,assertions,compiledCalls:0,scope:'Pure Hill request/identity/replay/transaction contract, including immutable inputs, failure prefix and recovery.'},null,2));
