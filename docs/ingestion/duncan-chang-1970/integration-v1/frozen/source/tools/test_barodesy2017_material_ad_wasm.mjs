// Persistent C ABI collection: retain raw/partial evidence before acceptance.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const o={};for(let i=2;i<process.argv.length;i+=2){const k=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(k)&&process.argv[i+1]&&!(k in o));o[k]=resolve(process.argv[i+1]);}for(const k of ['--native-report','--wasm','--output'])assert.ok(o[k]);
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const native=JSON.parse(readFileSync(o['--native-report']));assert.equal(native.version,'barodesy2017-material-ad-study-v1');assert.equal(native.backend,'native');assert.equal(native.records.length,21);
const wasm=o['--wasm'],binary=wasm.replace(/\.js$/,'.wasm');assert.notEqual(wasm,binary);const artifacts=[{path:wasm,sha256:hash(wasm)},{path:binary,sha256:hash(binary)}];
const report=structuredClone(native);report.backend='wasm';report.artifacts=artifacts;report.records=[];report.invalid_records=[];report.collection_complete=false;report.native_report_path=o['--native-report'];report.native_report_sha256=hash(o['--native-report']);report.maximum_scaled_jacobian_native_parity=null;
const transport={version:'barodesy2017-material-ad-transport-v1',backend:'wasm',artifacts,complete:false,calls:[]};
const save=()=>{writeFileSync(o['--output'],JSON.stringify(report,null,2)+'\n');writeFileSync(o['--output']+'.transport.json',JSON.stringify(transport,null,2)+'\n');};save();
const finite=x=>typeof x==='number'&&Number.isFinite(x);
function validate(r,w,ok){
 assert.deepEqual(Object.keys(r).sort(),['ok','model','catalogue_hash','parameters','state','increment','values','message','jacobian','columns'].sort());assert.equal(r.ok,ok);assert.equal(r.model,w.model);assert.equal(r.catalogue_hash,native.catalogue_hash);assert.deepEqual(r.columns,native.columns);
 for(const k of ['parameters','state','increment']){assert.ok(Array.isArray(r[k])&&r[k].every(finite));assert.deepEqual(r[k],w[k]);}
 assert.equal(r.message,ok?'':'unsupported regular material AD request');
 if(ok){assert.ok(Array.isArray(r.values)&&r.values.length===7&&r.values.every(finite));assert.ok(Array.isArray(r.jacobian)&&r.jacobian.length===7);for(const row of r.jacobian)assert.ok(Array.isArray(row)&&row.length===13&&row.every(finite));}else{assert.equal(r.values,null);assert.equal(r.jacobian,null);}
}
try{
 const module=await(await import(pathToFileURL(wasm))).default();
 function invoke(name,types,args){const c={name,arguments:args};transport.calls.push(c);try{c.raw=module.ccall(name,'string',types,args);save();return JSON.parse(c.raw);}catch(e){c.error=String(e);save();throw e;}}
 const desc=invoke('atlas_describe',[],[]);assert.equal(desc.sha256,native.catalogue_hash);assert.deepEqual(desc.models,[native.model_definition]);assert.deepEqual(Object.keys(desc.models[0].parameters),native.parameter_order);
 const call=w=>invoke('atlas_barodesy_material_ad',['string','string','string','string'],[w.model,w.parameters.join(','),w.state.join(','),w.increment.join(',')]);let parity=0;
 for(const source of native.records){const row=structuredClone(source);row.response=call(row.request);row.metrics=null;report.records.push(row);save();validate(row.response,row.request,true);const previous=source.response,scale=Math.max(1,Math.hypot(...previous.values));assert.ok(Math.hypot(...row.response.values.map((v,i)=>v-previous.values[i]))/scale<=2e-13);for(let k=0;k<13;k++){const s=row.reference.state_loading_scales[k],a=row.response.jacobian.map(r=>r[k]*s),b=previous.jacobian.map(r=>r[k]*s);const e=Math.hypot(...a.map((v,i)=>v-b[i]))/Math.max(scale,Math.hypot(...b));assert.ok(e<=2e-12);parity=Math.max(parity,e);}}
 const control=report.records[0];for(const source of native.invalid_records){const row=structuredClone(source);row.response=call(row.request);row.recovery=null;report.invalid_records.push(row);save();validate(row.response,row.request,false);row.recovery=call(control.request);save();validate(row.recovery,control.request,true);assert.deepEqual(row.recovery,control.response);}
 for(const a of artifacts)assert.equal(hash(a.path),a.sha256);report.maximum_scaled_jacobian_native_parity=parity;report.collection_complete=true;transport.complete=true;save();console.log(JSON.stringify({regular_cases:report.records.length,invalids:report.invalid_records.length,maximum_scaled_jacobian_native_parity:parity,independent_verification_required:true}));
}catch(e){transport.error=String(e);save();throw e;}
