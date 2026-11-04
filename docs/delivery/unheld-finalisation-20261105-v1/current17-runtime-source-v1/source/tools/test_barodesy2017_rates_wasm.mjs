// Actual isolated research C ABI, raw checkpoints before acceptance checks.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,appendFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const opts={};for(let i=2;i<process.argv.length;i+=2){const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in opts));opts[k]=resolve(process.argv[i+1]);}
for(const k of ['--native-report','--wasm','--output'])assert.ok(opts[k]);
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const native=JSON.parse(readFileSync(opts['--native-report']));assert.equal(native.version,'barodesy2017-instantaneous-rate-study-v1');assert.equal(native.backend,'native');assert.equal(native.records.length,111);assert.equal(native.support_records.length,3);assert.equal(native.budget,2e-13);
const wasmPath=opts['--wasm'],binaryPath=wasmPath.replace(/\.m?js$/,'.wasm');assert.notEqual(wasmPath,binaryPath);
const artifacts=[{path:wasmPath,sha256:hash(wasmPath)},{path:binaryPath,sha256:hash(binaryPath)}];
const module=await(await import(pathToFileURL(wasmPath))).default();
const transport=opts['--output']+'.transport.jsonl';writeFileSync(transport,'');
function rawCall(name,types,args){const raw=module.ccall(name,'string',types,args);appendFileSync(transport,JSON.stringify({name,arguments:args,response_text:raw})+'\n');return JSON.parse(raw);}
const description=rawCall('atlas_describe',[],[]);assert.equal(description.sha256,native.catalogue_hash);assert.equal(description.models.length,1);assert.deepEqual(description.models[0],native.model_definition);assert.deepEqual(Object.keys(description.models[0].parameters),native.parameter_order);
const finite=v=>typeof v==='number'&&Number.isFinite(v);
function validate(r,w,success){assert.deepEqual(Object.keys(r).sort(),['ok','model','catalogue_hash','parameters','state','increment','values','message'].sort());assert.equal(r.ok,success);assert.equal(r.catalogue_hash,native.catalogue_hash);assert.equal(r.model,w.model);for(const k of ['parameters','state','increment']){assert.ok(Array.isArray(r[k])&&r[k].every(finite));assert.deepEqual(r[k],w[k]);}assert.equal(r.message,success?'':'unsupported research rate request');if(success)assert.ok(Array.isArray(r.values)&&r.values.length===7&&r.values.every(finite));else assert.equal(r.values,null);}
const call=w=>rawCall('atlas_barodesy_rate',['string','string','string','string'],[w.model,w.parameters.join(','),w.state.join(','),w.increment.join(',')]);
const report={...structuredClone(native),backend:'wasm',artifacts,native_report_sha256:hash(opts['--native-report']),native_report_path:opts['--native-report'],records:[],support_records:[],invalid_records:[]};delete report.assessment;
const save=()=>writeFileSync(opts['--output'],JSON.stringify(report,null,2)+'\n');save();let parity=0;
for(const key of ['records','support_records'])for(const source of native[key]){const row={id:source.id,request:structuredClone(source.request)};report[key].push(row);save();row.response=call(row.request);save();validate(row.response,row.request,true);const e=Math.hypot(...row.response.values.map((x,i)=>x-source.response.values[i]))/Math.max(1,Math.hypot(...source.response.values));assert.ok(e<=2e-13);parity=Math.max(parity,e);}
const control=report.records[0];
for(const source of native.invalid_records){const row={id:source.id,request:structuredClone(source.request)};report.invalid_records.push(row);save();row.response=call(row.request);save();validate(row.response,row.request,false);row.recovery=call(control.request);save();validate(row.recovery,control.request,true);assert.deepEqual(row.recovery,control.response);}
for(const a of artifacts)assert.equal(hash(a.path),a.sha256);report.maximum_native_parity=parity;save();
console.log(JSON.stringify({rates:report.records.length,support:report.support_records.length,invalids:report.invalid_records.length,maximum_native_parity:parity,AD_validated:false,next:'Run Python fresh-reference assessment; this collector is not independent numerical acceptance.'}));
