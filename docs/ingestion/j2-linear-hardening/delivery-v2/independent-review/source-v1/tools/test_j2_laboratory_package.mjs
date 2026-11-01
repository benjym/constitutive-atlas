// Actual copied generic Wasm: immutable identities and frozen independent J2 references.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const {MODEL,MODEL_SHA256,validateIdentity,preset,runPath,replayRequest}=await import(pathToFileURL(join(dir,'j2-contract.mjs')));
const identity=validateIdentity(read('material-point-j2/identity.json')),approval=read('material-point-j2/approval.json'),review=read('material-point-j2/review.json');
assert.equal(approval.status,'approved');assert.equal(review.status,'accepted');assert.equal(approval.model_id,MODEL);assert.equal(approval.definition.sha256,MODEL_SHA256);assert.equal(review.model.sha256,MODEL_SHA256);
for(const [p,key]of [['material-point-j2/'+MODEL+'.json','model_sha256'],['material-point-j2/models.json','catalogue_sha256'],['material-point-j2/j2.js','module_sha256'],['material-point-j2/j2.wasm','wasm_sha256'],['material-point-j2/approval.json','approval_sha256'],['material-point-j2/review.json','review_sha256']])assert.equal(hash(p),identity[key],p);
assert.equal(read('material-point-j2/models.json').sha256,identity.catalogue_hash);
for(const [p,h]of Object.entries(read('material-point-j2/package-manifest.json'))){assert.ok(!p.startsWith('/')&&!p.split('/').includes('..'));assert.equal(hash(p),h,p);}
const page=readFileSync(join(dir,'j2-laboratory.mjs'),'utf8');
for(const required of ['material-point-j2','j2-contract.mjs','URL.createObjectURL','instantiateWasm'])assert.ok(page.includes(required),required);
const app=readFileSync(join(dir,'app.js'),'utf8');assert.ok(app.includes('setupJ2Laboratory'));assert.ok(!app.includes('href="j2.html"'));
for(const retired of ['j2.html','sls.html','power-creep.html','recorded.html','publications.html'])assert.ok(!existsSync(join(dir,retired)),retired+' remains retired');
const engine=await(await import(pathToFileURL(join(dir,'material-point-j2/j2.js')))).default();
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,read('material-point-j2/models.json').models);assert.equal(descriptor.models.length,1);assert.equal(descriptor.models[0].id,MODEL);
const call=w=>JSON.parse(engine.ccall(w.function,'string',w.types,w.args));
let calls=0,comparisons=0,tangentComparisons=0,maxStressError=0,maxHistoryError=0;
function compare(state,expected,label){assert.equal(state.length,8);assert.equal(expected.length,8);for(let j=0;j<8;j++){assert.ok(Number.isFinite(state[j]),label);const error=Math.abs(state[j]-expected[j]);if(j<6)maxStressError=Math.max(maxStressError,error);else maxHistoryError=Math.max(maxHistoryError,error);assert.ok(error<=(j<6?.002:2e-10),`${label}: state ${j}: ${error}`);comparisons++;}}
const source=p=>JSON.parse(readFileSync(join(root,'docs/ingestion/j2-linear-hardening',p),'utf8'));
for(const filename of ['execution-v2/references.json','execution-v2/default-references.json']){
 const frozen=source(filename);
 for(const c of frozen.cases){
  const w={function:c.call,types:c.types,args:c.args},actual=call(w);calls++;assert.equal(actual.ok,c.ok,c.id+': '+actual.message);
  if(actual.state){compare(actual.state,c.expected,c.id);assert.equal(actual.catalogue_hash,identity.catalogue_hash);assert.equal(actual.model,MODEL);for(const [k,i]of [['parameters',1],['initial',2],['strain',3]])assert.deepEqual(actual[k],c.args[i].split(',').map(Number));}
  else assert.equal(c.expected,null,c.id);
  if(actual.ok)assert.deepEqual(actual.diagnostics.increment_fractions,[1],c.id);
  if(c.tangent){assert.equal(actual.tangent_ok,true);assert.equal(actual.state_tangent.length,8);for(let i=0;i<8;i++){assert.equal(actual.state_tangent[i].length,6);for(let j=0;j<6;j++){assert.ok(Number.isFinite(actual.state_tangent[i][j]));assert.ok(Math.abs(actual.state_tangent[i][j]-c.tangent[i][j])<=(i<6?.2:2e-8),`${c.id}: tangent ${i}/${j}`);tangentComparisons++;}}}
  assert.deepEqual(call(w),actual,c.id+': exact replay');calls++;
 }
}
for(const path of source('execution-v2/paths.json')){
 const r={model:MODEL,parameters:path.parameters,initial:path.initial,settings:path.integration_settings.split(',').map(Number),increments:path.increments};
 const result=await runPath(w=>{calls++;return call(w);},r,identity);assert.equal(result.ok,true,result.message);assert.equal(result.points.length,path.expected.length+1);
 path.expected.forEach((expected,i)=>compare(result.points[i+1].state,expected,`${path.id}/${i}`));
 const replay=await runPath(w=>{calls++;return call(w);},replayRequest(result,identity),identity);assert.deepEqual(replay,result,`${path.id}: propagated exact replay`);
}
const frozenPreset=source('delivery-v1/preset-references.json');
const presetRequest=frozenPreset.request||{model:MODEL,parameters:frozenPreset.parameters,initial:frozenPreset.initial,settings:frozenPreset.integration_settings.split(',').map(Number),increments:frozenPreset.increments};
assert.deepEqual(presetRequest,preset(),'Public preset differs from frozen independent references.');
const result=await runPath(w=>{calls++;return call(w);},presetRequest,identity);assert.equal(result.ok,true,result.message);assert.equal(result.points.length,4);assert.equal(frozenPreset.expected.length,3);frozenPreset.expected.forEach((expected,i)=>compare(result.points[i+1].state,expected,`preset/${i}`));
assert.deepEqual(await runPath(w=>{calls++;return call(w);},replayRequest(result,identity),identity),result,'preset import replay');
// A valid first row commits; overflow in row 2 exercises failed-prefix and recovery in this same module.
const bad=preset();bad.increments=[bad.increments[0],[1e300,-1e300,0,0,0,0]];
const failed=await runPath(w=>{calls++;return call(w);},bad,identity);assert.equal(failed.ok,false);assert.equal(failed.failedRow,2);assert.equal(failed.points.length,2);assert.deepEqual(failed.points[1].state,result.points[1].state);
const recovery=await runPath(w=>{calls++;return call(w);},preset(),identity);assert.deepEqual(recovery,result,'recovery after failed row');
const corruption=structuredClone(result);corruption.provenance.model_sha256='0'.repeat(64);assert.throws(()=>replayRequest(corruption,identity));
const report={passed:true,calls,stateComparisons:comparisons,tangentComparisons,maxStressError,maxHistoryError,immutableIdentity:true,exactReplay:true,preset:true,actualHistory:true,failedPrefix:true,recovery:true,corruptImportRejected:true,identity};
if(process.argv[3])writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
