// Independent pure transport fixture. No module code or WebAssembly is executed.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {webcrypto,createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
import * as c from '../../../../../web/implicit-path-contract.mjs';
import {runImplicitPath,components} from '../../../../../web/implicit-path-engine.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../../..');
const read=p=>c.parseRunJSON(fs.readFileSync(path.join(root,p),'utf8'));
const report=read('docs/ingestion/lade-duncan-1975/outer-predictor-v1/native-triaxial-fixed-results.json');
const row=report.requests.find(x=>x.set==='dense'&&x.target===.005&&x.steps===400),result=read(row.raw_path),input=c.preset();
const catalogue=read('docs/ingestion/lade-duncan-1975/atlas-integration-v1/generated/models.json');
const sha=b=>createHash('sha256').update(b instanceof ArrayBuffer?new Uint8Array(b):b).digest('hex'),enc=v=>Buffer.from(c.stringifyRun(v));
const assets=new Map(),identity={profile:'implicit-path-v1',model:c.modelId,model_sha256:c.modelSha256,public_models:[c.modelId],catalogue_hash:catalogue.sha256,release_revision:'mock-no-qualification',component_sha256:{}};
function asset(name,bytes,key){assets.set(name,bytes);if(key)identity[key]=sha(bytes);}
asset('engine-implicit-path/lade-domain.mjs',Buffer.from('mock factory, never executed'),'module_sha256');
asset('engine-implicit-path/lade-domain.wasm',Buffer.from('mock binary, never instantiated'),'wasm_sha256');
asset('engine-implicit-path/models.json',enc(catalogue),'catalogue_file_sha256');
asset('engine-implicit-path/'+c.modelId+'.json',fs.readFileSync(path.join(root,'models/research/implicit-path/'+c.modelId+'.json')));
asset('engine-implicit-path/review.json',enc({status:'accepted',model:{id:c.modelId,path:'mock',sha256:c.modelSha256}}),'review_sha256');
asset('engine-implicit-path/approval.json',enc({status:'approved',model_id:c.modelId,definition:{path:'mock',sha256:c.modelSha256},review:{sha256:identity.review_sha256}}),'approval_sha256');
asset('engine-implicit-path/review.html',Buffer.from('mock readable review'),'review_html_sha256');
for(const name of components){asset(name,fs.readFileSync(path.join(root,'web',name)));identity.component_sha256[name]=sha(assets.get(name));}
let imported=0,instantiated=0,called=0;
function options({corrupt=null,missing=null,mutate=null,describe=catalogue,instantiateError=false}={}){
 const id=structuredClone(identity);mutate?.(id);
 return {base:new URL('https://fixture.invalid/atlas/'),cryptoApi:webcrypto,fetchAsset:async url=>{const name=url.pathname.slice('/atlas/'.length),b=name==='engine-implicit-path/identity.json'?enc(id):assets.get(name);return {ok:!!b&&name!==missing,text:async()=>b.toString(),arrayBuffer:async()=>Uint8Array.from(name===corrupt?Buffer.from('corrupt'):b).buffer};},
 importModule:async bytes=>{imported++;assert.equal(sha(bytes),identity.module_sha256);return opts=>new Promise(resolve=>opts.instantiateWasm({},()=>resolve({ccall(name,type,types,args){called++;if(name==='atlas_describe')return c.stringifyRun(describe);assert.equal(name,c.api);assert(c.equal(args,c.request(input,identity)));return c.stringifyRun(result);}})));},
 instantiateBinary:async bytes=>{instantiated++;assert.equal(sha(bytes),identity.wasm_sha256);if(instantiateError)throw Error('fixture instantiation rejected');return {instance:{},module:{}};}};
}
const checks=[];async function test(name,fn){try{await fn();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,error:String(error)});}}
await test('all verified bytes reach injected transport and saved result',async()=>{const out=await runImplicitPath(input,options());assert(c.equal(out.result,result));assert.equal(imported,1);assert.equal(instantiated,1);assert.equal(called,2);});
for(const name of assets.keys())await test('reject changed fetched '+name,async()=>{const before=called;await assert.rejects(runImplicitPath(input,options({corrupt:name})),/identity mismatch/);assert.equal(called,before);});
await test('reject missing loader before material call',async()=>assert.rejects(runImplicitPath(input,options({missing:'engine-implicit-path/lade-domain.mjs'})),/unavailable/));
await test('reject witness model identity',async()=>assert.rejects(runImplicitPath(input,options({mutate:id=>id.model='linear-elastic'})),/identity/));
await test('reject public witness allowlist',async()=>assert.rejects(runImplicitPath(input,options({mutate:id=>id.public_models.push('linear-elastic')})),/identity/));
await test('reject embedded catalogue mismatch before run',async()=>assert.rejects(runImplicitPath(input,options({describe:{...catalogue,sha256:'0'.repeat(64)}})),/embedded catalogue/));
await test('instantiation rejection propagates',async()=>assert.rejects(runImplicitPath(input,options({instantiateError:true})),/fixture instantiation rejected/));
const output={scope:'independent mocked transport only; no executable module/Wasm/material/browser calls',passed:checks.every(x=>x.passed),checks};fs.writeFileSync(path.join(here,'fetched-assets-results.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));process.exitCode=output.passed?0:1;
