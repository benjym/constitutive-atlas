// Saved-only full replay. No import or invocation of backend/worker/runner.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {fileURLToPath,pathToFileURL} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url)),packet=path.dirname(out),root=path.resolve(packet,'../../../..');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const original=path.join(packet,'check_wasm_bounded.mjs');
const prefix=`
import assert from 'node:assert/strict';
import {encodeArgs} from ${JSON.stringify(pathToFileURL(path.join(packet,'wasm-bounded-v1/transport.mjs')).href)};
const __out=${JSON.stringify(out)},__original=${JSON.stringify(original)};
const __manifestPath=${JSON.stringify(path.join(root,'.local/lade-fused-linear-v1/wasm-bounded-literal/manifest.json'))};
const __saved=JSON.parse(fs.readFileSync(__manifestPath));let __count=0,__writes=0;
const __hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function createBoundedModule(build,rawdir){return {ccall(name,result,types,args){
 const row=__saved.records[__count++];assert(row);assert.equal(row.state,'finished');assert.equal(row.timeout_ms,120000);assert.equal(row.maxBuffer,67108864);assert.equal(row.status,0);assert.equal(row.signal,null);assert.equal(row.error,null);assert(row.elapsed_ms<120000&&row.elapsed_ms>=0);
 const r=row.request;assert.equal(r.name,name);assert.equal(r.result,result);assert.deepEqual(r.types,types);assert.deepEqual(r.encoded_args,encodeArgs(types,args));
 for(const [file,key] of [['lade-domain.mjs','loader'],['lade-domain.wasm','wasm']]){assert.equal(path.join(build,file),r[key]);assert.equal(__hash(fs.readFileSync(r[key])),r[key+'_sha256']);}
 assert.equal(__hash(fs.readFileSync(path.join(${JSON.stringify(packet)},'wasm-bounded-v1/worker.mjs'))),r.worker_sha256);
 for(const kind of ['stdout','stderr'])assert.equal(__hash(fs.readFileSync(row[kind].path)),row[kind].sha256);
 return fs.readFileSync(row.stdout.path,'utf8');
}};}
const __write=fs.writeFileSync,__mkdir=fs.mkdirSync;
fs.writeFileSync=(name,data)=>{assert(fs.existsSync(name),'Replay may only compare existing evidence');assert.equal(Buffer.compare(Buffer.from(data),fs.readFileSync(name)),0,'Saved report/raw differs '+name);__writes++;};
fs.mkdirSync=(name)=>{assert(fs.statSync(name).isDirectory());};
`;
let source=fs.readFileSync(original,'utf8');
source=source.replace("import {createBoundedModule} from './wasm-bounded-v1/runner.mjs';",prefix);
source=source.replace("const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..');",`const here=${JSON.stringify(packet)},root=${JSON.stringify(root)};`);
source=source.replaceAll('fileURLToPath(import.meta.url)','__original');
source+=`
assert.equal(__count,935);assert.equal(__writes,936);assert.equal(report.records.length,979);assert(report.passed&&report.v4_passed&&report.historical_legacy_passed);
const comparisons=report.records.filter(x=>x.max_scaled_state_error!==undefined);
assert.equal(comparisons.length,935);const recovery=report.records.filter(x=>x.study==='supplement-recovery');assert.equal(recovery.length,44);assert(recovery.every(x=>x.passed));
const maxima=Object.fromEntries(['max_scaled_state_error','max_absolute_strain_error','max_absolute_control_error','max_relative_stress_error'].map(key=>[key,Math.max(...comparisons.map(x=>{assert(Number.isFinite(x[key]));return x[key];}))]));
const groups=Object.fromEntries([...new Set(comparisons.map(x=>x.study))].map(study=>[study,comparisons.filter(x=>x.study===study).length]));
const old=report.records.find(x=>x.study==='native-legacy-results.json'&&x.index===44);assert(old.native_ok&&old.wasm_ok&&old.passed);
fs.writeFileSync=__write;fs.mkdirSync=__mkdir;
__write(path.join(__out,'saved-wasm-full-check-results.json'),JSON.stringify({passed:true,scope:'Saved-only checker replay; no backend/worker/runner import or artifact execution',literal_requests:__count,exact_existing_writes_compared:__writes,records:979,recovery_records:44,groups,maxima,old_legacy_case:old,checker_sha256:__hash(fs.readFileSync(__original)),report_sha256:__hash(fs.readFileSync(path.join(here,'wasm-results.json'))),manifest_sha256:__hash(fs.readFileSync(__manifestPath))},null,2)+'\\n');
console.log(JSON.stringify({saved_replay_passed:true,requests:__count,groups,maxima}));
`;
const dest=path.join(out,'saved-wasm-full-replay.mjs');fs.writeFileSync(dest,source);
await import(pathToFileURL(dest));
