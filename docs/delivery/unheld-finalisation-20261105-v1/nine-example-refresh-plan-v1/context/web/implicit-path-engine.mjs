// Verify the served package before invoking the common engine. No constitutive law here.
import {modelId,modelSha256,parseRunJSON,request,verifyResult,types,validateControls,identityCheck,equal,api} from './implicit-path-contract.mjs';
export const components=Object.freeze(['implicit-path-contract.mjs','implicit-path-engine.mjs','implicit-path-runner.mjs','implicit-path-worker.mjs','implicit-path-laboratory.mjs']);
const hashPattern=/^[0-9a-f]{64}$/;

async function importVerified(bytes) {
  const url=URL.createObjectURL(new Blob([bytes],{type:'text/javascript'}));
  try { return (await import(url)).default; } finally { URL.revokeObjectURL(url); }
}
export async function runImplicitPath(controls,{fetchAsset=globalThis.fetch.bind(globalThis),cryptoApi=globalThis.crypto,importModule=importVerified,instantiateBinary=(bytes,imports)=>WebAssembly.instantiate(bytes,imports),base=new URL('./',import.meta.url)}={}) {
  // Input errors are rejected before fetching an engine.
  controls=validateControls(controls);
  const sha=async b=>[...new Uint8Array(await cryptoApi.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
  const fetchBytes=async(path,hash)=>{
    if(!hashPattern.test(hash))throw Error('Missing Implicit-path asset hash: '+path);
    const r=await fetchAsset(new URL(path,base),{cache:'no-store'});if(!r.ok)throw Error('Implicit-path asset unavailable: '+path);
    const bytes=await r.arrayBuffer();if(await sha(bytes)!==hash)throw Error('Implicit-path asset identity mismatch: '+path);return bytes;
  };
  const json=bytes=>parseRunJSON(new TextDecoder().decode(bytes));
  const response=await fetchAsset(new URL('engine-implicit-path/identity.json',base),{cache:'no-store'});
  if(!response.ok)throw Error('Implicit-path package identity unavailable.');
  const identity=parseRunJSON(await response.text());identityCheck(identity);
  if(identity.model!==modelId||identity.model_sha256!==modelSha256||!hashPattern.test(identity.catalogue_hash)||typeof identity.release_revision!=='string'||!identity.release_revision)throw Error('Unexpected Implicit-path model/package identity.');
  if(!identity.component_sha256||Object.keys(identity.component_sha256).length!==components.length||components.some(name=>!Object.hasOwn(identity.component_sha256,name)))throw Error('Incomplete Implicit-path interface identity.');
  const [moduleBytes,wasmBinary,catalogueBytes,definitionBytes,approvalBytes,reviewBytes]=await Promise.all([
    fetchBytes('engine-implicit-path/lade-domain.mjs',identity.module_sha256),fetchBytes('engine-implicit-path/lade-domain.wasm',identity.wasm_sha256),
    fetchBytes('engine-implicit-path/models.json',identity.catalogue_file_sha256),fetchBytes('engine-implicit-path/'+modelId+'.json',identity.model_sha256),
    fetchBytes('engine-implicit-path/approval.json',identity.approval_sha256),fetchBytes('engine-implicit-path/review.json',identity.review_sha256),
    fetchBytes('engine-implicit-path/review.html',identity.review_html_sha256),...components.map(name=>fetchBytes(name,identity.component_sha256[name]))
  ]);
  const catalogue=json(catalogueBytes),definition=json(definitionBytes),approval=json(approvalBytes),review=json(reviewBytes);
  if(definition.id!==modelId||catalogue.sha256!==identity.catalogue_hash||!Array.isArray(catalogue.models)||catalogue.models.length!==4||!equal(catalogue.models.map(m=>m.id),[modelId,'lade-duncan-1975-local-eq19-gap-be-v2','hypoplastic-sand-vw96','linear-elastic'])||!equal(catalogue.models[0],definition))throw Error('Implicit-path definition/catalogue mismatch.');
  if(approval.status!=='approved'||approval.model_id!==modelId||approval.definition?.sha256!==modelSha256||approval.review?.sha256!==identity.review_sha256||review.status!=='accepted'||review.model?.id!==modelId||review.model?.sha256!==modelSha256||approval.definition.path!==review.model.path)throw Error('Implicit-path approval/review binding mismatch.');
  const createAtlas=await importModule(moduleBytes);
  if(typeof createAtlas!=='function')throw Error('Implicit-path engine module has no factory.');
  let rejectInstantiation,instantiationStarted=false,instantiationCompleted=false;
  const failed=new Promise((_,reject)=>{rejectInstantiation=reject;});
  const engine=await Promise.race([Promise.resolve().then(()=>createAtlas({
    instantiateWasm(imports,receive){
      instantiationStarted=true;
      Promise.resolve().then(()=>instantiateBinary(wasmBinary,imports)).then(({instance,module})=>{instantiationCompleted=true;return receive(instance,module);}).catch(rejectInstantiation);
      return {};
    },
    locateFile(){throw Error('Unverified engine file loading is disabled.');}
  })),failed]);
  if(!instantiationStarted||!instantiationCompleted)throw Error('Implicit-path engine did not complete verified Wasm instantiation.');
  const descriptor=parseRunJSON(engine.ccall('atlas_describe','string',[],[]));
  if(descriptor.sha256!==identity.catalogue_hash||!equal(descriptor.models,catalogue.models))throw Error('Implicit-path embedded catalogue differs from supplied model.');
  const args=request(controls,identity),result=verifyResult(parseRunJSON(engine.ccall(api,'string',types,args)),identity,controls);
  return {result,identity,args};
}
