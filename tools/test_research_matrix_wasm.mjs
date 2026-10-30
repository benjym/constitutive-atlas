// Replay research matrices through the real C ABI, chaining actual Wasm states.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};
for(let i=2;i<process.argv.length;i+=2){
 const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in options));
 options[k]=resolve(process.argv[i+1]);
}
for(const k of ['--native-report','--wasm','--output'])assert.ok(options[k],`${k} required`);
const input=JSON.parse(readFileSync(options['--native-report']));
const rates=input.version==='gis2024-coupled-rate-0.1';
assert.ok(rates||input.version==='clay2013-nonisotropic-integration-0.1','unsupported research matrix');
const wasm=await (await import(pathToFileURL(options['--wasm']))).default();
const descriptor=JSON.parse(wasm.ccall('atlas_describe','string',[],[]));
assert.equal(descriptor.sha256,input.catalogue_hash);assert.equal(descriptor.models.length,1);
const call=r=>JSON.parse(wasm.ccall(rates?'atlas_evaluate':'atlas_integrate_with_settings','string',Array(5).fill('string'),rates?
 [r.model,r.parameters.join(','),r.initial.join(','),r.initial.join(','),r.strain.join(',')]:
 [r.model,r.parameters.join(','),r.initial.join(','),r.strain.join(','),r.settings.join(',')]));
const records=structuredClone(input.records);let calls=0,maximumParity=0;
for(const group of records){
 let actualState;
 for(const record of rates?[group]:group.calls){
  const expected=record.response;
  if(actualState)record.request.initial=actualState.slice();
  const actual=call(record.request);assert.equal(actual.ok,true,actual.message);
  if(!rates){
   for(const k of ['model','parameters','initial','strain'])assert.deepEqual(actual[k],record.request[k],k);
   for(const k of ['catalogue_hash','integration_settings'])assert.deepEqual(actual[k],expected[k],k);
  }
  const key=rates?'values':'state';assert.equal(actual[key].length,rates?14:7);
  actual[key].forEach((x,i)=>{
   assert.ok(Number.isFinite(x));const error=Math.abs(x-expected[key][i])/Math.max(1,Math.abs(expected[key][i]));
   maximumParity=Math.max(maximumParity,error);assert.ok(error<=2e-10,`${group.case} component${i}: ${error}`);
  });
  record.response=actual;if(!rates)actualState=actual.state;calls++;
 }
}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const report={...input,version:rates?'gis2024-coupled-rate-wasm-0.1':'clay2013-nonisotropic-wasm-0.1',records,summary:undefined,
 native_report_sha256:sha(options['--native-report']),wasm_loader_sha256:sha(options['--wasm']),
 wasm_binary_sha256:sha(options['--wasm'].replace(/\.m?js$/,'.wasm')),maximum_scaled_native_parity:maximumParity};
writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
console.log(`${calls} Wasm ${rates?'rates':'chained updates'} passed native parity; independent assessment required separately.`);
