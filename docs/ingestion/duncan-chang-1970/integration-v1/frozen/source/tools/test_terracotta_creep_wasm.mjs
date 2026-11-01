// The full frozen-preparation matrix, through the real C ABI and native CLI.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const argv=process.argv.slice(2),options={};
for(let i=0;i<argv.length;i+=2){
 assert.ok(['--wasm','--native','--output'].includes(argv[i])&&argv[i+1], 'expected --wasm/--native/--output value');
 assert.ok(!(argv[i] in options),'duplicate option');options[argv[i]]=argv[i+1];
}
const wasmPath=resolve(options['--wasm']??resolve(root,'build-wasm/research.js'));
assert.ok(/\.(?:m?js)$/.test(wasmPath),'expected a .js or .mjs Wasm loader');
const nativePath=resolve(options['--native']??resolve(root,'build/atlas_research_solver'));
const inputPath=resolve(root,'catalogue/investigations/terracotta-creep-v1/native.json');
const inputs=JSON.parse(readFileSync(inputPath));
assert.equal(inputs.length,9);
const create=(await import(pathToFileURL(wasmPath))).default,wasm=await create();
const signature=[...Array(7).fill('string'),...Array(8).fill('number')];
const defaults={relative_tolerance:1e-6,absolute_scale_fraction:1e-9,minimum_step:1e-12,
 maximum_step:1e6,maximum_substeps:20000,nonlinear_tolerance:1e-10,maximum_iterations:40};
const csv=values=>values.join(',');
const relativeParity=1e-7; // Independent reference bounds are checked separately in Python.
const records=[];
for(const input of inputs){
 const request=input.request,settings={...defaults,...request.solver};
 const wire=request.segments.flatMap(s=>[s.duration,s.samples,...s.controls.flatMap(c=>[
  +(c.quantity==='stress'),{hold:0,rate:1,target:2}[c.kind],c.value??0])]);
 const ids=request.segments.map(s=>s.id).join(',');
 const strings=[request.model,csv(request.parameters),csv(request.initial),csv(request.initial_strain),
  csv(request.initial_strain_rate),csv(wire),ids];
 const numbers=[request.start_time,settings.relative_tolerance,settings.absolute_scale_fraction,
  settings.minimum_step,settings.maximum_step,settings.maximum_substeps,
  settings.nonlinear_tolerance,settings.maximum_iterations];
 const actual=JSON.parse(wasm.ccall('atlas_run_schedule','string',signature,[...strings,...numbers]));
 const command=['--mode','schedule','--model',request.model,'--parameters',strings[1],
  '--initial',strings[2],'--initial-strain',strings[3],'--initial-strain-rate',strings[4],
  '--segments',strings[5],'--segment-ids',ids,'--start-time',String(numbers[0]),
  '--rtol',String(numbers[1]),'--atol',String(numbers[2]),'--min-time-step',String(numbers[3]),
  '--max-time-step',String(numbers[4]),'--max-substeps',String(numbers[5]),
  '--nonlinear-tolerance',String(numbers[6]),'--max-iterations',String(numbers[7])];
 const process=spawnSync(nativePath,command,{encoding:'utf8',timeout:60000,maxBuffer:4*1024*1024});
 assert.equal(process.error,undefined);assert.equal(process.status,0,process.stderr);
 const expected=JSON.parse(process.stdout);
 assert.equal(actual.ok,true,actual.message);assert.equal(expected.ok,true,expected.message);
 for(const key of ['schema_version','units','model','start_time','parameters','initial','initial_strain',
  'initial_strain_rate','segments','solver','catalogue_hash'])assert.deepEqual(actual[key],expected[key],key);
 assert.equal(actual.points.length,expected.points.length);
 const errors=Object.fromEntries(['state','strain','strain_rate','observables'].map(key=>[key,0]));
 actual.points.forEach((p,i)=>{
  const q=expected.points[i];
  for(const key of ['time','segment','side'])assert.equal(p[key],q[key],key);
  for(const key of Object.keys(errors)){
   assert.equal(p[key].length,q[key].length);
   p[key].forEach((value,j)=>{
    const target=q[key][j];
    if(value===null||target===null){assert.equal(value,target);return;}
    assert.equal(typeof value,'number');assert.equal(typeof target,'number');
    assert.ok(Number.isFinite(value)&&Number.isFinite(target));
    const error=Math.abs(value-target)/Math.max(1,Math.abs(target));
    errors[key]=Math.max(errors[key],error);
    assert.ok(error<=relativeParity,`${input.case} ${input.relative_tolerance} ${key}[${j}]: ${error}`);
   });
  }
  for(const point of [p,q]){
   for(const key of ['iterations','substeps','rejected'])assert.ok(Number.isInteger(point[key])&&point[key]>=0);
   assert.ok(Number.isFinite(point.temporal_error_norm)&&point.temporal_error_norm>=0&&point.temporal_error_norm<=1);
   assert.ok(Number.isFinite(point.nonlinear_residual_norm)&&point.nonlinear_residual_norm>=0&&point.nonlinear_residual_norm<=settings.nonlinear_tolerance);
  }
 });
 records.push({case:input.case,relative_tolerance:input.relative_tolerance,request,
  native:expected,wasm:actual,maximum_scaled_parity_errors:errors});
}
const sha=path=>createHash('sha256').update(readFileSync(path)).digest('hex');
const report={version:'terracotta-creep-wasm-parity-0.1',relative_parity_tolerance:relativeParity,
 artifacts:{request_matrix_sha256:sha(inputPath),wasm_loader_sha256:sha(wasmPath),
  wasm_binary_sha256:sha(wasmPath.replace(/\.(?:m?js)$/,'.wasm')),native_binary_sha256:sha(nativePath)},records};
if(options['--output']){
 const path=resolve(options['--output']);mkdirSync(dirname(path),{recursive:true});
 writeFileSync(path,JSON.stringify(report,null,2)+'\n');
}
console.log(`Terracotta prepared creep: ${records.length} native/Wasm pairs passed; numerical reference assessment is a separate required check.`);
