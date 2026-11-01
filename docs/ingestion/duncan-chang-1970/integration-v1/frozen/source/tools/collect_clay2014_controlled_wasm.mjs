// Opaque common-ABI collection; the frozen Python assessor owns numerical gates.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,appendFileSync,existsSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
assert.equal(process.argv.length,3,'one fresh output receipt path required');
const output=resolve(process.argv[2]),rawPath=output.replace(/\.json$/,'')+'.transport.jsonl';
assert.notEqual(output,rawPath);assert.ok(!existsSync(output)&&!existsSync(rawPath));
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const base='catalogue/investigations/clay2014-controlled-resolution-v1/';
const protocolPath=resolve(root,base+'protocol-reference.json'),freezePath=resolve(root,base+'collection-freeze.json');
const freeze=JSON.parse(readFileSync(freezePath));
for(const [name,pin] of Object.entries(freeze.files))assert.equal(sha(resolve(root,name)),pin,'source freeze: '+name);
const protocol=JSON.parse(readFileSync(protocolPath));
const artifacts={
 'build-wasm/clay2014-paths.js':'0100cc8d8682cef4bda38291361a3bd9bbfd0aaa1ac77de80955ebea42eac92f',
 'build-wasm/clay2014-paths.wasm':'51d95914a56d33302c3d2a32e950079aa713f7d07a9fc1506970d4bcc63dd588'
};
for(const [name,pin] of Object.entries(artifacts))assert.equal(sha(resolve(root,name)),pin,'receipted artifact: '+name);
mkdirSync(dirname(output),{recursive:true});writeFileSync(rawPath,'');
const receipt={version:'clay2014-controlled-resolution-observation-v1',backend:'wasm',
 protocol_sha256:sha(protocolPath),collection_freeze_sha256:sha(freezePath),artifacts,
 completed:false,calls:0,exit_status:null,stderr:'',trailing_stdout:''};
const save=()=>writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');save();
try{
 const module=await(await import(pathToFileURL(resolve(root,'build-wasm/clay2014-paths.js')))).default();
 function call(name,types,args,request){
  let raw;
  try{raw=module.ccall(name,'string',types,args);}
  catch(e){appendFileSync(rawPath,JSON.stringify({backend:'wasm',name,types,args,request,raw:null,exception:String(e)})+'\n');throw e;}
  appendFileSync(rawPath,JSON.stringify({backend:'wasm',name,types,args,request,raw})+'\n');
  assert.equal(typeof raw,'string');return JSON.parse(raw);
 }
 call('atlas_describe',[],[],{mode:'describe'});
 const csv=v=>{assert.ok(v.every(Number.isFinite));return v.map(x=>x.toString()).join(',');};
 for(const group of protocol.groups){
  let parent=structuredClone(protocol.input.initial);
  for(const point of group.points){
   const request={model:protocol.input.model,parameters:structuredClone(protocol.input.parameters),
    initial:structuredClone(parent),strain:structuredClone(point.increment),settings:structuredClone(protocol.policy.settings)};
   const args=[request.model,...['parameters','initial','strain','settings'].map(k=>csv(request[k]))];
   const response=call('atlas_integrate_with_settings',['string','string','string','string','string'],args,request);
   receipt.calls++;save();assert.equal(response.ok,true);
   assert.ok(Array.isArray(response.state)&&response.state.length===7&&response.state.every(Number.isFinite));
   parent=structuredClone(response.state);
  }
 }
 for(const [name,pin] of Object.entries(artifacts))assert.equal(sha(resolve(root,name)),pin);
 for(const [name,pin] of Object.entries(freeze.files))assert.equal(sha(resolve(root,name)),pin);
 assert.equal(receipt.calls,315);receipt.completed=true;receipt.exit_status=0;
}catch(e){receipt.stderr=String(e);receipt.exit_status=1;throw e;}
finally{receipt.transport_sha256=sha(rawPath);save();}
console.log('Retained descriptor and315 Wasm updates; numerical assessment remains separate.');
