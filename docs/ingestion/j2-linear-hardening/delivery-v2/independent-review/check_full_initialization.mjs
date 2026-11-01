// Execute full frozen initialization control flow with inert module/network/compile stubs.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const sourcePath=process.argv[2]||new URL('./source-r2/web/j2-laboratory.mjs',import.meta.url);
const source=readFileSync(sourcePath,'utf8');
const body=source.slice(source.indexOf('async function loadEngine(){'),source.indexOf('\n\n function select(id)')).replaceAll('import.meta.url',"'file:///inert-package/j2-laboratory.mjs'").replace('await import(moduleURL)','({default:stubCreate})');
assert.ok(!body.includes('await import('));
const report=await Function('URL','Blob',`return (async()=>{
 let engine,identity,initialization,active=false,creations=0,descriptorCalls=0;
 const MODEL='j2',MODEL_SHA256='model',validateIdentity=x=>x;
 const expected={catalogue_hash:'catalogue',module_sha256:'js',wasm_sha256:'wasm',model_sha256:'model',catalogue_sha256:'cat',approval_sha256:'approval',review_sha256:'review'};
 const payload={cat:{sha256:'catalogue',models:[{id:'j2'}]},approval:{status:'approved',definition:{sha256:'model'}},review:{status:'accepted',model:{sha256:'model'}}};
 const fetch=async()=>({ok:true,json:async()=>expected});
 const checked=async(url,key)=>new TextEncoder().encode(JSON.stringify(payload[key]||{})).buffer;
 const WebAssembly={compile:async()=>({})};
 const stubCreate=async()=>{const attempt=++creations;return {ccall(){descriptorCalls++;return JSON.stringify({sha256:attempt===1?'wrong':'catalogue',models:[{id:'j2'}]});}};};
 ${body}
 const errors=[];for(let i=0;i<2;i++){try{await ensureEngine();errors.push(null);}catch(error){errors.push({name:error.name,message:error.message});}}
 return {errors,creations,descriptorCalls,enginePublished:!!engine,compiledCalls:0,engineCalls:0};
})();`)(URL,Blob);
if(process.argv[3]==='--expect-valid-retry'){assert.equal(report.errors[0]?.message,'Loaded engine identity mismatch.');assert.equal(report.errors[1],null);assert.equal(report.creations,2);assert.equal(report.descriptorCalls,2);assert.equal(report.enginePublished,true);}
console.log(JSON.stringify({source_sha256:createHash('sha256').update(source).digest('hex'),...report,scope:'Full loadEngine/ensureEngine source retained; inert fetch, checked bytes, module factory and compile stand-ins. No application/compiled engine runs.'},null,2));
