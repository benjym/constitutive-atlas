// Pure validation plus optional serial native/Wasm recorded replay parity.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {gunzipSync} from 'node:zlib';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {parseRecordedJSON,validateRecordedRun,recordedSettings,recordedWire,runRecorded,verifyRecordedResponse,recordedSeries,restartDefaults} from '../web/recorded.mjs';
import {settingsCsv} from '../web/numerics.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),options={};
for(let i=2;i<process.argv.length;i+=2){assert.ok(['--wasm','--native','--output'].includes(process.argv[i]));assert.ok(process.argv[i+1]);options[process.argv[i]]=process.argv[i+1];}
const sample=JSON.parse(readFileSync(join(root,'protocols/recorded-linear-elastic-run.json'),'utf8'));
const example=JSON.parse(readFileSync(join(root,'protocols/recorded-dp-restart-run.json'),'utf8'));validateRecordedRun(example);
assert.deepEqual(recordedSettings({...sample,restart_settings:{}}).restarts,restartDefaults);
const original=structuredClone(sample);assert.equal(validateRecordedRun(sample),sample);assert.deepEqual(sample,original);
assert.equal(recordedWire(sample).controls.length,42);assert.equal(recordedWire(sample).knots.length,sample.path.knots.length*7);
const mutations=[s=>s.extra=1,s=>s.integration_settings=null,s=>s.control_settings=null,s=>s.restart_settings=null,s=>s.restart_settings={extra:1},s=>s.restart_settings={max_restarts:17},s=>s.restart_settings={restart_step:0},s=>s.restart_settings={restart_levels:1.5},s=>s.parameters=[],s=>s.initial=[NaN],s=>s.path.knots.reverse(),s=>s.path.knots[1].coordinate=s.path.knots[0].coordinate,s=>s.path.controls[0].coefficients.fill(0),s=>s.path.coordinate.unit='s',s=>s.path.knots[1].targets[0]=Infinity,s=>s.control_settings={max_material_trials:0},s=>s.control_settings={max_iterations:1.5},s=>s.integration_settings={max_depth:21},s=>s.path.coordinate.name=' ',s=>s.path.knots.length=1];
for(const mutate of mutations){const s=structuredClone(sample);mutate(s);assert.throws(()=>validateRecordedRun(s));}
const dependent=structuredClone(sample);dependent.path.controls.forEach(c=>{c.kind='strain';c.coefficients=[1,0,0,0,0,0];});assert.throws(()=>validateRecordedRun(dependent));
const oblique=structuredClone(sample);oblique.path.controls.forEach((c,i)=>{c.kind='strain';c.coefficients=Array.from({length:6},(_,j)=>Number(i===j)*1e-300);});assert.doesNotThrow(()=>validateRecordedRun(oblique));
assert.throws(()=>parseRecordedJSON('{"n":9007199254740993}'));assert.equal(parseRecordedJSON('{"n":9007199254740992}').n,9007199254740992);
assert.deepEqual(parseRecordedJSON('{"s":"9007199254740993 and \\\"quoted\\\""}'),{s:'9007199254740993 and "quoted"'});
assert.throws(()=>runRecorded({ccall:()=>'{"ok":true}'},sample));
const retained=JSON.parse(gunzipSync(readFileSync(join(root,'catalogue/investigations/recorded-replay-api-v1/responses.json.gz'))));
for(const {request,response} of retained)verifyRecordedResponse(response,request);
const restartRetained=JSON.parse(gunzipSync(readFileSync(join(root,'catalogue/investigations/recorded-restarts-v1/responses.json.gz'))));
for(const {request,response} of restartRetained)verifyRecordedResponse(response,request);
const enabled=restartRetained.find(x=>Object.hasOwn(x.request,'restart_settings')&&x.response.ok);
assert.ok(enabled);let endpoint;
runRecorded({ccall:(name,type,types,args)=>{endpoint=name;assert.equal(args.length,9);assert.equal(types.length,9);return JSON.stringify(enabled.response);}},enabled.request);
assert.equal(endpoint,'atlas_replay_recorded_with_restarts');
const policy=structuredClone(enabled);policy.response.restart_settings.restart_step*=2;assert.throws(()=>verifyRecordedResponse(policy.response,policy.request));
const accounting=structuredClone(enabled);accounting.response.restart_diagnostics.material_trials=-1;assert.throws(()=>verifyRecordedResponse(accounting.response,accounting.request));
const disabled=structuredClone(restartRetained.find(x=>x.request.restart_settings?.max_restarts===0));disabled.response.restart_diagnostics.searches=1;assert.throws(()=>verifyRecordedResponse(disabled.response,disabled.request));
const stray=structuredClone(retained[1]);stray.response.restart_diagnostics={searches:0,material_trials:0,accepted:0};assert.throws(()=>verifyRecordedResponse(stray.response,stray.request));
const missing=structuredClone(enabled);delete missing.response.material_trials;assert.throws(()=>verifyRecordedResponse(missing.response,missing.request));
const changed=structuredClone(retained[1]);changed.response.controls_wire[0]+=1;assert.throws(()=>verifyRecordedResponse(changed.response,changed.request));
const series=recordedSeries(retained[0].response,0);assert.equal(series.strain.length,5001);assert.equal(series.stress[0][1],100);assert.throws(()=>recordedSeries(retained[0].response,6));
const report={ok:true,pure_checks:['closed contract and finite ordered inputs','rank and row scaling','settings and optional defaults','integer literal precision','response/request agreement','component projection','opt-in bounded restart policy, counters and endpoint routing'],pairs:[]};
if(options['--wasm']||options['--native']){
 assert.ok(options['--wasm']&&options['--native']);const createAtlas=(await import(pathToFileURL(resolve(options['--wasm'])))).default,engine=await createAtlas();
 function compare(a,b,path='response'){
  if(typeof b==='number'){
   assert.equal(typeof a,'number',path);assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(b)),`${path}: ${a} != ${b}`);return;
  }
  if(Array.isArray(b)){assert.ok(Array.isArray(a),path);assert.equal(a.length,b.length,path);b.forEach((v,i)=>compare(a[i],v,`${path}[${i}]`));return;}
  if(b&&typeof b==='object'){assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort(),path);for(const key of Object.keys(b))compare(a[key],b[key],path+'.'+key);return;}
  assert.equal(a,b,path);
 }
 const dir=mkdtempSync(join(tmpdir(),'atlas-recorded-parity-'));
 try{
  for(const {request:s} of [...retained,...restartRetained,{request:example}]){
   const {controls,knots}=recordedWire(s),settings=recordedSettings(s),c=join(dir,'controls.csv'),k=join(dir,'knots.csv');writeFileSync(c,controls.join(','));writeFileSync(k,knots.join(','));
   const args=['--mode','recorded','--model',s.model,'--initial-strain',s.path.initial_strain.join(','),'--recorded-controls-file',c,'--recorded-knots-file',k,'--integration-settings',settingsCsv(settings.material),'--recorded-settings',Object.values(settings.control).join(',')];
   if(settings.restarts)args.push('--recorded-restarts',Object.values(settings.restarts).join(','));
   for(const key of ['parameters','initial'])if(s[key])args.push('--'+key,s[key].join(','));
   const proc=spawnSync(resolve(options['--native']),args,{encoding:'utf8',timeout:60000,maxBuffer:20*1024*1024});assert.equal(proc.error,undefined);assert.equal(proc.stderr,'');
   const native=JSON.parse(proc.stdout),wasm=runRecorded(engine,s);assert.equal(proc.status,native.ok?0:1);compare(wasm,native);
   for(const key of ['failed_knot','material_trials','attempted_substeps','finite_difference_probes'])assert.equal(wasm[key],native[key],key);
   report.pairs.push({request:s,native,wasm});
  }
 }finally{rmSync(dir,{recursive:true,force:true});}
}
if(options['--output'])writeFileSync(options['--output'],JSON.stringify(report)+'\n');
console.log(`Recorded-run contract checks passed; ${report.pairs.length} native/Wasm replay pairs passed.`);
