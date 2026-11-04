// Replay the retained exact-reference matrix through the real C ABI.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};
for(let i=2;i<process.argv.length;i+=2){
 const key=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(key)&&process.argv[i+1]&&!(key in options));
 options[key]=resolve(process.argv[i+1]);
}
for(const key of ['--native-report','--wasm','--output'])assert.ok(options[key],`${key} required`);
const input=JSON.parse(readFileSync(options['--native-report']));
assert.equal(input.version,'clay2013-isotropic-integration-0.1');
const create=(await import(pathToFileURL(options['--wasm']))).default,wasm=await create();
const call=r=>JSON.parse(wasm.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),
 [r.model,r.parameters.join(','),r.initial.join(','),r.strain.join(','),r.settings.join(',')]));
const records=structuredClone(input.records);
let calls=0,maximumParity=0;
for(const group of records){
 for(const record of group.calls){
  const expected=record.response,actual=call(record.request);assert.equal(actual.ok,true,actual.message);
  for(const key of ['model','catalogue_hash','parameters','initial','strain','integration_settings'])assert.deepEqual(actual[key],expected[key],key);
  assert.equal(actual.state.length,7);
  actual.state.forEach((x,i)=>{
   assert.ok(Number.isFinite(x));const error=Math.abs(x-expected.state[i])/Math.max(1,Math.abs(expected.state[i]));
   maximumParity=Math.max(maximumParity,error);assert.ok(error<=2e-10,`${group.kind} component${i}: ${error}`);
  });
  record.response=actual;calls++;
 }
}
// Persistent-module failures must not contaminate a subsequent valid call.
const base=structuredClone(input.records.find(x=>x.pressure===10000&&x.kind==='compression'&&x.tolerance===1e-8).calls[0].request);
const good=call(base);assert.equal(good.ok,true);
const probes=[];
for(const kind of ['budget','domain','zero']){
 const r=structuredClone(base);
 if(kind==='budget')r.settings[4]=3;
 if(kind==='domain'){r.initial[6]=.1;r.strain=[.2/3,.2/3,.2/3,0,0,0];r.settings[4]=256;}
 if(kind==='zero')r.strain=Array(6).fill(0);
 const a=call(r);assert.equal(a.ok,kind==='zero');assert.deepEqual(a.state,r.initial);
 if(kind!=='zero')assert.ok(a.diagnostics.substeps>0);
 assert.deepEqual(call(base),good);probes.push({kind,request:r,response:a});
}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const report={...input,version:'clay2013-isotropic-wasm-0.1',records,summary:undefined,native_report_sha256:sha(options['--native-report']),
 wasm_loader_sha256:sha(options['--wasm']),wasm_binary_sha256:sha(options['--wasm'].replace(/\.m?js$/,'.wasm')),
 maximum_scaled_native_parity:maximumParity,failure_probes:probes};
writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
console.log(`Clay2013 Wasm: ${calls} paired updates, persistent rollback/zero probes passed; exact-reference assessment required separately.`);
