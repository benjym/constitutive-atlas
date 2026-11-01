import assert from'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync}from'node:fs';
import {resolve,join}from'node:path';
import {pathToFileURL}from'node:url';
import {spawnSync}from'node:child_process';
import {tmpdir}from'node:os';
import {recordedWire,recordedSettings,runRecorded}from'../../../web/recorded.mjs';
import {settingsCsv}from'../../../web/numerics.mjs';
const [native,wasmFile,output]=process.argv.slice(2),requests=JSON.parse(readFileSync(new URL('./requests.json',import.meta.url),'utf8'));
const observations=[],save=()=>writeFileSync(output,JSON.stringify(observations)+'\n');
const engine=await(await import(pathToFileURL(resolve(wasmFile)))).default();
function call(id,argv,fn,args){const p=spawnSync(native,argv,{encoding:'utf8',timeout:60000,maxBuffer:10*1024*1024});const row={id,argv,status:p.status,signal:p.signal,error:p.error?String(p.error):null,stderr:p.stderr,native_raw:p.stdout};observations.push(row);save();assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');row.wasm_raw=engine.ccall(fn,'string',args.map(x=>typeof x==='number'?'number':'string'),args);save();const n=JSON.parse(p.stdout),w=JSON.parse(row.wasm_raw);assert.equal(p.status,n.ok?0:1);assert.equal(n.ok,w.ok);return [n,w];}
for(const c of requests.evaluations){const args=[c.model,c.parameters.join(','),c.current.join(','),c.initial.join(','),c.strain.join(',')];const result=call(c.id,['--mode','evaluate','--model',c.model,'--parameters',args[1],'--current',args[2],'--initial',args[3],'--strain',args[4]],'atlas_evaluate',args);assert.equal(result[0].ok,c.expected_evaluation_ok);}
const s=requests.original_recorded,wire=recordedWire(s),settings=recordedSettings(s),tmp=mkdtempSync(join(tmpdir(),'gis-recorded-diagnosis-'));const controls=join(tmp,'controls.csv'),knots=join(tmp,'knots.csv');writeFileSync(controls,wire.controls.join(','));writeFileSync(knots,wire.knots.join(','));
const result=call('original-recorded',['--mode','recorded','--model',s.model,'--parameters',s.parameters.join(','),'--initial',s.initial.join(','),'--initial-strain',s.path.initial_strain.join(','),'--recorded-controls-file',controls,'--recorded-knots-file',knots,'--integration-settings',settingsCsv(settings.material),'--recorded-settings',Object.values(settings.control).join(',')],'atlas_replay_recorded',[s.model,s.parameters.join(','),s.initial.join(','),s.path.initial_strain.join(','),wire.controls.join(','),wire.knots.join(','),settingsCsv(settings.material),Object.values(settings.control).join(',')]);
let parent=s.initial,previous=s.path.initial_strain;
for(let i=1;i<s.path.knots.length;i++){const target=s.path.knots[i].targets,de=target.map((v,j)=>v-previous[j]);const args=[s.model,s.parameters.join(','),parent.join(','),de.join(',')];const [n,w]=call('direct-segment-'+i,['--mode','integrate','--model',s.model,'--parameters',args[1],'--initial',args[2],'--strain',args[3]],'atlas_integrate',args);if(!n.ok){assert.deepEqual(n.state,parent);break;}parent=n.state;previous=target;}
console.log(JSON.stringify({calls:observations.length,recorded_native_ok:result[0].ok,recorded_wasm_ok:result[1].ok,failed_knot:result[0].failed_knot,points:result[0].points.length}));
