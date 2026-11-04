// Execute the packaged common Wasm and compare complete state to frozen source references.
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=read('engine-sls/identity.json'),approval=read('engine-sls/approval.json'),review=read('engine-sls/review.json'),manifest=read('engine-sls/package-manifest.json');
assert.equal(manifest.kind,'sls-general-atlas-laboratory-v1');assert.equal(review.status,'accepted');assert.equal(approval.status,'approved');assert.equal(approval.definition.sha256,identity.model_sha256);assert.equal(review.model.sha256,identity.model_sha256);
for(const [path,expected]of Object.entries(manifest.files))assert.equal(hash(path),expected,path);
for(const [name,key]of [['sls.mjs','module_sha256'],['sls.wasm','wasm_sha256'],['models.json','catalogue_file_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],['review.html','review_html_sha256'],[identity.model+'.json','model_sha256']])assert.equal(hash('engine-sls/'+name),identity[key]);
for(const [path,expected]of Object.entries(identity.component_sha256))assert.equal(hash(path),expected,path);
assert.equal(read('engine-sls/models.json').sha256,identity.catalogue_hash);assert.ok(!existsSync(join(dir,'sls.html')),'Standalone SLS page must remain absent.');
const ui=readFileSync(join(dir,'sls-laboratory.mjs'),'utf8');assert.ok(ui.includes("document.querySelector('#laboratory > .lab-layout')"));assert.ok(ui.includes('All12state and6stress'));assert.ok(ui.includes('Measurement comparison is unavailable'));assert.ok(!ui.includes('<iframe'));assert.ok(!ui.includes('sls.html'));
const {defaults,request,importRun,verifyResult,verifyReplay,types}=await import(pathToFileURL(join(dir,'sls-atlas-contract.mjs')));
const engine=await(await import(pathToFileURL(join(dir,'engine-sls/sls.mjs')))).default({instantiateWasm(imports,receive){WebAssembly.instantiate(readFileSync(join(dir,'engine-sls/sls.wasm')),imports).then(({instance})=>receive(instance));return {};}});
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,read('engine-sls/models.json').models);
const cases=JSON.parse(readFileSync(join(root,'docs/ingestion/sls-comsol63/execution-v1/cases.json'))).cases;
const call=args=>JSON.parse(engine.ccall('atlas_run_schedule','string',types,args));let comparisons=0,nullRateMasks=0;
for(const [mode,id]of [['relaxation','relax-schedule'],['creep','creep-schedule'],['rate','load-hold-reverse']]){
 const c={...structuredClone(defaults),mode,...(mode==='rate'?{duration:1}:{})},args=request(c,identity),result=verifyResult(call(args),identity,c),reference=cases.find(x=>x.id===id);
 for(const point of result.points){const expected=reference.references.find(x=>x.time===point.time);assert.ok(expected,'Frozen reference time');
  for(let i=0;i<12;i++){assert.ok(Math.abs(point.state[i]-expected.state[i])<=(i<6?3e-8:1),`${mode} state ${point.time}/${i}`);comparisons++;}
  for(let i=0;i<6;i++){assert.ok(Math.abs(point.observables[i]-expected.stress[i])<=1,`${mode} stress ${point.time}/${i}`);comparisons++;}
  nullRateMasks+=point.strain_rate.filter(x=>x===null).length;
 }
 const doc={kind:'atlas-sls-laboratory-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args},result},replay=importRun(JSON.stringify(doc),identity);verifyReplay(call(request(replay,identity)),result);const tampered=structuredClone(doc);tampered.result.points[2].state[9]+=100;tampered.result.points[2].observables[3]+=100;const changed=importRun(JSON.stringify(tampered),identity,{withResult:true});assert.throws(()=>verifyReplay(result,changed.result));
 assert.throws(()=>importRun(JSON.stringify({...doc,provenance:{...identity,wasm_sha256:'0'.repeat(64)}}),identity));
 if(mode==='relaxation'){const bad=[...args];bad[5]=args[5].replace(/^8,/, '-1,');assert.equal(call(bad).ok,false);assert.deepEqual(call(args),result,'Persistent module recovery after failed request');}
}
console.log(JSON.stringify({ok:true,model:identity.model,fullStateStressComparisons:comparisons,nullRateMaskEntries:nullRateMasks,exactReplay:true,failedRequestRecovery:true,allPackageAssetsGuarded:Object.keys(manifest.files).length,standalonePageAbsent:true},null,2));
