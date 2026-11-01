
import assert from 'node:assert/strict';
import {encodeArgs} from "file:///Users/bmar5496/code/constitutive-atlas/docs/ingestion/lade-duncan-1975/fused-linear-v1/wasm-bounded-v1/transport.mjs";
const __out="/Users/bmar5496/code/constitutive-atlas/docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review",__original="/Users/bmar5496/code/constitutive-atlas/docs/ingestion/lade-duncan-1975/fused-linear-v1/check_wasm_bounded.mjs";
const __manifestPath="/Users/bmar5496/code/constitutive-atlas/.local/lade-fused-linear-v1/wasm-bounded-literal/manifest.json";
const __saved=JSON.parse(fs.readFileSync(__manifestPath));let __count=0,__writes=0;
const __hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function createBoundedModule(build,rawdir){return {ccall(name,result,types,args){
 const row=__saved.records[__count++];assert(row);assert.equal(row.state,'finished');assert.equal(row.timeout_ms,120000);assert.equal(row.maxBuffer,67108864);assert.equal(row.status,0);assert.equal(row.signal,null);assert.equal(row.error,null);assert(row.elapsed_ms<120000&&row.elapsed_ms>=0);
 const r=row.request;assert.equal(r.name,name);assert.equal(r.result,result);assert.deepEqual(r.types,types);assert.deepEqual(r.encoded_args,encodeArgs(types,args));
 for(const [file,key] of [['lade-domain.mjs','loader'],['lade-domain.wasm','wasm']]){assert.equal(path.join(build,file),r[key]);assert.equal(__hash(fs.readFileSync(r[key])),r[key+'_sha256']);}
 assert.equal(__hash(fs.readFileSync(path.join("/Users/bmar5496/code/constitutive-atlas/docs/ingestion/lade-duncan-1975/fused-linear-v1",'wasm-bounded-v1/worker.mjs'))),r.worker_sha256);
 for(const kind of ['stdout','stderr'])assert.equal(__hash(fs.readFileSync(row[kind].path)),row[kind].sha256);
 return fs.readFileSync(row.stdout.path,'utf8');
}};}
const __write=fs.writeFileSync,__mkdir=fs.mkdirSync;
fs.writeFileSync=(name,data)=>{assert(fs.existsSync(name),'Replay may only compare existing evidence');assert.equal(Buffer.compare(Buffer.from(data),fs.readFileSync(name)),0,'Saved report/raw differs '+name);__writes++;};
fs.mkdirSync=(name)=>{assert(fs.statSync(name).isDirectory());};

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here="/Users/bmar5496/code/constitutive-atlas/docs/ingestion/lade-duncan-1975/fused-linear-v1",root="/Users/bmar5496/code/constitutive-atlas";
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8'));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const build=path.join(root,'.local/lade-fused-linear-v1/wasm-build');
const module=createBoundedModule(build,path.join(root,'.local/lade-fused-linear-v1/wasm-bounded-literal'));
const rawdir=path.join(root,'.local/lade-fused-linear-v1/wasm-requests');fs.mkdirSync(rawdir,{recursive:true});
const policy=read('POLICY.json'),records=[],scales=[101325,101325,101325,101325,101325,101325,40,101325];
function run(cmd){
  const get=(key,fallback='')=>{const i=cmd.indexOf(key);return i<0?fallback:cmd[i+1];};
  const a=[get('--model'),get('--parameters'),get('--initial')];
  if(get('--mode')==='integrate'){
    if(get('--integration-settings'))return JSON.parse(module.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],[...a,get('--strain'),get('--integration-settings')]));
    return JSON.parse(module.ccall('atlas_integrate','string',['string','string','string','string'],[...a,get('--strain')]));
  }
  return JSON.parse(module.ccall('atlas_run_scope_with_settings','string',['string','string','string','number','number','number','number','string'],[...a,Number(get('--protocol','0')),Number(get('--target','0')),Number(get('--steps','1')),Number(get('--cycles','0')),get('--integration-settings')]));
}
function finite(a){return Array.isArray(a)&&a.every(x=>typeof x==='number'&&Number.isFinite(x));}
function compare(a,b,unit=false){if(!finite(a)||!finite(b)||a.length!==b.length)return Infinity;return Math.max(0,...a.map((x,i)=>Math.abs(x-b[i])/(unit?1:(scales[i]??101325))));}
function stressBound(s,k1){
 if(!finite(s)||s.length<6)return NaN;
 const scale=Math.max(...s.slice(0,6).map(Math.abs));if(!(scale>0&&Number.isFinite(scale)))return NaN;
 const [x,y,z,aa,bb,cc]=s.slice(0,6).map(x=>x/scale),a=aa/Math.SQRT2,b=bb/Math.SQRT2,c=cc/Math.SQRT2;
 const det=x*y*z+2*a*b*c-x*b*b-y*c*c-z*a*a,T=x+y+z,f=T*T*T/det;
 if(!(x>0&&x*y-a*a>0&&det>0&&Number.isFinite(f)&&f<=k1*(1+1e-10)))return NaN;
 const bound=4*((s[0]+s[1]+s[2])/(k1*(1+1e-10)));return bound>0&&Number.isFinite(bound)?bound:NaN;
}
function relative(a,b,k1){const den=Math.min(stressBound(a,k1),stressBound(b,k1));return den>0?Math.hypot(...a.slice(0,6).map((x,i)=>x-b[i]))/den:Infinity;}
const inputs={};
for(const name of ['native-triaxial-results.json','native-triaxial-fixed-results.json','native-domain-results.json','native-lifecycle-corrected-results.json','native-legacy-results.json','native-supplement-results.json']){
  const native=read(name);inputs[name]=hash(fs.readFileSync(path.join(here,name)));const supplementPairs=[];
  for(let i=0;i<native.requests.length;i++){
    const row=native.requests[i],n=row.response??JSON.parse(fs.readFileSync(path.join(root,row.raw_path),'utf8')),r=run(row.command);
    const raw=path.join(rawdir,`${name.replace('.json','')}-${i}.json`),bytes=JSON.stringify(r)+'\n';fs.writeFileSync(raw,bytes);
    let error=0,shape=true,strainError=0,pressureError=0,controlError=0;
    const isV3=row.command[row.command.indexOf('--model')+1]===read('model.json').id;
    const par=row.command[row.command.indexOf('--parameters')+1].split(',').map(Number);
    const k1=par[Object.keys(read('model.json').parameters).indexOf('k1')];
    const pair=(a,b)=>{error=Math.max(error,compare(a,b));if(isV3){const initial=row.command[row.command.indexOf('--initial')+1].split(',').map(Number);if(Number.isFinite(stressBound(initial,k1)))pressureError=Math.max(pressureError,relative(a,b,k1));else if(n.ok!==false||r.ok!==false||JSON.stringify(a)!==JSON.stringify(initial)||JSON.stringify(b)!==JSON.stringify(initial))pressureError=Infinity;}};
    if(n.points){shape=!!r.points&&r.points.length===n.points.length;if(shape)for(let j=0;j<n.points.length;j++){
      pair(n.points[j].state,r.points[j].state);
      const ac=n.points[j].control,bc=r.points[j].control;controlError=Math.max(controlError,typeof ac==='number'&&typeof bc==='number'&&Number.isFinite(ac)&&Number.isFinite(bc)?Math.abs(ac-bc):Infinity);
      if(n.points[j].strain!==undefined||r.points[j].strain!==undefined)strainError=Math.max(strainError,compare(n.points[j].strain,r.points[j].strain,true));
    }}else {shape=Array.isArray(n.state)===Array.isArray(r.state);if(shape&&n.state)pair(n.state,r.state);}
    if(row.command.includes('--strain')){
      const initial=row.command[row.command.indexOf('--initial')+1].split(',').map(Number),de=row.command[row.command.indexOf('--strain')+1].split(',').map(Number);
      if((r.ok&&de.every(x=>x===0))||(!r.ok&&finite(initial)&&Array.isArray(r.state)))if(JSON.stringify(r.state)!==JSON.stringify(initial))shape=false;
    }
    if(name==='native-supplement-results.json')supplementPairs.push(r);
    const record={study:name,index:i,model:row.command[row.command.indexOf('--model')+1],native_ok:n.ok,wasm_ok:r.ok,status_match:r.ok===n.ok,shape_match:shape,max_scaled_state_error:error,max_absolute_strain_error:strainError,max_absolute_control_error:controlError,max_relative_stress_error:pressureError,raw_path:path.relative(root,raw),raw_sha256:hash(bytes)};
    for(const key of ['integration_settings','loading','response_contract'])if(n[key]!==undefined||r[key]!==undefined)record[key+'_match']=JSON.stringify(n[key])===JSON.stringify(r[key]);
    if(n.stress!==undefined)record.scope_match=JSON.stringify(n.stress)===JSON.stringify(r.stress);
    if(n.catalogue_hash!==undefined)record.catalogue_match=n.catalogue_hash===r.catalogue_hash;
    record.passed=record.status_match&&shape&&error<=1e-8&&strainError<=1e-10&&pressureError<=1e-6&&controlError<=1e-12&&Object.entries(record).filter(([k])=>k.endsWith('_match')).every(([,v])=>v)&&(record.scope_match??true)&&(record.catalogue_match??true);records.push(record);
  }
  if(name==='native-supplement-results.json')for(let j=0;j<supplementPairs.length;j+=2){const a=supplementPairs[j],b=supplementPairs[j+1];records.push({study:'supplement-recovery',index:j,passed:a.ok&&b.ok&&JSON.stringify(a.state)===JSON.stringify(b.state)});}
  console.log(`${name}: ${native.requests.length} requests complete`);
}
const report={v4_passed:records.filter(x=>x.model===read('model.json').id||x.study==='supplement-recovery').every(x=>x.passed),historical_legacy_passed:records.filter(x=>x.model&&x.model!==read('model.json').id).every(x=>x.passed),input_report_hashes:inputs,checker_sha256:hash(fs.readFileSync(__original)),supplement_policy_sha256:hash(fs.readFileSync(path.join(here,'SUPPLEMENT_POLICY.json'))),id:'lade1975-midpoint-elastic-wasm-parity-v4',model_sha256:hash(fs.readFileSync(path.join(here,'model.json'))),policy_sha256:hash(fs.readFileSync(path.join(here,'POLICY.json'))),module_sha256:hash(fs.readFileSync(path.join(build,'lade-domain.mjs'))),wasm_sha256:hash(fs.readFileSync(path.join(build,'lade-domain.wasm'))),records,passed:records.every(x=>x.passed),limitations:'Saved literal request API parity and statuses; source-reference and transaction gates are separately checked. Not browser or E5 approval.'};
fs.writeFileSync(path.join(here,'wasm-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,requests:records.length,max_scaled_state_error:Math.max(...records.map(x=>x.max_scaled_state_error)),failures:records.filter(x=>!x.passed)},null,2));process.exitCode=report.passed?0:1;

assert.equal(__count,935);assert.equal(__writes,936);assert.equal(report.records.length,979);assert(report.passed&&report.v4_passed&&report.historical_legacy_passed);
const comparisons=report.records.filter(x=>x.max_scaled_state_error!==undefined);
assert.equal(comparisons.length,935);const recovery=report.records.filter(x=>x.study==='supplement-recovery');assert.equal(recovery.length,44);assert(recovery.every(x=>x.passed));
const maxima=Object.fromEntries(['max_scaled_state_error','max_absolute_strain_error','max_absolute_control_error','max_relative_stress_error'].map(key=>[key,Math.max(...comparisons.map(x=>{assert(Number.isFinite(x[key]));return x[key];}))]));
const groups=Object.fromEntries([...new Set(comparisons.map(x=>x.study))].map(study=>[study,comparisons.filter(x=>x.study===study).length]));
const old=report.records.find(x=>x.study==='native-legacy-results.json'&&x.index===44);assert(old.native_ok&&old.wasm_ok&&old.passed);
fs.writeFileSync=__write;fs.mkdirSync=__mkdir;
__write(path.join(__out,'saved-wasm-full-check-results.json'),JSON.stringify({passed:true,scope:'Saved-only checker replay; no backend/worker/runner import or artifact execution',literal_requests:__count,exact_existing_writes_compared:__writes,records:979,recovery_records:44,groups,maxima,old_legacy_case:old,checker_sha256:__hash(fs.readFileSync(__original)),report_sha256:__hash(fs.readFileSync(path.join(here,'wasm-results.json'))),manifest_sha256:__hash(fs.readFileSync(__manifestPath))},null,2)+'\n');
console.log(JSON.stringify({saved_replay_passed:true,requests:__count,groups,maxima}));
