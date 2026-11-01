import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {defaults,modelId,modelSha256,validateControls,request,importRun,verifyResult,parseRunJSON,verifyReplay} from '../web/sls-atlas-contract.mjs';
const fixture=mode=>JSON.parse(readFileSync(new URL('../docs/reviews/sls-web-v1/browser-'+mode+'.json',import.meta.url))).result;
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:fixture('default').catalogue_hash,module_sha256:'module',wasm_sha256:'wasm',component_sha256:{'sls-atlas-contract.mjs':'contract'}};
const controls=(mode='relaxation')=>({...structuredClone(defaults),mode,...(mode==='rate'?{duration:1}:{})});
const doc=mode=>{const c=controls(mode);return {kind:'atlas-sls-laboratory-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args:request(c,identity)},result:fixture(mode==='relaxation'?'default':mode)};};
test('rate/hold wire controls retain physical time and full12state',()=>{
 for(const mode of ['relaxation','creep','rate']){const c=controls(mode),args=request(c,identity),wire=args[5].split(',').map(Number);assert.equal(args[2].split(',').length,12);assert.equal(args[7],0);for(let i=0;i<6;i++){assert.equal(wire[2+3*i],+(mode==='creep'));assert.equal(wire[3+3*i],+(mode==='rate'));assert.equal(wire[4+3*i],mode==='rate'?c.rates[i]:0);}verifyResult(doc(mode).result,identity,c);assert.deepEqual(importRun(JSON.stringify(doc(mode)),structuredClone(identity)),c);}
});
test('invalid controls rejected without mutating caller/defaults',()=>{
 const baseline=JSON.stringify(defaults);
 for(const delta of [{mode:'unknown'},{duration:0},{duration:Infinity},{samples:1.5},{start:-1},{start:1e30,duration:1},{parameters:[20e6,8e6,12e6,0]},{parameters:[20e6,8e6,12e6,1e31]},{rates:[0]},{initial:Array(12).fill(NaN)},{initial:[...defaults.initial.slice(0,6),5001,-2000,-3000,1000,-500,250]},{extra:1}])assert.throws(()=>validateControls({...structuredClone(defaults),...delta}));
 const c=validateControls(defaults);c.initial[0]=99;assert.equal(JSON.stringify(defaults),baseline);
});
test('strict JSON rejects duplicate keys, nonfinite overflow and unsafe integers',()=>{
 for(const text of ['{"x":1,"x":2}','{"x":1,"\\u0078":2}','{"nested":{"x":1,"x":2}}','{"x":1e999}','{"x":9007199254740993}'])assert.throws(()=>parseRunJSON(text));
 assert.deepEqual(parseRunJSON('{"x":1,"y":{"x":2},"s":"1e999"}'),{x:1,y:{x:2},s:'1e999'});
});
test('import rejects wrong model/engine/component identity, wire and result mutations',()=>{
 for(const mutate of [d=>d.provenance.model='other',d=>d.provenance.wasm_sha256='other',d=>d.provenance.component_sha256['sls-atlas-contract.mjs']='other',d=>d.request.args[14]=39,d=>d.controls.initial.pop(),d=>d.result.points[2].state.pop(),d=>d.result.points[2].observables[0]=null,d=>d.result.points[2].time=3,d=>d.result.solver.maximum_depth=39,d=>d.result.points[1].side='left',d=>d.result.points[0].strain[0]=9,d=>d.result.points[2].strain_rate=Array(6).fill(null)]){const d=structuredClone(doc('relaxation'));mutate(d);assert.throws(()=>importRun(JSON.stringify(d),identity));}
 assert.throws(()=>request(defaults,{...identity,model_sha256:'changed'}));
 assert.deepEqual(importRun(JSON.stringify(doc('relaxation')),identity),defaults);
});

test('exact numerical replay rejects finite later branch/stress tampering',()=>{
 const original=doc('relaxation'),changed=structuredClone(original);changed.result.points[2].state[9]+=100;changed.result.points[2].observables[3]+=100;
 const imported=importRun(JSON.stringify(changed),identity,{withResult:true});assert.deepEqual(imported.controls,defaults);assert.throws(()=>verifyReplay(original.result,imported.result),/differs/);assert.deepEqual(verifyReplay(original.result,structuredClone(original.result)),original.result);
 const reordered=Object.fromEntries(Object.entries(original.result).reverse());assert.deepEqual(verifyReplay(original.result,reordered),original.result);
});
