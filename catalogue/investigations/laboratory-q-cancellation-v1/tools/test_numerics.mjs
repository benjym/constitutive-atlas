// Pure browser settings checks; optional serial native/Wasm integration checks.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {normalizeSettings,settingsCsv,settingFields,runLaboratory,verifyReturnedSettings} from '../web/numerics.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const options={};for(let i=2;i<process.argv.length;i+=2){assert.ok(['--wasm','--native','--output'].includes(process.argv[i]));assert.ok(process.argv[i+1]);assert.ok(!options[process.argv[i]]);options[process.argv[i]]=process.argv[i+1];}
const defaults=normalizeSettings();
assert.equal(settingsCsv(), '2e-10,0.000001,45,14,20000,11');
assert.notEqual(normalizeSettings(),defaults);assert.deepEqual(normalizeSettings(defaults),defaults);
for(const value of [null,[],{}, {...defaults,version:'future'}, {...defaults,norm:'other'}, {...defaults,unknown:1}])assert.throws(()=>normalizeSettings(value));
for(const f of settingFields){
 for(const bad of [undefined,null,'1',NaN,Infinity,-1,...(f.integer?[.5,f.max+1]:[0])])assert.throws(()=>normalizeSettings({...defaults,[f.key]:bad}));
 const edge={...defaults,[f.key]:f.integer?f.min:1e-20};assert.doesNotThrow(()=>normalizeSettings(edge));
}
verifyReturnedSettings({integration_settings:defaults},defaults);
for(const result of [{ok:true},{integration_settings:{...defaults,max_depth:13}},{integration_settings:{...defaults,version:'future'}}])assert.throws(()=>verifyReturnedSettings(result,defaults));
assert.throws(()=>verifyReturnedSettings({ok:false,message:'inadmissible input'},defaults),/inadmissible input/);
let called=false;const spec={model:'test',parameters:[1,2],initial:[3,4],protocol:1,target:.001,steps:8,cycles:0};
runLaboratory({ccall:(name,output,types,args)=>{called=true;assert.equal(name,'atlas_run_with_settings');assert.equal(output,'string');assert.equal(types.length,8);assert.deepEqual(args,['test','1,2','3,4',1,.001,8,0,settingsCsv(defaults)]);return JSON.stringify({ok:true,integration_settings:defaults});}},spec);assert.ok(called);
assert.throws(()=>runLaboratory({ccall:()=>JSON.stringify({ok:true})},spec),/matching build/);
console.log('Browser settings validation, default migration, wire mapping and stale-engine checks passed.');
const report={status:'passed',pure_checks:['defaults and legacy migration','version, shape and bounds','response settings agreement','worker C ABI mapping and stale-engine rejection'],pairs:[]};
if(options['--wasm']||options['--native']){
 assert.ok(options['--wasm']&&options['--native'],'Both --wasm and --native are required');
 const createAtlas=(await import(pathToFileURL(resolve(options['--wasm'])))).default;const engine=await createAtlas();
 const rows=JSON.parse(gunzipSync(readFileSync(resolve(root,'catalogue/investigations/update-tangent-v1/results.json.gz')))).slice(0,5);
 const configured={...defaults,residual_tolerance:1e-11,rate_tolerance:1e-7,max_iterations:60,max_substeps:5000,max_backtracks:8};
 function compare(a,b,path='response'){
  if(typeof b==='number'){assert.equal(typeof a,'number',path);assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=1e-7*Math.max(1,Math.abs(b)),path+': '+a+' != '+b);return;}
  if(Array.isArray(b)){assert.ok(Array.isArray(a),path);assert.equal(a.length,b.length,path);b.forEach((v,i)=>compare(a[i],v,path+'['+i+']'));return;}
  if(b&&typeof b==='object'){assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort(),path);for(const key of Object.keys(b))if(key!=='elapsed_ms')compare(a[key],b[key],path+'.'+key);return;}
  assert.equal(a,b,path);
 }
 function check(name,args,fn,types,wire){
  const run=spawnSync(resolve(options['--native']),args,{encoding:'utf8',timeout:45000});assert.equal(run.error,undefined);assert.equal(run.stderr,'');assert.notEqual(run.status,null);
  const expected=JSON.parse(run.stdout),actual=JSON.parse(engine.ccall(fn,'string',types,wire));compare(actual,expected);assert.equal(run.status,expected.ok?0:1);
  report.pairs.push({name,argv:args,returncode:run.status,native:expected,wasm:actual});return actual;
 }
 for(const row of rows){
  const csv=settingsCsv(configured);
  const result=check('configured-run/'+row.model,['--mode','run','--model',row.model,'--protocol','1','--target','.001','--steps','8','--integration-settings',csv],
   'atlas_run_with_settings',['string','string','string','number','number','number','number','string'],[row.model,'','',1,.001,8,0,csv]);
  assert.equal(result.ok,true,result.message);verifyReturnedSettings(result,configured);
  for(const settings of [undefined,configured]){
   const cli=['--mode','linearize','--model',row.model,'--initial',row.parent.join(','),'--strain',row.increment.join(',')];
   const types=['string','string','string','string'];const wire=[row.model,'',row.parent.join(','),row.increment.join(',')];
   if(settings){cli.push('--integration-settings',settingsCsv(settings));types.push('string');wire.push(settingsCsv(settings));}
   const out=check((settings?'configured':'default')+'-tangent/'+row.model,cli,settings?'atlas_linearize_with_settings':'atlas_linearize',types,wire);
   assert.equal(out.ok,true,out.message);assert.equal(out.tangent_ok,true,out.tangent_message);
  }
 }
 const limited={...defaults,max_iterations:1,max_depth:0};
 const stopped=check('limited-run',['--mode','run','--model','linear-elastic','--protocol','1','--target','.001','--steps','8','--integration-settings',settingsCsv(limited)],'atlas_run_with_settings',['string','string','string','number','number','number','number','string'],['linear-elastic','','',1,.001,8,0,settingsCsv(limited)]);assert.equal(stopped.ok,false);assert.equal(stopped.points.length,1);
 const invalid='0,1e-6,45,14,20000,11';const bad=check('invalid-settings',['--mode','integrate','--model','linear-elastic','--strain','0,0,0,0,0,0','--integration-settings',invalid],'atlas_integrate_with_settings',['string','string','string','string','string'],['linear-elastic','','','0,0,0,0,0,0',invalid]);assert.equal(bad.ok,false);
 console.log(`Native/Wasm numerical settings and full-update tangent parity passed for ${report.pairs.length} cases.`);
}
if(options['--output'])writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
