// A dedicated worker owns each run; main-view termination preserves latest-request semantics.
import {modelId,modelSha256,request,verifyResult,verifyApproval,types} from './bingham-atlas-contract.mjs';
const sha=async b=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
async function bytes(path,hash){const r=await fetch(path);if(!r.ok)throw Error('Bingham asset unavailable: '+path);const b=await r.arrayBuffer();if(await sha(b)!==hash)throw Error('Bingham asset identity mismatch: '+path);return b;}
self.onmessage=async({data:{id,controls}})=>{
 try{
  const response=await fetch('./engine-bingham/identity.json');if(!response.ok)throw Error('Bingham package identity unavailable.');const identity=await response.json(),base='./engine-bingham/';
  if(identity.model!==modelId||identity.model_sha256!==modelSha256)throw Error('Unexpected Bingham model identity.');
  await bytes(base+'bingham.mjs',identity.module_sha256);const wasmBinary=await bytes(base+'bingham.wasm',identity.wasm_sha256);
  const catalogue=JSON.parse(new TextDecoder().decode(await bytes(base+'models.json',identity.catalogue_file_sha256)));
  const decode=b=>JSON.parse(new TextDecoder().decode(b)),definition=decode(await bytes(base+modelId+'.json',identity.model_sha256)),approval=decode(await bytes(base+'approval.json',identity.approval_sha256)),review=decode(await bytes(base+'review.json',identity.review_sha256));verifyApproval(identity,approval,review,definition);await bytes(base+'review.html',identity.review_html_sha256);const source=decode(await bytes(base+'source-receipts.json',identity.source_receipts_sha256));
  const sourceHashes=source.receipts.filter(x=>x.original&&x.url).map(x=>({url:x.url,sha256:x.sha256}));if(!sourceHashes.length||JSON.stringify(sourceHashes)!==JSON.stringify(identity.source_sha256))throw Error('Source identity list differs from retained receipts.');
  if(!review.artifacts?.some(x=>x.path==='docs/ingestion/bingham-comsol63/source-v1/source-receipts.json'&&x.sha256===identity.source_receipts_sha256))throw Error('Source receipts are not bound to accepted review.');
  for(const [path,hash]of Object.entries(identity.component_sha256))await bytes('./'+path,hash);
  const engine=await(await import(base+'bingham.mjs')).default({instantiateWasm(imports,receive){WebAssembly.instantiate(wasmBinary,imports).then(({instance})=>receive(instance)).catch(error=>self.postMessage({id,error:error.message}));return {};}});
  const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));if(descriptor.sha256!==identity.catalogue_hash||JSON.stringify(descriptor.models)!==JSON.stringify(catalogue.models))throw Error('Bingham embedded catalogue differs from supplied model.');
  const args=request(controls,identity),result=verifyResult(JSON.parse(engine.ccall('atlas_run_schedule','string',types,args)),identity,controls);
  self.postMessage({id,result,identity,args});
 }catch(error){self.postMessage({id,error:error.message});}
};
