// Isolated checked expm C ABI: full derivatives, contexts and persistent recovery.
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};
for(let i=2;i<process.argv.length;i+=2){const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in options));options[k]=resolve(process.argv[i+1]);}
for(const k of ['--native-report','--wasm','--output'])assert.ok(options[k],`${k} required`);
const native=JSON.parse(readFileSync(options['--native-report']));
assert.equal(native.version,'checked-symmetric-expm-study-v1');assert.equal(native.backend,'native');
const wasm=await (await import(pathToFileURL(options['--wasm']))).default();
const call=csv=>JSON.parse(wasm.ccall('atlas_expm_probe','string',['string','number'],[csv,0]));
const records=structuredClone(native.records);let maximumParity=0;
for(const record of records){
 const expected=record.response,actual=call(record.request.csv);
 for(const key of ['ok','mode','operator_version','catalogue_hash','input','contexts','primitive_ok','schema_ok'])assert.deepEqual(actual[key],expected[key],key);
 for(const key of ['values','schema_values','jacobian','schema_jacobian']){
  const a=actual[key].flat(),b=expected[key].flat();assert.equal(a.length,b.length);
  assert.ok(a.every(x=>typeof x==='number'&&Number.isFinite(x)));
  const error=Math.hypot(...a.map((x,i)=>x-b[i]))/Math.max(1,Math.hypot(...b));
  maximumParity=Math.max(maximumParity,error);assert.ok(error<=2e-13,`${record.id}: ${key} parity ${error}`);
 }
 record.response=actual;
}
const control=call(records[0].request.csv);assert.deepEqual(control,records[0].response);
const invalid_records=structuredClone(native.invalid_records);
for(const record of invalid_records){
 record.response=call(record.request.csv);assert.deepEqual(record.response,native.invalid_records.find(r=>r.request.id===record.request.id).response);
 record.recovery=call(records[0].request.csv);assert.deepEqual(record.recovery,control,'persistent recovery');
}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const report={...native,backend:'wasm',records,invalid_records,native_report_sha256:sha(options['--native-report']),wasm_loader_sha256:sha(options['--wasm']),wasm_binary_sha256:sha(options['--wasm'].replace(/\.m?js$/,'.wasm')),maximum_scaled_native_parity:maximumParity};
delete report.binary_sha256;delete report.assessment;
writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
console.log(`expm Wasm: ${records.length} full Jacobians, ${invalid_records.length} invalid calls and persistent recoveries; maximum native parity ${maximumParity}. Run Python independent assessment.`);
