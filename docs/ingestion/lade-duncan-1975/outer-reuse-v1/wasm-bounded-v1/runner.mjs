import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {encodeArgs} from './transport.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
export function boundedCall(worker,request,{timeout=120000,maxBuffer=67108864}={}){
 const start=performance.now();const p=spawnSync(process.execPath,[worker],{input:JSON.stringify(request),encoding:null,timeout,killSignal:'SIGKILL',maxBuffer});
 return {stdout:p.stdout??Buffer.alloc(0),stderr:p.stderr??Buffer.alloc(0),status:p.status,signal:p.signal,error:p.error?{code:p.error.code,message:p.error.message}:null,elapsed_ms:performance.now()-start};
}
export function createBoundedModule(build,rawdir){
 fs.mkdirSync(rawdir,{recursive:true});const loader=path.join(build,'lade-domain.mjs'),wasm=path.join(build,'lade-domain.wasm'),worker=path.join(here,'worker.mjs');
 const identities={loader,wasm,loader_sha256:hash(fs.readFileSync(loader)),wasm_sha256:hash(fs.readFileSync(wasm)),worker_sha256:hash(fs.readFileSync(worker))};const records=[];
 return {ccall(name,result,types,args){
  const request={...identities,name,result,types,encoded_args:encodeArgs(types,args)};const index=records.length;const record={request,timeout_ms:120000,maxBuffer:67108864,state:'running'};records.push(record);const save=()=>fs.writeFileSync(path.join(rawdir,'manifest.json'),JSON.stringify({records},null,2)+'\n');save();const r=boundedCall(worker,request);const streams={};
  for(const kind of ['stdout','stderr']){const dest=path.join(rawdir,`${index}.${kind}`);fs.writeFileSync(dest,r[kind]);streams[kind]={path:dest,sha256:hash(r[kind])};}
  Object.assign(record,{state:'finished',status:r.status,signal:r.signal,error:r.error,elapsed_ms:r.elapsed_ms,...streams});save();
  if(r.error||r.signal||r.status!==0)throw Error(`Wasm material request ${index} failed: ${JSON.stringify({status:r.status,signal:r.signal,error:r.error})}`);
  const output=r.stdout.toString('utf8');JSON.parse(output);return output;
 }};
}
