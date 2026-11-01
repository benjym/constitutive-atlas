import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..');
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8'));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const build=path.join(root,'.local/lade-domain-control-v1/wasm-build');
const {default:create}=await import(pathToFileURL(path.join(build,'lade-domain.mjs')));
const module=await create({wasmBinary:fs.readFileSync(path.join(build,'lade-domain.wasm'))});
const rawdir=path.join(root,'.local/lade-domain-control-v1/wasm-requests');fs.mkdirSync(rawdir,{recursive:true});
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
for(const name of ['native-triaxial-results.json','native-domain-results.json','native-lifecycle-corrected-results.json','native-legacy-results.json','native-supplement-results.json']){
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
      if((r.ok&&de.every(x=>x===0))||(!r.ok&&finite(initial)))if(JSON.stringify(r.state)!==JSON.stringify(initial))shape=false;
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
const report={v3_passed:records.filter(x=>x.model===read('model.json').id||x.study==='supplement-recovery').every(x=>x.passed),historical_legacy_passed:records.filter(x=>x.model&&x.model!==read('model.json').id).every(x=>x.passed),input_report_hashes:inputs,checker_sha256:hash(fs.readFileSync(fileURLToPath(import.meta.url))),supplement_policy_sha256:hash(fs.readFileSync(path.join(here,'SUPPLEMENT_POLICY.json'))),id:'lade1975-left-elastic-wasm-parity-v3',model_sha256:hash(fs.readFileSync(path.join(here,'model.json'))),policy_sha256:hash(fs.readFileSync(path.join(here,'POLICY.json'))),module_sha256:hash(fs.readFileSync(path.join(build,'lade-domain.mjs'))),wasm_sha256:hash(fs.readFileSync(path.join(build,'lade-domain.wasm'))),records,passed:records.every(x=>x.passed),limitations:'Saved literal request API parity and statuses; source-reference and transaction gates are separately checked. Not browser or E5 approval.'};
fs.writeFileSync(path.join(here,'wasm-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,requests:records.length,max_scaled_state_error:Math.max(...records.map(x=>x.max_scaled_state_error)),failures:records.filter(x=>!x.passed)},null,2));process.exitCode=report.passed?0:1;
