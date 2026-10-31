import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const [stage,role,build,outdir]=process.argv.slice(2);assert.ok(['native','wasm'].includes(role));
const requests=JSON.parse(readFileSync(resolve(stage,'requests.json'),'utf8'));assert.equal(requests.length,14);
const invalid=JSON.parse(readFileSync(resolve(stage,'rejection-requests.json'),'utf8'));
const work=mkdtempSync('/private/tmp/atlas-mc-explicit-wire-');let serial=0,engine;
if(role==='wasm')engine=await(await import(pathToFileURL(resolve(build,'atlas-preview.js')))).default();
function native(args){const r=spawnSync(resolve(build,'atlas_laboratory_preview'),args,{encoding:'utf8',timeout:30000});assert.ok([0,1].includes(r.status),r.stderr);return r.stdout;}
function call(req){
 if(role==='native'){
  const args=['--mode',req.mode,'--model',req.model,'--parameters',req.parameters,'--initial',req.initial,'--protocol',String(req.protocol),'--integration-settings',req.integration_settings];
  if(req.mode==='run-controls'){const file=resolve(work,`${serial++}.csv`);writeFileSync(file,req.controls_bits_csv);args.push('--laboratory-controls-file',file);}
  else args.push('--target',String(req.target),'--steps',String(req.steps),'--cycles',String(req.cycles));
  return native(args);
 }
 if(req.mode==='run-controls')return engine.ccall('atlas_run_controls_with_settings','string',['string','string','string','number','string','string'],[req.model,req.parameters,req.initial,req.protocol,req.controls_bits_csv,req.integration_settings]);
 return engine.ccall('atlas_run_with_settings','string',['string','string','string','number','number','number','number','string'],[req.model,req.parameters,req.initial,req.protocol,req.target,req.steps,req.cycles,req.integration_settings]);
}
const journalFile=resolve(outdir,'journal.json');assert.ok(!existsSync(journalFile));
const rows=[{id:'describe',raw:role==='native'?native(['--describe']):engine.ccall('atlas_describe','string',[],[])}];
writeFileSync(journalFile,JSON.stringify(rows,null,2)+'\n');
for(const req of requests){rows.push({id:req.id,request:req,raw:call(req)});writeFileSync(journalFile,JSON.stringify(rows,null,2)+'\n');}
const recovery=requests.find(x=>x.id===invalid.recovery_request_id);assert.ok(recovery);
const original=JSON.parse(rows.find(x=>x.id===recovery.id).raw);assert.equal(original.ok,true,original.message);
const physical=r=>{const {elapsed_ms,...rest}=r;return rest;};
const records=[],path=resolve(outdir,'rejections.json');assert.ok(!existsSync(path));
for(const req of invalid.cases){
 const row={id:req.id,request:req,raw:call(req),recovery_raw:call(recovery)};records.push(row);writeFileSync(path,JSON.stringify(records,null,2)+'\n');
 const failure=JSON.parse(row.raw);assert.equal(failure.ok,false,req.id);assert.ok(!Object.hasOwn(failure,'points')||(Array.isArray(failure.points)&&failure.points.length===invalid.expected_invalid_points),req.id);
 assert.deepEqual(physical(JSON.parse(row.recovery_raw)),physical(original),req.id+' recovery');
}
const report={passed:true,backend:role,requests:requests.length,points:rows.slice(1).reduce((n,r)=>n+JSON.parse(r.raw).points.length,0),rejected_requests:records.length,recovery_calls:records.length,recovery_scope:role==='wasm'?'same-instance':'fresh-process'};
writeFileSync(resolve(outdir,'rejection-assessment.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
