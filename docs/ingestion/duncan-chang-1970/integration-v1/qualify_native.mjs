import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,mkdtempSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {createLoading} from '../../../../web/loading.mjs';
import {runScopedLaboratory} from '../../../../web/laboratory-scope.mjs';
const [binary,out]=process.argv.slice(2);assert.ok(!existsSync(out));
const here=resolve('docs/ingestion/duncan-chang-1970/integration-v1');
const catalogue=JSON.parse(readFileSync(join(here,'frozen/generated/models.json')));
const policy=JSON.parse(readFileSync('catalogue/laboratory-package-policy.json'));
const report={status:'running',catalogue_hash:catalogue.sha256,ordinary:[],presets:[],calls:[]};
const save=()=>writeFileSync(out,JSON.stringify(report)+'\n');
const temp=mkdtempSync(join(tmpdir(),'duncan-integration-native-'));let serial=0;
function call(cli){const p=spawnSync(binary,cli,{encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024});report.calls.push({cli,status:p.status,stderr:p.stderr,raw:p.stdout});save();assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');const r=JSON.parse(p.stdout);assert.equal(p.status,r.ok===false?1:0);return r;}
const engine={ccall(name,type,types,args){
 if(name==='atlas_describe')return JSON.stringify(call(['--describe']));
 const cli=['--response-contract','stress-scope-0.1','--model',args[0],'--parameters',args[1],'--initial',args[2],'--protocol',String(args[3])];
 if(name==='atlas_run_controls_scope_with_settings'){const f=join(temp,String(serial++)+'.csv');writeFileSync(f,args[4]);cli.push('--mode','run-controls','--laboratory-controls-file',f,'--integration-settings',args[5]);}
 else{assert.equal(name,'atlas_run_scope_with_settings');cli.push('--mode','run','--target',String(args[4]),'--steps',String(args[5]),'--cycles',String(args[6]),'--integration-settings',args[7]);}
 return JSON.stringify(call(cli));
}};
try{
 assert.deepEqual(call(['--describe']),catalogue);
 const settings={version:'incremental-settings-0.1',norm:'scaled_component_max',residual_tolerance:2e-10,rate_tolerance:1e-6,max_iterations:45,max_depth:14,max_substeps:20000,max_backtracks:11};
 for(const model of catalogue.models){
  const s={response_contract:'stress-scope-0.1',stress_scope:model.formulation?.stress.scope??'effective',model:model.id,parameters:Object.values(model.parameters).map(p=>p.default),initial:model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol:1,target:.01,steps:100,cycles:0,integration_settings:settings};s.loading=createLoading(s);
  const result=runScopedLaboratory(engine,s,catalogue);report.ordinary.push({id:model.id,specification:s,result});save();
  const declared=policy.declared_failures.find(e=>e.model===model.id);assert.equal(result.ok,!declared);assert.equal(result.points.length,declared?declared.committed_points:101);if(declared)assert.equal(result.message,declared.message);
 }
 const e4=JSON.parse(readFileSync('docs/ingestion/duncan-chang-1970/material-v1/execution-v2/native-results.json'));
 const model=catalogue.models.find(m=>m.id==='duncan-chang-1970-endpoint-average');
 for(const p of JSON.parse(readFileSync(join(here,'preset-inputs.json')))){
  const s={response_contract:'stress-scope-0.1',stress_scope:'effective',model:model.id,parameters:Object.keys(model.parameters).map(k=>p.parameters[k]),initial:p.initial,protocol:p.protocol,target:p.target,steps:p.steps,cycles:p.cycles,integration_settings:settings};
  const result=runScopedLaboratory(engine,s,catalogue);report.presets.push({id:p.id,specification:s,result});save();assert.equal(result.ok,true);
  const old=e4.presets.find(x=>x.id===p.id).call.response;
  assert.ok(old,'Saved E4 parsed result required');
  assert.equal(result.points.length,old.points.length);
  for(let i=0;i<old.points.length;i++)for(const k of ['state','strain','control','p','q','q_signed','error'])assert.deepEqual(result.points[i][k],old.points[i][k],p.id+'/'+i+'/'+k);
 }
 report.status='passed';save();console.log('14 ordinary native cases and 2 exact E4 source preset histories passed.');
}catch(e){report.status='failed';report.error=String(e);save();throw e;}
