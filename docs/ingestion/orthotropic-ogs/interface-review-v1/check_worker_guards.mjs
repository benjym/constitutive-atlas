// Reviewer-only network mocks: never instantiate, compile or call any Wasm.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {webcrypto} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const site=resolve(process.argv[2]),text=readFileSync(join(site,'orthotropic-laboratory.mjs'),'utf8');
const contract=await import(pathToFileURL(join(site,'orthotropic-contract.mjs')));
const start=text.indexOf('function workerMain(base){'),end=text.indexOf('\nfunction execute(',start);
assert.ok(start>=0&&end>start);
const original=text.slice(start,end),declaration=original.replace("await import(new URL('orthotropic-contract.mjs',base))",'contractFixture');
assert.notEqual(declaration,original);
const manifestPath='material-point-orthotropic/package-manifest.json',manifest=JSON.parse(readFileSync(join(site,manifestPath),'utf8'));
async function attempt({corrupt,omit,manifestReplacement}){
 let response=null,compileCalls=0,fetches=0;
 const self={postMessage:r=>response=r};
 const fetch=async url=>{fetches++;const p=new URL(url).pathname.slice(1);let b;
  if(p===manifestPath)b=Buffer.from(JSON.stringify(manifestReplacement||Object.fromEntries(Object.entries(manifest).filter(([k])=>k!==omit))));
  else {b=Buffer.from(readFileSync(join(site,p)));if(p===corrupt)b[0]^=1;}
  return {ok:true,arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)};
 };
 const webassembly={compile(){compileCalls++;throw Error('Compiled execution prohibited in review');}};
 const worker=new Function('contractFixture','self','fetch','crypto','TextDecoder','URL','Blob','WebAssembly',declaration+';return workerMain;')(contract,self,fetch,webcrypto,TextDecoder,URL,Blob,webassembly);
 worker('https://review.invalid/');await self.onmessage({data:{id:1,input:contract.preset()}});
 assert.equal(compileCalls,0);assert.equal(response.id,1);assert.ok(response.error);return response.error;
}
let corruptions=0,omissions=0;
for(const p of Object.keys(manifest)){
 assert.match(await attempt({corrupt:p}),/Package asset identity mismatch/);corruptions++;
 assert.match(await attempt({omit:p}),/Package manifest missing/);omissions++;
}
for(const p of ['../escape','/absolute','a/./b','a/../b'])assert.match(await attempt({manifestReplacement:{[p]:'1'.repeat(64)}}),/Invalid package asset path/);
console.log(JSON.stringify({passed:true,corrupt_asset_rejections:corruptions,required_asset_omission_rejections:omissions,path_traversal_rejections:4,compiled_calls:0,scope:'Actual worker body with injected real pure contract and mocked network; no material execution'},null,2));
