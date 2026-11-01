// Saved full-response compatibility collector. No tolerances or physics here.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const [role,build,requestsFile,output]=process.argv.slice(2);assert(['native','wasm'].includes(role));
const requests=JSON.parse(readFileSync(requestsFile,'utf8')),calls=[],rows=[];
const temp=mkdtempSync('/private/tmp/atlas-mc-compat-wire-');
const mod=role==='wasm'?await(await import(pathToFileURL(resolve(build,'atlas.js')))).default():null;
function call(name,args){
 let raw,process;
 if(mod)raw=mod.ccall(name,'string',args.map(x=>typeof x==='number'?'number':'string'),args);
 else{
  let argv=['--describe'];
  if(name!=='atlas_describe'){
   const wire=resolve(temp,`${rows.length}.csv`);writeFileSync(wire,args[4]);
   argv=['--mode','run-controls','--response-contract','stress-scope-0.1','--model',args[0],'--parameters',args[1],'--initial',args[2],'--protocol',String(args[3]),'--laboratory-controls-file',wire,'--integration-settings',args[5]];
  }
  const p=spawnSync(resolve(build,'atlas_solver'),argv,{encoding:'utf8',timeout:30000});raw=p.stdout;
  process={status:p.status,signal:p.signal,error:p.error?String(p.error):null,stderr:p.stderr};
 }
 calls.push({name,args,raw,...(process?{process}:{})});save();return raw;
}
function save(){writeFileSync(output,JSON.stringify({role,rows,calls},null,2)+'\n');}
const descriptor=call('atlas_describe',[]);
for(const request of requests){
 const s=request.specification,settings=['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'].map(k=>s.integration_settings[k]).join(',');
 const raw=call('atlas_run_controls_scope_with_settings',[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.loading.controls_bits.join(','),settings]);
 rows.push({id:request.id,raw});save();
}
assert.equal(rows.length,12);assert.equal(calls.length,13);save();
