// Coordinator-only compiled check: actual packaged common engine against frozen source references.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const site=resolve(process.argv[2]||'web/dist'),repo=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const raw=p=>readFileSync(join(site,p)),read=p=>JSON.parse(raw(p)),hash=p=>createHash('sha256').update(raw(p)).digest('hex');
const {MODEL,MODEL_SHA256,SETTINGS,preset,validateIdentity,runPath,replayRequest,verifyReplay,parseRunJSON}=await import(pathToFileURL(join(site,'orthotropic-contract.mjs')));
const prefix='material-point-orthotropic/',identity=validateIdentity(read(prefix+'identity.json'));
for(const [p,key]of [['model.json','model_sha256'],['models.json','catalogue_sha256'],['orthotropic.js','module_sha256'],['orthotropic.wasm','wasm_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],['review.html','review_html_sha256']])assert.equal(hash(prefix+p),identity[key],p);
const manifest=read(prefix+'package-manifest.json');
for(const [p,h]of Object.entries(manifest)){assert.match(p,/^[a-zA-Z0-9._/-]+$/);assert.ok(!p.startsWith('/')&&!p.split('/').some(x=>x==='..'||x==='.'));assert.match(h,/^[a-f0-9]{64}$/);assert.equal(hash(p),h,p);}
for(const p of ['orthotropic-contract.mjs','orthotropic-laboratory.mjs',...['orthotropic.js','orthotropic.wasm','models.json','model.json','identity.json','approval.json','review.json','review.html'].map(v=>prefix+v)])assert.ok(Object.hasOwn(manifest,p),'Missing manifest asset '+p);
const approval=read(prefix+'approval.json'),review=read(prefix+'review.json');assert.equal(approval.status,'approved');assert.equal(approval.definition.sha256,MODEL_SHA256);assert.equal(review.status,'accepted');assert.equal(review.model.sha256,MODEL_SHA256);
const catalogue=read(prefix+'models.json');assert.equal(catalogue.sha256,identity.catalogue_hash);
const source=p=>JSON.parse(readFileSync(join(repo,'docs/ingestion/orthotropic-ogs',p),'utf8'));
const sourceChecks=source('source-v1/checks.json');assert.equal(sourceChecks.candidate_sha256,MODEL_SHA256);assert.equal(sourceChecks.status,'pass');
// Instantiate already-hashed bytes through the same supported hook used by the browser.
const compiled=await WebAssembly.compile(raw(prefix+'orthotropic.wasm'));
const engine=await(await import(pathToFileURL(join(site,prefix+'orthotropic.js')))).default({instantiateWasm(imports,receive){const instance=new WebAssembly.Instance(compiled,imports);receive(instance);return instance.exports;}});
const descriptor=parseRunJSON(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,catalogue.models);assert.equal(descriptor.models.length,1);assert.equal(descriptor.models[0].id,MODEL);
const call=w=>parseRunJSON(engine.ccall(w.function,'string',w.types,w.args));let calls=0,comparisons=0,maxError=0;
const compare=(actual,expected,label)=>{assert.equal(actual.length,6);assert.equal(expected.length,6);actual.forEach((v,j)=>{assert.ok(Number.isFinite(v));const e=Math.abs(v-expected[j]);maxError=Math.max(maxError,e);assert.ok(e<=1e-6,`${label}/${j}: ${e} Pa > frozen 1e-6 Pa tolerance`);comparisons++;});};
const keys=['E1','E2','E3','G12','G23','G13','nu12','nu23','nu13'],references=source('source-v1/references.json');
for(const c of references){
 const request={model:MODEL,parameters:keys.map(k=>c.parameters[k]),initial:c.previous_state,settings:[...SETTINGS],increments:[c.strain_increment]};
 const result=await runPath(w=>{calls++;return call(w);},request,identity);assert.equal(result.ok,true,c.case+': '+result.message);compare(result.points[1].state,c.expected_state,c.case);
 const replay=await runPath(w=>{calls++;return call(w);},replayRequest(result,identity),identity);verifyReplay(replay,result);
}
// The frozen default component witnesses independently provide the linear operator.
const basis=Array.from({length:6},(_,j)=>references.find(c=>c.case===`default-${j}`));assert.ok(basis.every(Boolean));
const defaultRequest=preset();basis.forEach(c=>assert.deepEqual(keys.map(k=>c.parameters[k]),defaultRequest.parameters));
let expected=[...defaultRequest.initial];const result=await runPath(w=>{calls++;return call(w);},defaultRequest,identity);assert.equal(result.ok,true,result.message);
defaultRequest.increments.forEach((row,i)=>{expected=expected.map((v,j)=>v+row.reduce((sum,e,k)=>sum+e*(basis[k].expected_state[j]-basis[k].previous_state[j])/basis[k].strain_increment[k],0));compare(result.points[i+1].state,expected,`preset/${i}`);});
verifyReplay(await runPath(w=>{calls++;return call(w);},replayRequest(result,identity),identity),result);
for(const mutate of [r=>r.points[2].state[5]+=1,r=>r.records[1].response.state[0]+=1,r=>r.points[1].strain[4]+=.1]){const bad=structuredClone(result);mutate(bad);assert.throws(()=>verifyReplay(result,bad));}
const bad=preset();bad.increments=[bad.increments[0],[1e308,0,0,0,0,0]];
const failed=await runPath(w=>{calls++;return call(w);},bad,identity);assert.equal(failed.ok,false);assert.equal(failed.failedRow,2);assert.equal(failed.points.length,2);assert.deepEqual(failed.points[1].state,result.points[1].state);
verifyReplay(await runPath(w=>{calls++;return call(w);},preset(),identity),result);
assert.ok(!existsSync(join(site,'orthotropic.html')),'No standalone page');
assert.match(readFileSync(join(site,'app.js'),'utf8'),/setupOrthotropicLaboratory/);
const report={passed:true,calls,referenceCases:references.length,stateComparisons:comparisons,maxAbsoluteErrorPa:maxError,tolerancePa:1e-6,exactVerifiedWasm:true,immutableIdentity:true,fullDocumentReplay:true,finiteTamperRejected:true,failedPrefix:true,recovery:true,preset:true,identity};
if(process.argv[3])writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
