import test from 'node:test';
import assert from 'node:assert/strict';
import {defaults,validateControls,request,importRun,verifyResult} from '../web/power-creep-contract.mjs';
const identity={model:'power-creep-itasca900-both-active-ode',model_sha256:'definition',catalogue_hash:'catalogue',module_sha256:'module',wasm_sha256:'wasm'};
const envelope=c=>({provenance:identity,request:{function:'atlas_run_schedule',args:request(c,identity)}});
test('both experiments and changed parameter/initial-state controls replay exactly',()=>{
 for(const mode of ['creep','relaxation'])for(const c of [{...defaults,mode},{...defaults,mode,duration:2,samples:7,pressure:2,initialQ:-.2,bulk:30,shear:15,pref:2,b1:.004,n1:1.5,b2:.002,n2:2.2}]){
  const replay=importRun(JSON.stringify(envelope(c)),identity);
  assert.deepEqual(request(replay,identity),request(c,identity));
 }
});
test('reject altered identity, arbitrary ABI/settings/non-axisymmetric history and injection',()=>{
 for(const mutate of [d=>d.provenance={...identity,wasm_sha256:'other'},d=>d.request.function='atlas_evaluate_time',d=>d.request.args[8]=1e-2,d=>d.request.args[2]='1200000,900000,900000,1,0,0',d=>d.request.args[3]='1,0,0,0,0,0',d=>d.request.args[5]='1,1,1,'+Array(17).fill(0).join(','),d=>d.request.args[6]='other',d=>d.request.args[1]='20000000,12000000,1000000,.002,.5,.001,3,1']){
  const d=envelope(defaults);mutate(d);assert.throws(()=>importRun(JSON.stringify(d),identity));
 }
 for(const text of ['{"request":{},"request":{}}','{"x":1e999}'])assert.throws(()=>importRun(text,identity));
});
test('strict finite bounds and returned full-state shape prevent stale/invalid exports',()=>{
 for(const c of [{...defaults,duration:0},{...defaults,samples:1.5},{...defaults,shear:NaN},{...defaults,n2:.5}])assert.throws(()=>validateControls(c));
 assert.throws(()=>verifyResult({ok:false,catalogue_hash:identity.catalogue_hash,message:'budget'},identity),/budget/);
 assert.throws(()=>verifyResult({ok:true,catalogue_hash:'wrong'},identity),/identity/);
 const point={state:Array(6).fill(1),strain:Array(6).fill(0),observables:Array(9).fill(1)};
 const good={ok:true,catalogue_hash:identity.catalogue_hash,points:[point,point]};assert.equal(verifyResult(good,identity),good);
 assert.throws(()=>verifyResult({...good,points:[point,{...point,state:[1]}]},identity),/state/);
});
