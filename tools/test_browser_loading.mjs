import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,existsSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createLoading,exportRun,importRunDocument} from '../web/loading.mjs';
import {runLaboratory,normalizeSettings,settingsCsv} from '../web/numerics.mjs';
const [native,wasmdir,outfile]=process.argv.slice(2),tmp=mkdtempSync(join(tmpdir(),'atlas-browser-loading-wire-'));let serial=0;
assert.ok(!existsSync(outfile)&&!existsSync(outfile+'.raw.json'),'Preserve existing observations');
const rawJournal=[];
function raw(role,name,args,output){rawJournal.push({role,name,args,raw:output});writeFileSync(outfile+'.raw.json',JSON.stringify(rawJournal)+'\n');return output;}
const metadata=JSON.parse(readFileSync(resolve(wasmdir,'generated/models.json'),'utf8'));assert.ok(metadata.models.length>=1);
const module=await(await import(pathToFileURL(resolve(wasmdir,'atlas.js')))).default();
const wasm={ccall:(name,type,types,args)=>raw('wasm',name,args,module.ccall(name,type,types,args))};
const nativeEngine={ccall:(name,type,types,args)=>{
 const [model,parameters,initial,protocol]=args;
 const cli=['--mode',name==='atlas_run_controls_with_settings'?'run-controls':'run','--model',model,'--parameters',parameters,'--initial',initial,'--protocol',String(protocol)];
 if(name==='atlas_run_controls_with_settings'){const file=resolve(tmp,`${serial++}.csv`);writeFileSync(file,args[4]);cli.push('--laboratory-controls-file',file,'--integration-settings',args[5]);}
 else{assert.equal(name,'atlas_run_with_settings');cli.push('--target',String(args[4]),'--steps',String(args[5]),'--cycles',String(args[6]),'--integration-settings',args[7]);}
 const p=spawnSync(native,cli,{encoding:'utf8',timeout:30000});raw('native',name,args,p.stdout);assert.ok([0,1].includes(p.status),p.stderr);return p.stdout;
}};
const report={status:'running',catalogue_hash:metadata.sha256,pairs:[]};
const physical=r=>{const {elapsed_ms,...rest}=r;return rest;};
function compare(a,b,tol,path='result'){
 if(typeof b==='number'){assert.equal(typeof a,'number',path);assert.ok(Number.isFinite(a)&&Number.isFinite(b));assert.ok(Math.abs(a-b)<=tol*Math.max(1,Math.abs(a),Math.abs(b)),path+': '+a+' vs '+b);return;}
 if(Array.isArray(b)){assert.ok(Array.isArray(a));assert.equal(a.length,b.length);b.forEach((v,i)=>compare(a[i],v,tol,path+'['+i+']'));return;}
 if(b&&typeof b==='object'){assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort());for(const k of Object.keys(b))if(k!=='elapsed_ms')compare(a[k],b[k],tol,path+'.'+k);return;}
 assert.equal(a,b,path);
}
function check(name,s,tol){
 const row={name,specification:s};report.pairs.push(row);writeFileSync(outfile,JSON.stringify(report)+'\n');
 row.native=runLaboratory(nativeEngine,s,metadata.sha256);writeFileSync(outfile,JSON.stringify(report)+'\n');
 row.wasm=runLaboratory(wasm,s,metadata.sha256);writeFileSync(outfile,JSON.stringify(report)+'\n');
 compare(row.native,row.wasm,tol);return row;
}
for(const m of metadata.models){
 const initial=m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),parameters=Object.values(m.parameters).map(p=>p.default);
 for(const protocol of [0,1,2,3,4]){
  const base={model:m.id,parameters,initial,protocol,target:protocol===3?10000:.002,steps:64,cycles:protocol===3?1:0,integration_settings:normalizeSettings()};
  for(const mode of ['legacy','current']){
   const s=mode==='current'?{...base,loading:createLoading(base)}:base;
   const row=check(mode+'/'+m.id+'/'+protocol,s,mode==='current'?1e-10:1e-7);assert.equal(row.native.ok,true,row.native.message);
   if(mode==='legacy'){
    const types=['string','string','string','number','number','number','number','string'];
    const args=[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.target,s.steps,s.cycles,settingsCsv(s.integration_settings)];
    row.direct_native=JSON.parse(nativeEngine.ccall('atlas_run_with_settings','string',types,args));
    row.direct_wasm=JSON.parse(wasm.ccall('atlas_run_with_settings','string',types,args));
    writeFileSync(outfile,JSON.stringify(report)+'\n');
    assert.deepEqual(physical(row.direct_native),physical(row.native));assert.deepEqual(physical(row.direct_wasm),physical(row.wasm));
   }

   const doc=exportRun(metadata.sha256,s,row.wasm),imported=importRunDocument(JSON.parse(JSON.stringify(doc)),metadata.sha256);
   const replay=runLaboratory(wasm,imported,metadata.sha256);assert.deepEqual(physical(replay),physical(row.wasm));row.roundtrip_replayed=true;
  }
 }
 const base={model:m.id,parameters,initial,protocol:1,target:.01,steps:100,cycles:0,integration_settings:normalizeSettings()};
 const s={...base,loading:createLoading(base)};const row=check('default/'+m.id,s,1e-10);assert.equal(row.native.ok,true,row.native.message);assert.equal(row.native.points.length,101);
}
const m=metadata.models.find(m=>m.id==='linear-elastic');const base={model:m.id,parameters:Object.values(m.parameters).map(p=>p.default),initial:m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol:1,target:.002,steps:64,cycles:0,integration_settings:normalizeSettings()};
const s={...base,loading:createLoading(base)},limited={...s,integration_settings:{...normalizeSettings(),max_iterations:1,max_depth:0}};
const failed=check('limited-prefix',limited,1e-10);assert.equal(failed.native.ok,false);assert.equal(failed.native.points.length,1);
const recovered=check('recovery',s,1e-10);assert.equal(recovered.native.ok,true);
const before=report.pairs.find(r=>r.name==='current/linear-elastic/1');assert.deepEqual(physical(recovered.wasm),physical(before.wasm));
assert.equal(report.pairs.length,11*metadata.models.length+2);report.status='passed';report.backend_runs=2*report.pairs.length;report.same_instance_wasm_export_import_replays=10*metadata.models.length;
writeFileSync(outfile,JSON.stringify(report)+'\n');console.log(`${report.pairs.length} native/Wasm pairs, ${report.same_instance_wasm_export_import_replays} same-instance import/export replays and failed-prefix recovery passed.`);
