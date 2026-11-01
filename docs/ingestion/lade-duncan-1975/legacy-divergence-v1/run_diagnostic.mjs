import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {createBoundedModule} from './bounded-worker/runner.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..'),local=path.join(root,'.local/lade-legacy-divergence-v1');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');fs.mkdirSync(local,{recursive:true});
const baseline=JSON.parse(fs.readFileSync(path.join(root,'docs/ingestion/lade-duncan-1975/outer-predictor-v1/native-legacy-results.json'))).requests[44];
const exe=path.join(local,'native-build/atlas_legacy_trace'),args=baseline.command.slice(1),started=performance.now();
const native=spawnSync(exe,args,{encoding:null,timeout:120000,killSignal:'SIGKILL',maxBuffer:67108864});const records=[];
const row={backend:'native',exe_sha256:hash(fs.readFileSync(exe)),args,status:native.status,signal:native.signal,error:native.error?String(native.error):null,elapsed_ms:performance.now()-started};
for(const stream of ['stdout','stderr']){const bytes=native[stream]??Buffer.alloc(0),p=path.join(local,'native.'+stream);fs.writeFileSync(p,bytes);row[stream]={path:path.relative(root,p),sha256:hash(bytes)};}
records.push(row);const save=()=>fs.writeFileSync(path.join(here,'diagnostic-execution.json'),JSON.stringify({records},null,2)+'\n');save();
if(row.error||row.signal||row.status!==0||row.elapsed_ms>=120000)throw Error('Native diagnostic did not complete inside limits');
const module=createBoundedModule(path.join(local,'wasm-build'),path.join(local,'wasm-raw'));
try{module.ccall('atlas_integrate','string',['string','string','string','string'],['lade-duncan-1975-local-eq19-gap-be-v2','101325,58,33,0.39,0.97,0.00068,1.17,1600,0.86,0','60000,60000,60000,0,0,0,6,0','-2,-2,-2,0,0,0']);records.push({backend:'wasm',completed:true,manifest:'.local/lade-legacy-divergence-v1/wasm-raw/manifest.json'});save();}catch(error){records.push({backend:'wasm',completed:false,error:String(error)});save();throw error;}
