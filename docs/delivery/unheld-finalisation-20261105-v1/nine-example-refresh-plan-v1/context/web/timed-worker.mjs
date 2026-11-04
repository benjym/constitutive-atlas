// Dedicated common-engine instance; parent termination gives latest-request semantics.
import {request,verifyResult} from './timed-contract.mjs';
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
async function bytes(url,hash){const r=await fetch(url);if(!r.ok)throw Error('Engine asset unavailable: '+url);const b=await r.arrayBuffer();if(await sha(b)!==hash)throw Error('Engine asset hash mismatch: '+url);return b;}
self.onmessage=async({data:{id,controls}})=>{
 try{
  const res=await fetch('./engine-burgers/identity.json');if(!res.ok)throw Error('Timed package identity unavailable.');const identity=await res.json();
  const base='./engine-burgers/';
  await bytes(base+'burgers.mjs',identity.module_sha256);
  const wasmBinary=await bytes(base+'burgers.wasm',identity.wasm_sha256);
  const catalogue=JSON.parse(new TextDecoder().decode(await bytes(base+'models.json',identity.catalogue_file_sha256)));
  await bytes(base+identity.model+'.json',identity.model_sha256);
  await bytes(base+'approval.json',identity.approval_sha256);await bytes(base+'review.json',identity.review_sha256);
  const engine=await(await import(base+'burgers.mjs')).default({wasmBinary});
  const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));
  if(descriptor.sha256!==identity.catalogue_hash||JSON.stringify(descriptor.models)!==JSON.stringify(catalogue.models))throw Error('Loaded engine metadata mismatch.');
  const args=request(controls,identity),result=verifyResult(JSON.parse(engine.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],args)),identity,controls);
  self.postMessage({id,result,identity,args});
 }catch(e){self.postMessage({id,error:e.message});}
};
