// Same-instance checked scalar log1p probe; independently assess JSON with Python.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const opts={};for(let i=2;i<process.argv.length;i+=2){const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in opts));opts[k]=resolve(process.argv[i+1]);}
for(const k of ['--native-report','--wasm','--output'])assert.ok(opts[k],`${k} required`);
const native=JSON.parse(readFileSync(opts['--native-report']));assert.equal(native.version,'checked-scalar-log1p-study-v1');assert.equal(native.backend,'native');assert.equal(native.records.length,38);assert.equal(native.invalid_records.length,10);
const module=await(await import(pathToFileURL(opts['--wasm']))).default();
const call=text=>JSON.parse(module.ccall('atlas_log1p_probe','string',['string'],[text]));
const records=structuredClone(native.records);for(const row of records)row.response=call(row.request.text);
const invalid_records=structuredClone(native.invalid_records);for(const row of invalid_records){row.response=call(row.request.text);row.recovery=call(records[0].request.text);}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const report={...native,backend:'wasm',records,invalid_records,native_report_sha256:sha(opts['--native-report']),wasm_loader_sha256:sha(opts['--wasm']),wasm_binary_sha256:sha(opts['--wasm'].replace(/\.m?js$/,'.wasm'))};delete report.assessment;delete report.binary_sha256;
// Write raw records before any assessment/parity assertion.
writeFileSync(opts['--output'],JSON.stringify(report,null,2)+'\n');
for(let i=0;i<records.length;i++)for(const k of ['ok','operator_version','catalogue_hash','contexts','primitive_ok','schema_ok','negative_zero'])assert.deepEqual(records[i].response[k],native.records[i].response[k],`metadata ${i} ${k}`);
for(let i=0;i<records.length;i++)assert.ok(typeof records[i].response.input==='number'&&records[i].response.input===native.records[i].response.input,'numeric input echo');
for(let i=0;i<invalid_records.length;i++){assert.deepEqual(invalid_records[i].response,native.invalid_records[i].response);assert.deepEqual(invalid_records[i].recovery,records[0].response);}
console.log(`log1p Wasm raw38cases/10invalid/recovery saved. Run Python --report assessment for fresh650digit numerical validation.`);
