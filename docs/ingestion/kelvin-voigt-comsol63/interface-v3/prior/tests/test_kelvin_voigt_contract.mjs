import test from 'node:test';
import assert from 'node:assert/strict';
import {defaults,modelId,modelSha256,solver,validateControls,request,verifyResult,parseRunJSON,importRun,verifyReplay} from '../web/kelvin-voigt-contract.mjs';
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:'synthetic-transport-fixture',component_sha256:{'kelvin-voigt-contract.mjs':'fixture'}};
// Synthetic shape fixtures exercise transport validation, not engine/numerical evidence.
function doc(mode='creep'){
 const c={...structuredClone(defaults),mode},result={catalogue_hash:identity.catalogue_hash,model:modelId,ok:true,units:'SI',schema_version:'0.2',start_time:c.start,parameters:c.parameters,initial:c.initial,initial_strain:c.initial,initial_strain_rate:c.initialRates,solver,points:Array.from({length:c.samples+2},(_,i)=>({time:i<2?c.start:c.start+c.duration*(i-1)/c.samples,side:i===1?'right':'left',segment:i===0?-1:0,state:[...c.initial],strain:[...c.initial],strain_rate:i===0?[...c.initialRates]:i===1&&mode==='creep'?Array(6).fill(null):Array(6).fill(0),observables:Array(6).fill(0)}))};
 return {kind:'atlas-kelvin-voigt-laboratory-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args:request(c,identity)},result};
}
test('all-six initial rates and mode masks survive exact wire/import',()=>{
 for(const mode of ['creep','rate','hold']){const d=doc(mode),args=d.request.args,w=args[5].split(',').map(Number);assert.equal(args[2].split(',').length,6);assert.equal(args[4],defaults.initialRates.join(','));assert.equal(args[6],mode==='hold'?'relaxation':mode);for(let i=0;i<6;i++){assert.equal(w[2+3*i],+(mode==='creep'));assert.equal(w[3+3*i],+(mode==='rate'));assert.equal(w[4+3*i],mode==='rate'?defaults.rates[i]:0);}assert.deepEqual(importRun(JSON.stringify(d),identity),d.controls);}
});
test('strict controls reject invalid inputs and preserve caller',()=>{
 const before=JSON.stringify(defaults);for(const change of [{mode:'relaxation'},{samples:0},{duration:0},{duration:Infinity},{start:-1},{start:1e30,duration:1},{parameters:[20e6,12e6,0]},{parameters:[1,1,1e31]},{initial:[0]},{initialRates:[NaN,0,0,0,0,0]},{rates:[0]},{extra:1}])assert.throws(()=>validateControls({...structuredClone(defaults),...change}));const c=validateControls(defaults);c.initial[0]=7;assert.equal(JSON.stringify(defaults),before);
});
test('strict JSON rejects duplicates overflow and inexact integers',()=>{
 for(const s of ['{"a":1,"a":2}','{"a":1,"\\u0061":2}','{"a":{"b":1,"b":2}}','{"x":1e999}','{"x":9007199254740993}'])assert.throws(()=>parseRunJSON(s));assert.deepEqual(parseRunJSON('{"x":"1e999","a":{"x":1}}'),{x:'1e999',a:{x:1}});
});
test('import/result guards cover identity full state incoming rate event and solver',()=>{
 for(const mutate of [d=>d.provenance={...identity,model:'wrong'},d=>d.provenance={...identity,component_sha256:{}},d=>d.request.args[4]='0,0,0,0,0,0',d=>d.result.initial_strain_rate=Array(6).fill(0),d=>d.result.points[2].state.pop(),d=>d.result.points[2].strain[0]=1,d=>d.result.points[2].strain_rate=Array(6).fill(null),d=>d.result.points[2].observables[5]=null,d=>d.result.points[1].side='left',d=>d.result.points[2].time=123,d=>d.result.solver={...solver,maximum_depth:39}]){const d=structuredClone(doc());mutate(d);assert.throws(()=>importRun(JSON.stringify(d),identity));}assert.throws(()=>request(defaults,{...identity,model_sha256:'wrong'}));
});
test('full numerical replay rejects finite tampering',()=>{
 const d=doc(),changed=structuredClone(d);changed.result.points[3].observables[4]+=1;const imported=importRun(JSON.stringify(changed),identity,{withResult:true});assert.throws(()=>verifyReplay(d.result,imported.result));assert.deepEqual(verifyReplay(d.result,structuredClone(d.result)),d.result);assert.deepEqual(verifyResult(d.result,identity,d.controls),d.result);
});
