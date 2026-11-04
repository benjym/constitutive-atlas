// Full14 GIS paths through the actual C ABI, including persistent failure recovery.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};
for(let i=2;i<process.argv.length;i+=2){const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in options));options[k]=resolve(process.argv[i+1]);}
for(const k of ['--native-report','--wasm','--output'])assert.ok(options[k],`${k} required`);
const input=JSON.parse(readFileSync(options['--native-report']));assert.equal(input.version,'gis2024-coupled-integration-0.1');
const wasm=await (await import(pathToFileURL(options['--wasm']))).default();
const descriptor=JSON.parse(wasm.ccall('atlas_describe','string',[],[]));assert.equal(descriptor.sha256,input.catalogue_hash);assert.equal(descriptor.models.length,1);
const names=Object.keys(descriptor.models[0].parameters);
const call=r=>JSON.parse(wasm.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),[r.model,r.parameters.join(','),r.initial.join(','),r.strain.join(','),r.settings.join(',')]));
let maximumParity=0,calls=0;
const records=structuredClone(input.records);
for(const group of records){
 let previous;
 for(const record of group.calls){
  const r=record.request,expected=record.response;if(previous)r.initial=previous.slice();
  const actual=call(r);assert.equal(actual.ok,true,actual.message);assert.equal(actual.state.length,14);
  for(const k of ['model','parameters','initial','strain'])assert.deepEqual(actual[k],r[k],k);
  for(const k of ['catalogue_hash','integration_settings'])assert.deepEqual(actual[k],expected[k],k);
  const scales=Array(6).fill(r.parameters[names.indexOf('p_scale')]).concat([1],Array(6).fill(r.parameters[names.indexOf('R')]),[1]);
  actual.state.forEach((x,i)=>{assert.ok(Number.isFinite(x));const error=Math.abs(x-expected.state[i])/scales[i];maximumParity=Math.max(maximumParity,error);assert.ok(error<=2e-10,`${group.case}: component${i} parity ${error}`);});
  record.response=actual;previous=actual.state;calls++;
 }
}
// All histories must remain unchanged on failed updates; subsequent valid calls
// must reproduce the unfailed control in the same live module instance.
const base=structuredClone(input.records.find(g=>g.tolerance===1e-8&&g.partitions===1).calls[0].request);
const good=call(base);assert.equal(good.ok,true);
const failure_probes=[],recovery_responses=[];
for(const original of input.failure_probes){
 const probe=structuredClone(original),actual=call(probe.request),zero=probe.kind==='zero';
 assert.equal(actual.ok,zero);assert.deepEqual(actual.state,probe.request.initial);
 if(probe.kind==='budget')assert.ok(actual.diagnostics.substeps>0);
 const recovered=call(base);assert.deepEqual(recovered,good,'persistent recovery');recovery_responses.push({after:probe.kind,request:structuredClone(base),response:recovered});probe.response=actual;failure_probes.push(probe);
}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
writeFileSync(options['--output'],JSON.stringify({...input,version:'gis2024-coupled-integration-wasm-0.1',records,assessment:undefined,failure_probes,
 native_report_sha256:sha(options['--native-report']),wasm_loader_sha256:sha(options['--wasm']),wasm_binary_sha256:sha(options['--wasm'].replace(/\.m?js$/,'.wasm')),
 maximum_scaled_native_parity:maximumParity,persistent_recovery_verified:true,recovery_control:{request:base,response:good},recovery_responses},null,2)+'\n');
console.log(`GIS Wasm: ${calls} chained updates, native parity and persistent rollback/zero recovery passed; independent assessment required.`);
