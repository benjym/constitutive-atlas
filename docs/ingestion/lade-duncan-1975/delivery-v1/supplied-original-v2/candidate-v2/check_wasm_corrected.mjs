import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../../../..');
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const build=path.join(root,'.local/lade-duncan-candidate-v2/wasm-build');
const {default:create}=await import(pathToFileURL(path.join(build,'lade-gap.mjs')));
const module=await create({wasmBinary:fs.readFileSync(path.join(build,'lade-gap.wasm'))});
const policy=read('wasm-corrected-policy.json'),model=read('model.json'),native=read('native-triaxial-results.json'),life=read('native-lifecycle-corrected-results.json'),refs=read('triaxial-reference-results.json'),tp=read('triaxial-policy.json');
const rawdir=path.join(root,'.local/lade-duncan-candidate-v2/wasm-corrected-requests');fs.mkdirSync(rawdir,{recursive:true});
const records=[];
function run(command){
  const get=(key,fallback='')=>{const i=command.indexOf(key);return i<0?fallback:command[i+1];};
  const args=[model.id,get('--parameters'),get('--initial')];
  if(get('--integration-settings'))return JSON.parse(module.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],[...args,get('--strain'),get('--integration-settings')]));
  if(get('--mode')==='integrate')return JSON.parse(module.ccall('atlas_integrate','string',['string','string','string','string'],[...args,get('--strain')]));
  return JSON.parse(module.ccall('atlas_run_scope_with_settings','string',['string','string','string','number','number','number','number','string'],[...args,Number(get('--protocol','0')),Number(get('--target','0')),Number(get('--steps','1')),Number(get('--cycles','0')),'']));
}
function compare(a,b){let err=0;if(a.length!==b.length)return Infinity;for(let i=0;i<a.length;i++)err=Math.max(err,Math.abs(a[i]-b[i])/policy.state_scales[i]);return err;}
for(const [kind,rows] of [['corrected-lifecycle',life.requests]])for(let i=0;i<rows.length;i++){
  const row=rows[i],n=row.response??JSON.parse(fs.readFileSync(path.join(root,row.raw_path),'utf8')),r=run(row.command);
  const bytes=JSON.stringify(r)+'\n',raw=path.join(rawdir,`${kind}-${i}.json`);fs.writeFileSync(raw,bytes);
  let error=0,shape=true;
  if(n.points){shape=!!r.points&&n.points.length===r.points.length;if(shape)for(let j=0;j<n.points.length;j++)error=Math.max(error,compare(n.points[j].state,r.points[j].state));}
  else if(n.state){shape=!!r.state;if(shape)error=compare(n.state,r.state);}
  const record={kind,index:i,ok:r.ok,native_ok:n.ok,status_match:r.ok===n.ok,shape_match:shape,max_scaled_state_error:error,raw_path:path.relative(root,raw),raw_sha256:hash(bytes)};
  if(kind==='triaxial'&&row.steps===tp.native_refinement_steps.at(-1)&&r.ok){
    const ref=refs.cases.find(x=>x.set===row.set&&x.reference.axial_strain===row.target).reference,z=r.points.at(-1);
    record.source_errors={relative_axial_stress:Math.abs(z.state[0]-ref.axial_stress)/ref.axial_stress,absolute_radial_strain:Math.abs(z.strain[1]-ref.radial_strain),relative_work_using_1Pa_floor:Math.abs(z.state[7]-ref.wp)/Math.max(1,Math.abs(ref.wp))};
    record.within_source_bounds=Object.entries(tp.native_final_reference_bounds).every(([k,v])=>record.source_errors[k]<=v);
  }
  record.passed=record.status_match&&shape&&error<=policy.full_state_max_scaled_error_tolerance&&(record.within_source_bounds??true);records.push(record);
}
const report={id:policy.id,model_sha256:hash(fs.readFileSync(path.join(here,'model.json'))),policy_sha256:hash(fs.readFileSync(path.join(here,'wasm-corrected-policy.json'))),wasm_sha256:hash(fs.readFileSync(path.join(build,'lade-gap.wasm'))),module_sha256:hash(fs.readFileSync(path.join(build,'lade-gap.mjs'))),native_triaxial_report_sha256:hash(fs.readFileSync(path.join(here,'native-triaxial-results.json'))),native_lifecycle_report_sha256:hash(fs.readFileSync(path.join(here,'native-lifecycle-corrected-results.json'))),records,passed:records.every(x=>x.passed),limitations:'Bounded Node Wasm API parity only. Original native lifecycle, original Wasm parity and hydrostatic source-domain failures remain FAIL. No browser, E5 acceptance or public delivery.'};
fs.writeFileSync(path.join(here,'wasm-corrected-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,requests:records.length,max_scaled_state_error:Math.max(...records.map(x=>x.max_scaled_state_error)),failures:records.filter(x=>!x.passed)},null,2));
process.exitCode=report.passed?0:1;
