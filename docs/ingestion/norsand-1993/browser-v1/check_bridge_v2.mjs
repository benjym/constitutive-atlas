// Prospective source-reference and transaction qualification of the generic bridge.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createPathEngine} from './proposed/path-engine.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const freeze=read(path.join(here,'bridge-freeze-v2.json'));
for(const [p,hash]of Object.entries(freeze.files))assert.equal(sha(path.join(root,p)),hash,`Changed frozen input ${p}`);
const parent=path.join(here,'../e2-v3'),moduleFile=path.join(parent,'wasm-v2/atlas_path_capability.mjs'),wasmFile=path.join(parent,'wasm-v2/atlas_path_capability.wasm');
const module=await(await import(pathToFileURL(moduleFile))).default({wasmBinary:fs.readFileSync(wasmFile)});
const catalogue=read(path.join(here,'../shared-integration-v1/generated/path_catalogue.json'));
const engine=createPathEngine(module,catalogue),descriptor=catalogue.models[0];
const requests=read(path.join(parent,'backend-requests-v2.json')).requests,references=read(path.join(parent,'references-v2.json')).cases;
const sourceErrors=[],backendErrors=[],volumeErrors=[],checks=[];
const flat=(object,fields)=>fields.flatMap(f=>f.size===1?[object[f.name]]:object[f.name]);
for(const reference of references){
 const req=requests.find(r=>r.id===reference.id);
 const context={state:Object.fromEntries(descriptor.state.map((f,i)=>[f.name,req.state[i]])),coordinate:req.coordinate,controls:Object.fromEntries(descriptor.controls.map((n,i)=>[n,req.current_controls[i]])),parameters:Object.fromEntries(descriptor.parameters.map((n,i)=>[n,req.parameters[i]]))};
 const request={context,progress:req.progress,controls_end:Object.fromEntries(descriptor.controls.map((n,i)=>[n,req.end_controls[i]])),samples:1,settings:req.settings};
 const original=JSON.stringify(request),single=engine.run(descriptor.id,request),endpoint=single.points.at(-1);
 assert.equal(JSON.stringify(request),original,'caller request mutated');
 const actual=[...flat(endpoint.context.state,descriptor.state),...flat(endpoint.observables,descriptor.observables)],expected=[...req.expected_state,...req.expected_observables],scales=[1,1,1,1,...req.observable_scales];
 backendErrors.push(Math.max(...actual.map((v,i)=>Math.abs(v-expected[i])/scales[i])));
 assert(backendErrors.at(-1)<=2e-11);
 for(const samples of [1,40]){
  const result=samples===1?single:engine.run(descriptor.id,{...request,samples}),end=result.points.at(-1),outputs=reference.reference.outputs;
  const source=[...descriptor.state.flatMap(f=>[Number(outputs[f.name])]),...descriptor.observables.flatMap(f=>f.size===1?[Number(outputs[f.name])]:outputs[f.name].map(Number))];
  const values=[...flat(end.context.state,descriptor.state),...flat(end.observables,descriptor.observables)];
  sourceErrors.push(Math.max(...values.map((v,i)=>Math.abs(v-source[i])/scales[i])));assert(sourceErrors.at(-1)<=2e-6);
  for(const point of result.points){
   const z=point.context.state;volumeErrors.push(Math.abs((1+z.e)*Math.exp(z.ev)/(1+context.state.e)-1));
   assert(volumeErrors.at(-1)<=2e-8);assert(Math.abs((z.eq-point.context.coordinate)-(context.state.eq-context.coordinate))<2e-12);
  }
  assert.deepEqual(engine.run(descriptor.id,{...request,samples}),result,'replay differs');
 }
 const bad=structuredClone(request);bad.controls_end.pressure_control=0;bad.samples=40;const badBefore=JSON.stringify(bad),calls=[];
 const traced=new Proxy(module,{get(target,key){if(key==='_path_advance')return(...args)=>{const status=target._path_advance(...args);calls.push({progress:args[8],status});return status;};return Reflect.get(target,key);}});
 assert.throws(()=>createPathEngine(traced,catalogue).run(descriptor.id,bad));
 assert(calls.some(c=>c.progress>0&&c.status===1),'late failure must follow accepted positive intervals');
 assert.equal(JSON.stringify(bad),badBefore,'failed request mutated');assert.equal(JSON.stringify(request),original);
 assert.deepEqual(engine.run(descriptor.id,request),single,'recovery differs');
 const exhausted=structuredClone(request);exhausted.settings[5]=1;
 assert.throws(()=>engine.run(descriptor.id,exhausted));assert.deepEqual(engine.run(descriptor.id,request),single);
 const zero=engine.run(descriptor.id,{...request,progress:0,controls_end:context.controls});assert.deepEqual(zero.points.at(-1).context,context);
 checks.push(reference.id);
}
const first=requests[0],d=catalogue.models[0],base={context:{state:Object.fromEntries(d.state.map((f,i)=>[f.name,first.state[i]])),coordinate:first.coordinate,controls:Object.fromEntries(d.controls.map((n,i)=>[n,first.current_controls[i]])),parameters:Object.fromEntries(d.parameters.map((n,i)=>[n,first.parameters[i]]))},progress:first.progress,controls_end:Object.fromEntries(d.controls.map((n,i)=>[n,first.end_controls[i]])),samples:1,settings:first.settings};
for(const mutate of [r=>r.context.coordinate=NaN,r=>r.progress=-1,r=>r.samples=0,r=>r.context.parameters.M=Infinity,r=>delete r.context.controls.pressure_control,r=>r.context.state.extra=0,r=>r.settings[4]=1.5,r=>{r.progress=0;r.controls_end.pressure_control+=1;}]){
 const request=structuredClone(base);mutate(request);assert.throws(()=>engine.run(d.id,request));
}
const output={scope:'generic bridge only; actual main-atlas/browser/package still pending',cases:checks,sampled_histories:18,validation_negatives:8,max_source_error:Math.max(...sourceErrors),max_backend_error:Math.max(...backendErrors),max_volume_error:Math.max(...volumeErrors),freeze_sha256:sha(path.join(here,'bridge-freeze-v2.json'))};
fs.writeFileSync(path.join(here,'bridge-results-v2.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output));
