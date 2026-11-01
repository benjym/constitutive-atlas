// Parent-owned execution: verifies the exact package before any Wasm instantiation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync,lstatSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),base='material-point-hill/',read=p=>readFileSync(join(dir,p)),json=p=>JSON.parse(read(p)),digest=b=>createHash('sha256').update(b).digest('hex');
const required=['hill-contract.mjs','hill-laboratory.mjs',...['hill.js','hill.wasm','models.json','approval.json','review.json','identity.json','build-receipt.json','references.json','negative-requests.json','POLICY.md','dossier.md','hill-abaqus2025-perfect-be.json','review.html'].map(p=>base+p)].sort();
const manifest=json(base+'package-manifest.json');assert.deepEqual(Object.keys(manifest).sort(),required,'Strict package manifest file set');
assert.deepEqual(readdirSync(join(dir,base)).sort(),[...required.filter(p=>p.startsWith(base)).map(p=>p.slice(base.length)),'package-manifest.json'].sort(),'Unexpected or missing package files');
const verified=new Map();
for(const [p,h]of Object.entries(manifest)){assert.ok(!p.startsWith('/')&&!p.split('/').includes('..')&&/^[0-9a-f]{64}$/.test(h));assert.equal(lstatSync(join(dir,p)).isFile(),true,p);assert.equal(lstatSync(join(dir,p)).isSymbolicLink(),false,p);const bytes=read(p);assert.equal(digest(bytes),h,p);verified.set(p,bytes);}
// Import occurs only after both interface modules and every package asset were verified.
const {MODEL,MODEL_SHA256,SETTINGS,validateIdentity,preset,runPath,replayRequest}=await import(pathToFileURL(join(dir,'hill-contract.mjs')));
const identity=validateIdentity(json(base+'identity.json')),approval=json(base+'approval.json'),review=json(base+'review.json'),catalogue=json(base+'models.json'),receipt=json(base+'build-receipt.json'),frozen=json(base+'references.json'),negative=json(base+'negative-requests.json');
assert.equal(approval.status,'approved');assert.equal(review.status,'accepted');assert.equal(approval.model_id,MODEL);assert.equal(approval.definition.sha256,MODEL_SHA256);assert.equal(review.model.id,MODEL);assert.equal(review.model.sha256,MODEL_SHA256);assert.equal(approval.review.sha256,digest(verified.get(base+'review.json')));assert.deepEqual(review.blocking_findings,[]);
for(const [name,key]of [[MODEL+'.json','model_sha256'],['models.json','catalogue_sha256'],['hill.js','module_sha256'],['hill.wasm','wasm_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256']])assert.equal(digest(verified.get(base+name)),identity[key],name);
assert.equal(catalogue.sha256,identity.catalogue_hash);assert.equal(catalogue.models.length,1);assert.equal(catalogue.models[0].id,MODEL);
const pins=new Map(review.artifacts.map(e=>[e.path,e.sha256]));
for(const name of ['build-receipt.json','references.json','negative-requests.json','POLICY.md'])assert.equal(pins.get('docs/ingestion/hill-abaqus2025/execution-v1/'+name),digest(verified.get(base+name)),name+' reviewed evidence');
for(const [suffix,key]of [['hill.js','module_sha256'],['hill.wasm','wasm_sha256'],['generated/models.json','catalogue_sha256']]){const matched=Object.entries(receipt.artifacts).filter(([p])=>p.endsWith('/'+suffix));assert.equal(matched.length,1);assert.equal(matched[0][1],identity[key]);}
assert.equal(frozen.model,MODEL);assert.equal(frozen.model_sha256,MODEL_SHA256);assert.deepEqual(frozen.settings.split(',').map(Number),SETTINGS);
const controller=verified.get('hill-laboratory.mjs').toString();for(const requiredText of ['Complete state at every accepted row','Experimental overlays unavailable','URL.createObjectURL','wasmBinary:verifiedWasm','instantiateWasm(imports,receive)','setupHillLaboratory','material-point-hill/review.html'])assert.ok(controller.includes(requiredText),requiredText);
const wasmBytes=verified.get(base+'hill.wasm'),wasmModule=await WebAssembly.compile(wasmBytes),create=(await import(pathToFileURL(join(dir,base+'hill.js')))).default;
const engine=await create({wasmBinary:wasmBytes,instantiateWasm(imports,receive){const instance=new WebAssembly.Instance(wasmModule,imports);receive(instance);return instance.exports;}});
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,identity.catalogue_hash);assert.deepEqual(descriptor.models,catalogue.models);
let calls=0,comparisons=0,maxStressError=0,maxGammaError=0;
const call=w=>{calls++;return JSON.parse(engine.ccall(w.function,'string',w.types,w.args));};
const results=new Map();
for(const c of frozen.cases){
 const request={model:MODEL,parameters:c.parameters,initial:c.initial,settings:[...SETTINGS],increments:c.increments};
 const result=await runPath(call,request,identity);assert.equal(result.ok,true,c.id+': '+result.message);assert.equal(result.points.length,c.expected.length+1);
 c.expected.forEach((state,i)=>{assert.equal(state.length,7);for(let j=0;j<7;j++){const actual=result.points[i+1].state[j],error=Math.abs(actual-state[j]);assert.ok(Number.isFinite(actual));assert.ok(error<=(j<6?.01+1e-10*Math.abs(state[j]):1e-9),`${c.id}/${i}/${j}: ${error}`);comparisons++;if(j<6)maxStressError=Math.max(maxStressError,error);else maxGammaError=Math.max(maxGammaError,error);}});
 assert.deepEqual(await runPath(call,replayRequest(result,identity),identity),result,c.id+': exact fresh saved-request replay');results.set(c.id,result);
}
const named=results.get('public-preset');assert.ok(named);assert.deepEqual(named.request,preset(),'Browser preset differs from independently frozen request');
const changed=results.get('coefficient-variant-1.1');assert.ok(changed);assert.notDeepEqual(changed.request.parameters,named.request.parameters);assert.notDeepEqual(changed.points.at(-1).state,named.points.at(-1).state,'Directional coefficients must affect the material response');
const baseline=results.get('elastic-0--1'),raw=(parameters,initial,strain,settings=SETTINGS)=>call({function:'atlas_integrate_with_settings',types:Array(5).fill('string'),args:[MODEL,parameters.join(','),initial.join(','),strain.join(','),settings.join(',')]});
for(const c of negative.cases){const rejected=raw(c.parameters,c.initial,c.strain);assert.equal(rejected.ok,false,c.id);if(Object.hasOwn(rejected,'state'))assert.deepEqual(rejected.state,c.initial,c.id+': full rollback');const recovery=await runPath(call,baseline.request,identity);assert.deepEqual(recovery,baseline,c.id+': same-instance recovery');}
// Prospectively qualified material-level failure, not a changed acceptance tolerance.
const mixed=frozen.cases.find(c=>c.id==='mixed-nonproportional');assert.ok(mixed);const failed=raw(mixed.parameters,mixed.initial,mixed.increments[0],[1e-11,1e-6,1,0,1,0]);assert.equal(failed.ok,false);assert.deepEqual(failed.state,mixed.initial);assert.deepEqual(await runPath(call,preset(),identity),named,'Recovery after failed Newton solve');
const corrupt=structuredClone(named);corrupt.provenance.wasm_sha256='0'.repeat(64);assert.throws(()=>replayRequest(corrupt,identity));
const report={passed:true,calls,cases:frozen.cases.length,stateComparisons:comparisons,maxStressError,maxGammaError,strictPackageManifest:true,reviewedBuildArtifactIdentity:true,independentFrozenReferences:true,exactReplay:true,namedPreset:true,alteredCoefficients:true,negativeCases:negative.cases.length,failedNewtonRollback:true,sameInstanceRecovery:true,corruptReplayRejected:true,identity};
if(process.argv[3])writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
