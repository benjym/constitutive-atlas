// Verify the served package before invoking the common engine. No constitutive law here.
import {modelId,modelSha256,parseRunJSON,request,verifyResult,types,validateControls} from './maxwell-atlas-contract.mjs';
export const components=Object.freeze(['maxwell-atlas-contract.mjs','maxwell-atlas-engine.mjs','maxwell-atlas-runner.mjs','maxwell-atlas-worker.mjs','maxwell-laboratory.mjs','laboratory-controller-router.mjs']);
const hashPattern=/^[0-9a-f]{64}$/;
const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
const equal=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b));
async function importVerified(bytes) {
  const url=URL.createObjectURL(new Blob([bytes],{type:'text/javascript'}));
  try { return (await import(url)).default; } finally { URL.revokeObjectURL(url); }
}
export async function runMaxwellSchedule(controls,{fetchAsset=globalThis.fetch.bind(globalThis),cryptoApi=globalThis.crypto,importModule=importVerified,instantiateBinary=(bytes,imports)=>WebAssembly.instantiate(bytes,imports),base=new URL('./',import.meta.url)}={}) {
  // Input errors are rejected before fetching an engine.
  controls=validateControls(controls);
  const sha=async b=>[...new Uint8Array(await cryptoApi.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
  const fetchBytes=async(path,hash)=>{
    if(!hashPattern.test(hash))throw Error('Missing Maxwell asset hash: '+path);
    const r=await fetchAsset(new URL(path,base),{cache:'no-store'});if(!r.ok)throw Error('Maxwell asset unavailable: '+path);
    const bytes=await r.arrayBuffer();if(await sha(bytes)!==hash)throw Error('Maxwell asset identity mismatch: '+path);return bytes;
  };
  const json=bytes=>parseRunJSON(new TextDecoder().decode(bytes));
  const response=await fetchAsset(new URL('engine-maxwell/identity.json',base),{cache:'no-store'});
  if(!response.ok)throw Error('Maxwell package identity unavailable.');
  const identity=parseRunJSON(await response.text());
  if(identity.model!==modelId||identity.model_sha256!==modelSha256||!hashPattern.test(identity.catalogue_hash)||typeof identity.release_revision!=='string'||!identity.release_revision)throw Error('Unexpected Maxwell model/package identity.');
  if(!identity.component_sha256||Object.keys(identity.component_sha256).length!==components.length||components.some(name=>!Object.hasOwn(identity.component_sha256,name)))throw Error('Incomplete Maxwell interface identity.');
  const [moduleBytes,wasmBinary,catalogueBytes,definitionBytes,approvalBytes,reviewBytes]=await Promise.all([
    fetchBytes('engine-maxwell/maxwell.mjs',identity.module_sha256),fetchBytes('engine-maxwell/maxwell.wasm',identity.wasm_sha256),
    fetchBytes('engine-maxwell/models.json',identity.catalogue_file_sha256),fetchBytes('engine-maxwell/'+modelId+'.json',identity.model_sha256),
    fetchBytes('engine-maxwell/approval.json',identity.approval_sha256),fetchBytes('engine-maxwell/review.json',identity.review_sha256),
    fetchBytes('engine-maxwell/review.html',identity.review_html_sha256),...components.map(name=>fetchBytes(name,identity.component_sha256[name]))
  ]);
  const catalogue=json(catalogueBytes),definition=json(definitionBytes),approval=json(approvalBytes),review=json(reviewBytes);
  if(definition.id!==modelId||catalogue.sha256!==identity.catalogue_hash||!Array.isArray(catalogue.models)||catalogue.models.length!==1||!equal(catalogue.models,[definition]))throw Error('Maxwell definition/catalogue mismatch.');
  if(approval.status!=='approved'||approval.model_id!==modelId||approval.definition?.sha256!==modelSha256||approval.review?.sha256!==identity.review_sha256||review.status!=='accepted'||review.model?.id!==modelId||review.model?.sha256!==modelSha256||approval.definition.path!==review.model.path)throw Error('Maxwell approval/review binding mismatch.');
  const createAtlas=await importModule(moduleBytes);
  if(typeof createAtlas!=='function')throw Error('Maxwell engine module has no factory.');
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
  if(!instantiationStarted||!instantiationCompleted)throw Error('Maxwell engine did not complete verified Wasm instantiation.');
  const descriptor=parseRunJSON(engine.ccall('atlas_describe','string',[],[]));
  if(descriptor.sha256!==identity.catalogue_hash||!equal(descriptor.models,catalogue.models))throw Error('Maxwell embedded catalogue differs from supplied model.');
  const args=request(controls,identity),result=verifyResult(parseRunJSON(engine.ccall('atlas_run_schedule','string',types,args)),identity,controls);
  return {result,identity,args};
}
