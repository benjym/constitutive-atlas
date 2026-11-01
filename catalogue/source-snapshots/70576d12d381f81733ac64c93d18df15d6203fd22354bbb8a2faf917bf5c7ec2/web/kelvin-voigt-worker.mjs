// A dedicated worker owns each run; main-view termination preserves latest-request semantics.
import {modelId,modelSha256,request,verifyResult,types} from './kelvin-voigt-contract.mjs';
const sha=async b=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
async function bytes(path,hash){const r=await fetch(path);if(!r.ok)throw Error('Kelvin–Voigt asset unavailable: '+path);const b=await r.arrayBuffer();if(await sha(b)!==hash)throw Error('Kelvin–Voigt asset identity mismatch: '+path);return b;}
self.onmessage=async({data:{id,controls}})=>{
 try{
  const response=await fetch('./engine-kelvin-voigt/identity.json');if(!response.ok)throw Error('Kelvin–Voigt package identity unavailable.');const identity=await response.json(),base='./engine-kelvin-voigt/';
  if(identity.model!==modelId||identity.model_sha256!==modelSha256)throw Error('Unexpected Kelvin–Voigt model identity.');
  await bytes(base+'kv.mjs',identity.module_sha256);const wasmBinary=await bytes(base+'kv.wasm',identity.wasm_sha256);
  const catalogue=JSON.parse(new TextDecoder().decode(await bytes(base+'models.json',identity.catalogue_file_sha256)));
  await bytes(base+modelId+'.json',identity.model_sha256);await bytes(base+'approval.json',identity.approval_sha256);await bytes(base+'review.json',identity.review_sha256);await bytes(base+'review.html',identity.review_html_sha256);
  for(const [path,hash]of Object.entries(identity.component_sha256))await bytes('./'+path,hash);
  const engine=await(await import(base+'kv.mjs')).default({instantiateWasm(imports,receive){WebAssembly.instantiate(wasmBinary,imports).then(({instance})=>receive(instance)).catch(error=>self.postMessage({id,error:error.message}));return {};}});
  const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));if(descriptor.sha256!==identity.catalogue_hash||JSON.stringify(descriptor.models)!==JSON.stringify(catalogue.models))throw Error('Kelvin–Voigt embedded catalogue differs from supplied model.');
  const args=request(controls,identity),result=verifyResult(JSON.parse(engine.ccall('atlas_run_schedule','string',types,args)),identity,controls);
  self.postMessage({id,result,identity,args});
 }catch(error){self.postMessage({id,error:error.message});}
};
