// Execute the packaged common Wasm and compare complete state to frozen source references.
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=read('engine-kelvin-voigt/identity.json'),approval=read('engine-kelvin-voigt/approval.json'),review=read('engine-kelvin-voigt/review.json'),manifest=read('engine-kelvin-voigt/package-manifest.json');
assert.equal(manifest.kind,'kelvin-voigt-general-atlas-laboratory-v1');assert.equal(review.status,'accepted');assert.equal(approval.status,'approved');assert.equal(approval.definition.sha256,identity.model_sha256);assert.equal(review.model.sha256,identity.model_sha256);
for(const [path,expected]of Object.entries(manifest.files))assert.equal(hash(path),expected,path);
for(const [name,key]of [['kv.mjs','module_sha256'],['kv.wasm','wasm_sha256'],['models.json','catalogue_file_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],['review.html','review_html_sha256'],[identity.model+'.json','model_sha256']])assert.equal(hash('engine-kelvin-voigt/'+name),identity[key]);
for(const [path,expected]of Object.entries(identity.component_sha256))assert.equal(hash(path),expected,path);
assert.equal(read('engine-kelvin-voigt/models.json').sha256,identity.catalogue_hash);assert.ok(!existsSync(join(dir,'kelvin-voigt.html')),'Standalone Kelvin–Voigt page must remain absent.');
const ui=readFileSync(join(dir,'kelvin-voigt-laboratory.mjs'),'utf8');assert.ok(ui.includes("document.querySelector('#laboratory > .lab-layout')"));assert.ok(ui.includes('All6state and6stress'));assert.ok(ui.includes('Measurement comparison is unavailable'));assert.ok(!ui.includes('<iframe'));assert.ok(!ui.includes('kelvin-voigt.html'));
const {defaults,request,importRun,verifyResult,verifyReplay,types}=await import(pathToFileURL(join(dir,'kelvin-voigt-contract.mjs')));
const engine=await(await import(pathToFileURL(join(dir,'engine-kelvin-voigt/kv.mjs')))).default({instantiateWasm(imports,receive){WebAssembly.instantiate(readFileSync(join(dir,'engine-kelvin-voigt/kv.wasm')),imports).then(({instance})=>receive(instance));return {};}});
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,read('engine-kelvin-voigt/models.json').models);
// Independent closed-form references, frozen before any packaged execution.
// These equations are a test oracle only, never a constitutive implementation.
const dev=v=>{const m=(v[0]+v[1]+v[2])/3;return v.map((x,i)=>x-(i<3?m:0));};
function expected(c,p){
 const [K,G,tau]=c.parameters,t=p.time-c.start,initial=c.initial,d0=dev(c.initialRates),e0=dev(initial),mean=(initial[0]+initial[1]+initial[2])/3;
 let strain,rate;
 if(p.segment===-1){strain=initial;rate=c.initialRates;}
 else if(c.mode==='hold'){strain=initial;rate=Array(6).fill(0);}
 else if(c.mode==='rate'){strain=initial.map((v,i)=>v+t*c.rates[i]);rate=c.rates;}
 else {strain=e0.map((v,i)=>v+tau*d0[i]*(1-Math.exp(-t/tau))+(i<3?mean:0));rate=d0.map(v=>v*Math.exp(-t/tau));}
 const e=dev(strain),d=dev(rate),trace=strain[0]+strain[1]+strain[2];
 return {state:strain,stress:e.map((v,i)=>2*G*v+2*G*tau*d[i]+(i<3?K*trace:0))};
}
const call=args=>JSON.parse(engine.ccall('atlas_run_schedule','string',types,args));let comparisons=0,nullRateMasks=0;
for(const mode of ['creep','rate','hold']){
 const c={...structuredClone(defaults),mode},args=request(c,identity),result=verifyResult(call(args),identity,c);
 for(const point of result.points){const reference=expected(c,point);
  for(let i=0;i<6;i++){assert.ok(Math.abs(point.state[i]-reference.state[i])<=3e-8,`${mode} state ${point.time}/${i}`);comparisons++;assert.ok(Math.abs(point.observables[i]-reference.stress[i])<=1,`${mode} stress ${point.time}/${i}`);comparisons++;}
  nullRateMasks+=point.strain_rate.filter(x=>x===null).length;
 }
 const doc={kind:'atlas-kelvin-voigt-laboratory-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args},result},replay=importRun(JSON.stringify(doc),identity);verifyReplay(call(request(replay,identity)),result);
 const tampered=structuredClone(doc);tampered.result.points[2].state[3]+=.01;tampered.result.points[2].strain[3]+=.01;tampered.result.points[2].observables[3]+=100;const changed=importRun(JSON.stringify(tampered),identity,{withResult:true});assert.throws(()=>verifyReplay(result,changed.result));
 assert.throws(()=>importRun(JSON.stringify({...doc,provenance:{...identity,wasm_sha256:'0'.repeat(64)}}),identity));
 if(mode==='hold'){const bad=[...args];bad[5]=args[5].replace(/^8,/, '-1,');assert.equal(call(bad).ok,false);assert.deepEqual(call(args),result,'Persistent module recovery after failed request');}
}
console.log(JSON.stringify({ok:true,model:identity.model,fullStateStressComparisons:comparisons,nullRateMaskEntries:nullRateMasks,exactReplay:true,failedRequestRecovery:true,allPackageAssetsGuarded:Object.keys(manifest.files).length,standalonePageAbsent:true},null,2));
