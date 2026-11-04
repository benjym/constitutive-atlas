import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import {resolve,join,dirname} from 'node:path';import {pathToFileURL,fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=read('engine-burgers/identity.json'),review=read('engine-burgers/review.json'),approval=read('engine-burgers/approval.json');
assert.equal(review.status,'accepted');assert.equal(approval.status,'approved');assert.equal(approval.definition.sha256,identity.model_sha256);assert.equal(review.model.sha256,identity.model_sha256);
for(const [file,key]of [['burgers.mjs','module_sha256'],['burgers.wasm','wasm_sha256'],['models.json','catalogue_file_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],[identity.model+'.json','model_sha256']])assert.equal(hash('engine-burgers/'+file),identity[key]);
for(const [p,h]of Object.entries(read('engine-burgers/package.json').files))assert.equal(hash(p),h,p);
const {defaults,request,importRun,verifyResult}=await import(pathToFileURL(join(dir,'timed-contract.mjs')));
const engine=await(await import(pathToFileURL(join(dir,'engine-burgers/burgers.mjs')))).default();
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,read('engine-burgers/models.json').models);
const old=JSON.parse(readFileSync(join(root,'docs/ingestion/burgers-itasca900/integration-v1/wasm-calls.json')));
let comparisons=0,nullMasks=0;
for(const mode of ['relaxation','creep']){
 const c={...structuredClone(defaults),mode},args=request(c,identity);
 const r=verifyResult(JSON.parse(engine.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],args)),identity,c);
 const saved=old.find(x=>x.label===mode).response;assert.equal(r.points.length,saved.points.length);
 for(let i=0;i<r.points.length;i++)for(const field of ['state','strain','strain_rate','observables'])for(let j=0;j<r.points[i][field].length;j++){
  const a=r.points[i][field][j],b=saved.points[i][field][j];if(a===null||b===null){assert.equal(a,b,'Initial event null-rate mask');nullMasks++;}else{assert.ok(Math.abs(a-b)<=1e-10*Math.max(1,Math.abs(b)),`${mode}/${field}/${i}/${j}`);comparisons++;}
 }
 const doc={kind:'atlas-timed-hold-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args},result:r};
 const replay=importRun(JSON.stringify(doc),identity);assert.deepEqual(request(replay,identity),args);
 assert.deepEqual(JSON.parse(engine.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],request(replay,identity))),r);
 assert.throws(()=>importRun(JSON.stringify({...doc,provenance:{...identity,wasm_sha256:'0'.repeat(64)}}),identity));
 assert.throws(()=>importRun(JSON.stringify({...doc,request:{...doc.request,args:[...args.slice(0,14),39]}}),identity));
}
const module=readFileSync(join(dir,'timed-laboratory.mjs'),'utf8');assert.ok(module.includes('Measurement comparison is unavailable'));assert.ok(module.includes('Kelvin strain'));assert.ok(module.includes('Physical time (s)'));
console.log(JSON.stringify({ok:true,finitePhysicalScalarComparisons:comparisons,nullRateMaskComparisons:nullMasks,exactReplay:true,model:identity.model},null,2));
