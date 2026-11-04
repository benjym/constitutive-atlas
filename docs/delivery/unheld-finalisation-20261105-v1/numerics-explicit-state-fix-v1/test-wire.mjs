// Manufactured responses/wire only: no native process or generated module.
import assert from'node:assert/strict';import fs from'node:fs';import{gunzipSync}from'node:zlib';import{resolve,dirname}from'node:path';import{fileURLToPath}from'node:url';
const H=dirname(fileURLToPath(import.meta.url)),W='/private/tmp/atlas-baseline-delivery-20261105/source';const{normalizeSettings,settingsCsv}=await import('file://'+W+'/web/numerics.mjs');const rows=JSON.parse(gunzipSync(fs.readFileSync(W+'/catalogue/investigations/update-tangent-v1/results.json.gz'))).slice(0,5),expected=new Map(rows.map(r=>[r.model,r.parent.join(',')]));
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;const defaults=normalizeSettings();
async function exercise(source){
 const marker="if(options['--wasm']||options['--native']){";let block=source.slice(source.indexOf(marker)+marker.length,source.lastIndexOf("\nif(options['--output'])"));block=block.slice(0,block.lastIndexOf('}'));
 const importText="(await import(pathToFileURL(resolve(options['--wasm'])))).default";assert.ok(block.includes(importText));block=block.replace(importText,'mockFactory');
 const report={pairs:[]},calls=[];let last=null;
 const spawnSync=(exe,args)=>{
  const value=k=>args[args.indexOf(k)+1],model=value('--model');assert.ok(args.includes('--initial'),'manufactured: explicit native initial missing');assert.equal(value('--initial'),expected.get(model));
  const mode=value('--mode'),csv=args.includes('--integration-settings')?value('--integration-settings'):settingsCsv(defaults);let result;
  if(mode==='run'){const nums=csv.split(',').map(Number),settings={...defaults,residual_tolerance:nums[0],rate_tolerance:nums[1],max_iterations:nums[2],max_depth:nums[3],max_substeps:nums[4],max_backtracks:nums[5]};result={ok:nums[2]!==1,message:'manufactured',integration_settings:settings,points:nums[2]===1?[{}]:[]};}
  else if(mode==='linearize')result={ok:true,tangent_ok:true,tangent_message:'manufactured'};else{assert.equal(mode,'integrate');result={ok:false,message:'manufactured invalid settings'};assert.equal(csv,'0,1e-6,45,14,20000,11');}
  last={args,model,mode,result};calls.push(last);return{error:undefined,stderr:'',status:result.ok?0:1,stdout:JSON.stringify(result)};
 };
 const mockFactory=async()=>({ccall(fn,type,types,wire){assert.equal(type,'string');assert.equal(wire[0],last.model);assert.equal(wire[1],'');assert.equal(wire[2],expected.get(last.model));assert.equal(types.length,wire.length);assert.ok(fn.startsWith('atlas_'));return JSON.stringify(last.result);}});
 const fn=new AsyncFunction('assert','options','mockFactory','gunzipSync','readFileSync','resolve','root','settingsCsv','defaults','normalizeSettings','spawnSync','report','verifyReturnedSettings',block);
 await fn(assert,{'--wasm':'manufactured-module-only','--native':'manufactured-native-only'},mockFactory,gunzipSync,fs.readFileSync,resolve,W,settingsCsv,defaults,normalizeSettings,spawnSync,report,(r,s)=>assert.deepEqual(r.integration_settings,s));
 assert.equal(report.pairs.length,17);assert.equal(calls.length,17);assert.equal(calls.filter(c=>c.mode==='linearize').length,10);assert.equal(calls.filter(c=>c.mode==='run').length,6);assert.equal(calls.filter(c=>c.mode==='integrate').length,1);return report;
}
const original=fs.readFileSync(W+'/tools/test_numerics.mjs','utf8'),proposed=fs.readFileSync(H+'/proposed/tools/test_numerics.mjs','utf8');await assert.rejects(()=>exercise(original),/explicit native initial missing/);const report=await exercise(proposed);console.log(JSON.stringify({status:'PASS_MANUFACTURED_WIRE_ONLY',original_missing_state_reproduced:true,original_pairs:report.pairs.length,initial_wire_checks:34,native_processes:0,generated_module_imports:0,material_evaluations:0}));
