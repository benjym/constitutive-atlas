// Current scoped API parity, additional to every retained legacy request.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,existsSync}from'node:fs';
import {resolve,join}from'node:path';
import {tmpdir}from'node:os';
import {pathToFileURL}from'node:url';
import {spawnSync}from'node:child_process';
import {loadProfileAllocation}from'./laboratory_profile_policy.mjs';
import {runScopedLaboratory}from'../web/laboratory-scope.mjs';
const [native,wasmdir,output,policyFile]=process.argv.slice(2);
assert.ok(native&&wasmdir&&output&&policyFile);assert.ok(!existsSync(output)&&!existsSync(output+'.raw.json'),'Preserve observations');
const catalogue=JSON.parse(readFileSync(resolve(wasmdir,'generated/models.json'),'utf8'));
const allocation=loadProfileAllocation(resolve(policyFile),catalogue);
const report={status:'running',catalogue_hash:catalogue.sha256,cases:[],compared_physical_scalars:0,maximum_budget_fraction:0},journal=[];
const save=()=>{writeFileSync(output,JSON.stringify(report)+'\n');writeFileSync(output+'.raw.json',JSON.stringify(journal)+'\n');};
const temp=mkdtempSync(join(tmpdir(),'atlas-scoped-parity-'));let serial=0;
const module=await(await import(pathToFileURL(resolve(wasmdir,'atlas.js')))).default();
const wasm={ccall:(name,type,types,args)=>{const raw=module.ccall(name,type,types,args);journal.push({role:'wasm',name,args,raw});save();return raw;}};
const nativeEngine={ccall:(name,type,types,args)=>{
 let cli=['--describe'];
 if(name!=='atlas_describe'){
  assert.equal(name,'atlas_run_controls_scope_with_settings');const file=join(temp,String(serial++)+'.csv');writeFileSync(file,args[4]);
  cli=['--response-contract','stress-scope-0.1','--mode','run-controls','--model',args[0],'--parameters',args[1],'--initial',args[2],'--protocol',String(args[3]),'--laboratory-controls-file',file,'--integration-settings',args[5]];
 }
 const p=spawnSync(native,cli,{encoding:'utf8',timeout:30000,maxBuffer:16*1024*1024});
 journal.push({role:'native',name,args,raw:p.stdout,status:p.status,signal:p.signal,stderr:p.stderr,error:p.error?String(p.error):null});save();
 assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');const result=JSON.parse(p.stdout);assert.equal(p.status,name==='atlas_describe'||result.ok?0:1);return p.stdout;
}};
// Only physical response channels have floating tolerance. Everything else is exact.
const physical=new Set(['state','strain','p','q','q_signed','u','error']);
function compare(a,b,path='result',floating=false){
 if(typeof b==='number'){
  assert.ok(Number.isFinite(a)&&Number.isFinite(b),path);
  if(!floating){assert.equal(a,b,path);return;}
  const fraction=Math.abs(a-b)/(allocation.policy.parity_relative_tolerance*Math.max(1,Math.abs(a),Math.abs(b)));
  report.compared_physical_scalars++;report.maximum_budget_fraction=Math.max(report.maximum_budget_fraction,fraction);assert.ok(fraction<=1,path+': budget fraction '+fraction);return;
 }
 if(Array.isArray(b)){assert.ok(Array.isArray(a));assert.equal(a.length,b.length);b.forEach((v,i)=>compare(a[i],v,path+'['+i+']',floating));return;}
 if(b&&typeof b==='object'){
  assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort());for(const k of Object.keys(b))if(k!=='elapsed_ms')compare(a[k],b[k],path+'.'+k,path.match(/\.points\[\d+\]$/)?physical.has(k):floating);return;
 }
 assert.equal(a,b,path);
}
try{
 const total=allocation.cases.find(c=>c.specification.stress_scope==='total');assert.ok(total);const wrong={...structuredClone(total.specification),stress_scope:'effective'},before=journal.length;
 assert.throws(()=>runScopedLaboratory(wasm,wrong,catalogue),/scope\/model mismatch/);assert.equal(journal.length,before);report.wrong_scope_rejected_before_compiled_call=true;save();
 for(const c of allocation.cases){const row={id:c.id,specification:c.specification};report.cases.push(row);save();
  row.native=runScopedLaboratory(nativeEngine,c.specification,catalogue);save();row.wasm=runScopedLaboratory(wasm,c.specification,catalogue);save();
  for(const result of [row.native,row.wasm]){assert.equal(result.ok,c.expected_ok);assert.equal(result.message||'',c.expected_message);assert.equal(result.points.length,c.expected_points);}
  compare(row.native,row.wasm);row.passed=true;save();
 }
 report.status='passed';save();console.log(`Scoped parity passed: ${report.cases.length} cases across ${catalogue.models.length} models, ${report.compared_physical_scalars} physical scalars; exact identity, controls and diagnostics.`);
}catch(error){report.status='failed';report.error=String(error);save();throw error;}
