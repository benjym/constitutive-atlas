// Coordinator-only executable package check; references and gates frozen before observations.
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),dir=resolve(process.argv[2]||'web/dist');
const json=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=json('engine-bingham/identity.json'),manifest=json('engine-bingham/package-manifest.json'),approval=json('engine-bingham/approval.json'),review=json('engine-bingham/review.json');
assert.equal(manifest.kind,'bingham-general-atlas-laboratory-v1');
for(const [path,sha]of Object.entries(manifest.files))assert.equal(hash(path),sha,path);
for(const [name,key]of [['bingham.mjs','module_sha256'],['bingham.wasm','wasm_sha256'],['models.json','catalogue_file_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],['review.html','review_html_sha256'],['source-receipts.json','source_receipts_sha256'],['build-receipt.json','build_receipt_sha256'],[identity.model+'.json','model_sha256']])assert.equal(hash('engine-bingham/'+name),identity[key],key);
for(const [path,sha]of Object.entries(identity.component_sha256))assert.equal(hash(path),sha,path);
assert.ok(!existsSync(join(dir,'bingham.html')),'Bingham must use the normal atlas laboratory');
const contract=await import(pathToFileURL(join(dir,'bingham-atlas-contract.mjs'))),{defaults,request,verifyResult,verifyApproval,verifyBuildReceipt,importRun,verifyReplay,types}=contract;
verifyApproval(identity,approval,review,json('engine-bingham/'+identity.model+'.json'));verifyBuildReceipt(identity,review,json('engine-bingham/build-receipt.json'));
const source=json('engine-bingham/source-receipts.json');assert.ok(review.artifacts.some(x=>x.path==='docs/ingestion/bingham-comsol63/source-v1/source-receipts.json'&&x.sha256===identity.source_receipts_sha256));assert.deepEqual(source.receipts.filter(x=>x.original&&x.url).map(x=>({url:x.url,sha256:x.sha256})),identity.source_sha256);
const ui=readFileSync(join(dir,'bingham-laboratory.mjs'),'utf8');assert.ok(ui.includes("document.querySelector('#laboratory > .lab-layout')"));assert.ok(ui.includes('All13state and6stress'));assert.ok(ui.includes('Measurement comparison is unavailable'));assert.ok(!ui.includes('<iframe'));
const policy=JSON.parse(readFileSync(join(root,'docs/ingestion/bingham-comsol63/interface-v1/POLICY-v2.json'))),referencePath='docs/ingestion/bingham-comsol63/execution-v1/cases.json',referenceBytes=readFileSync(join(root,referencePath));assert.equal(createHash('sha256').update(referenceBytes).digest('hex'),policy.frozen_inputs[referencePath]);
const cases=JSON.parse(referenceBytes).cases;
const engine=await(await import(pathToFileURL(join(dir,'engine-bingham/bingham.mjs')))).default({instantiateWasm(imports,receive){WebAssembly.instantiate(readFileSync(join(dir,'engine-bingham/bingham.wasm')),imports).then(({instance})=>receive(instance));return {};}});
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,json('engine-bingham/models.json').models);
const call=args=>JSON.parse(engine.ccall('atlas_run_schedule','string',types,args));let comparisons=0,nullRateMasks=0;const results=[];
for(const mode of policy.modes){
 const controls={...structuredClone(defaults),mode},args=request(controls,identity),reference=cases.find(x=>x.id==='public-'+mode),result=verifyResult(call(args),identity,controls);
 assert.ok(reference);assert.deepEqual(controls.parameters,reference.specification.parameters);assert.deepEqual(controls.initial,reference.specification.initial);assert.equal(controls.duration,reference.specification.segments[0].duration);assert.equal(controls.samples,reference.specification.segments[0].samples);if(mode==='rate')assert.deepEqual(controls.rates,reference.specification.segments[0].controls.map(x=>x.value));assert.equal(result.points.length,6);
 let maxStateError=0,maxStressError=0;
 for(const point of result.points){const expected=reference.references.find(p=>p.time===point.time);assert.ok(expected,'Independent frozen reference time');
  for(const [values,refs,absolute,kind]of [[point.state,expected.state,policy.accuracy.state_absolute,'state'],[point.observables,expected.stress,policy.accuracy.stress_absolute_pa,'stress']])for(let i=0;i<refs.length;i++){const error=Math.abs(values[i]-refs[i]);assert.ok(error<=Math.max(absolute,policy.accuracy.relative*Math.abs(refs[i])),`${mode} ${kind} t=${point.time} component=${i}: ${error}`);if(kind==='state')maxStateError=Math.max(maxStateError,error);else maxStressError=Math.max(maxStressError,error);comparisons++;}
  nullRateMasks+=point.strain_rate.filter(x=>x===null).length;
 }
 const doc={kind:'atlas-bingham-laboratory-v1',controls,provenance:identity,request:{function:'atlas_run_schedule',args},result};
 verifyReplay(call(request(importRun(JSON.stringify(doc),identity),identity)),result);
 const changed=structuredClone(doc);changed.result.points[2].state[12]+=0.1;changed.result.points[2].observables[3]+=100;const imported=importRun(JSON.stringify(changed),identity,{withResult:true});assert.throws(()=>verifyReplay(result,imported.result));
 for(const key of ['wasm_sha256','model_sha256','review_sha256','source_receipts_sha256'])assert.throws(()=>importRun(JSON.stringify({...doc,provenance:{...identity,[key]:'0'.repeat(64)}}),identity));
 const invalid=[...args];invalid[5]='-1'+args[5].slice(args[5].indexOf(','));const failed=call(invalid);assert.equal(failed.ok,false);assert.deepEqual(call(args),result,'Same-module recovery after rejection');
 results.push({mode,reference:reference.id,points:result.points.length,maxStateError,maxStressError,exactReplay:true,rejectedRequestRecovery:true});
}
assert.equal(nullRateMasks,6,'Only creep right-event strain rates are unresolved');
console.log(JSON.stringify({ok:true,model:identity.model,comparisons,nullRateMasks,guardedAssets:Object.keys(manifest.files).length,results,scope:'Synthetic numerical verification; actual browser qualification separate; no experimental validation'},null,2));
