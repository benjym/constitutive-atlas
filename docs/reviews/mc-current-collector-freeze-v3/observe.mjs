
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createLaboratoryDocument,parseLaboratoryDocument} from '../../../web/laboratory-document.mjs';
import {runScopedLaboratory} from '../../../web/laboratory-scope.mjs';
const [role,build,outdir]=process.argv.slice(2);assert.ok(['native','wasm','synthetic'].includes(role));
const read=n=>JSON.parse(readFileSync(new URL(n,import.meta.url),'utf8'));
const requests=read('./requests.json'),inputs=read('./source-input.json'),catalogue=read('./generated/models.json'),invalid=read('./rejection-requests.json');
const file=n=>resolve(outdir,n);for(const n of ['journal.json','calls.json','replays.json','rejections.json'])assert.ok(!existsSync(file(n)));
const tmp=mkdtempSync('/private/tmp/atlas-mc-current-wire-');let serial=0,lastRaw;
const module=role!=='native'?await(await import(pathToFileURL(resolve(build,'atlas.js')))).default():null;
const calls=[];
function call(name,args){
 let raw,processResult;
 if(role!=='native')raw=module.ccall(name,'string',args.map(x=>typeof x==='number'?'number':'string'),args);
 else{
  let cli;
  if(name==='atlas_describe')cli=['--describe'];
  else{
   const [model,parameters,initial,protocol]=args;cli=['--response-contract','stress-scope-0.1','--mode',name==='atlas_run_controls_scope_with_settings'?'run-controls':'run','--model',model,'--parameters',parameters,'--initial',initial,'--protocol',String(protocol)];
   if(name==='atlas_run_controls_scope_with_settings'){const wire=resolve(tmp,`${serial++}.csv`);writeFileSync(wire,args[4]);cli.push('--laboratory-controls-file',wire,'--integration-settings',args[5]);}
   else{assert.equal(name,'atlas_run_scope_with_settings');cli.push('--target',String(args[4]),'--steps',String(args[5]),'--cycles',String(args[6]),'--integration-settings',args[7]);}
  }
  const p=spawnSync(resolve(build,'atlas_solver'),cli,{encoding:'utf8',timeout:30000});raw=p.stdout;processResult={status:p.status,signal:p.signal,stderr:p.stderr,error:p.error?String(p.error):null};
 }
 calls.push({name,args,raw,...(processResult?{process:processResult}:{})});writeFileSync(file('calls.json'),JSON.stringify(calls,null,2)+'\n');lastRaw=raw;
 if(processResult)assert.ok([0,1].includes(processResult.status),JSON.stringify(processResult));
 return raw;
}
const engine={ccall:(name,type,types,args)=>call(name,args)},physical=r=>{const {elapsed_ms,...rest}=r;return rest;};
const specifications=read('./contracts.json');
const spec=req=>specifications.find(x=>x.id===req.id).specification;
const rows=[{id:'describe',raw:call('atlas_describe',[])}],replays=[];
writeFileSync(file('journal.json'),JSON.stringify(rows,null,2)+'\n');
for(const req of requests){
 const s=spec(req),result=runScopedLaboratory(engine,s,catalogue);rows.push({id:req.id,request:req,raw:lastRaw});writeFileSync(file('journal.json'),JSON.stringify(rows,null,2)+'\n');assert.equal(result.ok,true,result.message);
 const exported=JSON.parse(JSON.stringify(createLaboratoryDocument(s,result,catalogue))),imported=parseLaboratoryDocument(JSON.stringify(exported),catalogue);
 const record={id:req.id,specification:s,exported,imported};replays.push(record);writeFileSync(file('replays.json'),JSON.stringify(replays,null,2)+'\n');
 assert.deepEqual(imported,s);assert.deepEqual(imported.loading.controls_bits,inputs.paths.find(p=>p.id===req.id).controls_bits);
 const replay=runScopedLaboratory(engine,imported,catalogue);record.raw=lastRaw;writeFileSync(file('replays.json'),JSON.stringify(replays,null,2)+'\n');assert.deepEqual(physical(replay),physical(result));
}
const recovery=requests.find(r=>r.id===invalid.recovery_request_id);assert.ok(recovery);const baseline=JSON.parse(rows.find(r=>r.id===recovery.id).raw);
function direct(req){
 if(req.mode==='run-controls')return call('atlas_run_controls_scope_with_settings',[req.model,req.parameters,req.initial,req.protocol,req.controls_bits_csv,req.integration_settings]);
 return call('atlas_run_scope_with_settings',[req.model,req.parameters,req.initial,req.protocol,req.target,req.steps,req.cycles,req.integration_settings]);
}
const failures=[];
for(const req of invalid.cases){
 const row={id:req.id,request:req,raw:direct(req)};failures.push(row);writeFileSync(file('rejections.json'),JSON.stringify(failures,null,2)+'\n');
 const rejected=JSON.parse(row.raw);assert.equal(rejected.ok,false,req.id);assert.ok(!Object.hasOwn(rejected,'points')||Array.isArray(rejected.points)&&rejected.points.length===0);
 const recovered=runScopedLaboratory(engine,spec(recovery),catalogue);row.recovery_raw=lastRaw;writeFileSync(file('rejections.json'),JSON.stringify(failures,null,2)+'\n');assert.deepEqual(physical(recovered),physical(baseline));
}
assert.equal(rows.length,15);assert.equal(replays.length,14);assert.equal(failures.length,12);assert.equal(calls.length,93);
console.log(JSON.stringify({passed:true,backend:role,paths:14,points:834,export_import_replays:14,rejection_recovery_pairs:12,raw_calls:93,recovery_scope:role==='synthetic'?'manufactured same-instance':role==='wasm'?'same-instance':'fresh-process'}));
