// Opaque persistent C-ABI collection only; Python independently audits both backends.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,appendFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname,relative,isAbsolute} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const options={};
for(let i=2;i<process.argv.length;i+=2){const key=process.argv[i];assert.ok(['--native-report','--native-transport','--wasm','--output'].includes(key)&&process.argv[i+1]&&!(key in options));options[key]=resolve(process.argv[i+1]);}
for(const key of ['--native-report','--native-transport','--wasm','--output'])assert.ok(options[key],key+' required');
const shaBytes=b=>createHash('sha256').update(b).digest('hex');
const sha=p=>shaBytes(readFileSync(p));
const finite=x=>typeof x==='number'&&Number.isFinite(x);
// JSON numeric spelling is immaterial; Boolean aliases and nonfinite numbers are not.
function same(a,b){
 if(typeof a==='number'||typeof b==='number')return finite(a)&&finite(b)&&a===b;
 if(a===null||b===null||typeof a!=='object'||typeof b!=='object')return a===b;
 if(Array.isArray(a)!==Array.isArray(b))return false;
 if(Array.isArray(a))return a.length===b.length&&a.every((v,i)=>same(v,b[i]));
 const ak=Object.keys(a).sort(),bk=Object.keys(b).sort();return same(ak,bk)&&ak.every(k=>same(a[k],b[k]));
}
const reportBytes=readFileSync(options['--native-report']),nativeBefore=shaBytes(reportBytes);
const rawBytes=readFileSync(options['--native-transport']),nativeRawBefore=shaBytes(rawBytes);
const native=JSON.parse(reportBytes);
assert.equal(native.version,'clay2014-fixed-plane-integration-v1');assert.equal(native.backend,'native');
assert.equal(native.transport_sha256,nativeRawBefore,'explicit native raw companion');
assert.ok(Array.isArray(native.records)&&native.records.length===24);
assert.equal(native.records.reduce((n,g)=>n+g.calls.length,0),288);
assert.ok(Array.isArray(native.failure_probes)&&native.failure_probes.length===3);
const ownPath=fileURLToPath(import.meta.url),repo=resolve(dirname(ownPath),'..');
assert.equal(sha(ownPath),native.wasm_collector_sha256,'collector source receipt');
assert.ok(native.source_pins&&typeof native.source_pins==='object'&&!Array.isArray(native.source_pins));
const sourcePins=Object.entries(native.source_pins).map(([path,expected])=>{
 const full=resolve(repo,path),rel=relative(repo,full);assert.ok(!isAbsolute(path)&&!rel.startsWith('..')&&!isAbsolute(rel),'source pin path');
 assert.match(expected,/^[a-f0-9]{64}$/);assert.equal(sha(full),expected,'source receipt: '+path);return [full,expected];
});
const wasmBinary=options['--wasm'].replace(/\.m?js$/,'.wasm');assert.notEqual(wasmBinary,options['--wasm'],'Wasm loader extension');
const loaderBefore=sha(options['--wasm']),binaryBefore=sha(wasmBinary);
const transport=options['--output'].replace(/\.json$/,'')+'.transport.jsonl';
assert.ok(![options['--native-report'],options['--native-transport'],options['--wasm'],wasmBinary].includes(options['--output']));
assert.ok(![options['--native-report'],options['--native-transport'],options['--wasm'],wasmBinary,options['--output']].includes(transport));
assert.ok(!existsSync(options['--output'])&&!existsSync(transport)&&!existsSync(options['--output']+'.descriptor.raw.json'),'use fresh output paths; retained partial evidence is immutable');
mkdirSync(dirname(options['--output']),{recursive:true});writeFileSync(transport,'');
const report={...native,backend:'wasm',runtime_descriptor:null,records:[],failure_probes:[],persistent_recovery:false,native_report_sha256:nativeBefore,native_transport_sha256:nativeRawBefore,wasm_loader_sha256:loaderBefore,wasm_binary_sha256:binaryBefore};
delete report.native_sha256;delete report.assessment;delete report.transport_sha256;delete report.transaction_prefix;delete report.recovery_control;
const save=()=>writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');save();
const module=await(await import(pathToFileURL(options['--wasm']))).default();
let rawCount=0,lastRaw;
function rawCall(name,types,args,request){
 let raw;try{raw=module.ccall(name,'string',types,args);}catch(error){appendFileSync(transport,JSON.stringify({backend:'wasm',name,types,args,request,raw:null,exception:String(error)})+'\n');throw error;}
 appendFileSync(transport,JSON.stringify({backend:'wasm',name,types,args,request,raw})+'\n');rawCount++;lastRaw=raw;
 assert.equal(typeof raw,'string');return JSON.parse(raw);
}
report.runtime_descriptor=rawCall('atlas_describe',[],[],{mode:'describe'});save();
writeFileSync(options['--output']+'.descriptor.raw.json',lastRaw);
assert.ok(same(report.runtime_descriptor.models,[native.model_definition]),'compiled model definition');
assert.equal(report.runtime_descriptor.sha256,native.catalogue_hash,'compiled catalogue identity');
assert.ok(same(report.runtime_descriptor,native.runtime_descriptor),'native/Wasm descriptor identity');
const csv=xs=>{assert.ok(Array.isArray(xs));return xs.map(x=>{assert.ok(finite(x));return x.toString();}).join(',');};
const call=r=>rawCall('atlas_integrate_with_settings',['string','string','string','string','string'],[r.model,csv(r.parameters),csv(r.initial),csv(r.strain),csv(r.settings)],r);
for(const group of native.records){
 const out={case:group.case,tolerance:group.tolerance,partitions:group.partitions,calls:[]};report.records.push(out);
 assert.ok(group.calls.length>0);let state=structuredClone(group.calls[0].request.initial);
 for(const original of group.calls){
  const request=structuredClone(original.request);request.initial=structuredClone(state);
  const response=call(request);out.calls.push({request,response});save();
  assert.equal(response.ok,true);assert.ok(Array.isArray(response.state)&&response.state.length===7&&response.state.every(finite));state=structuredClone(response.state);
 }
}
const groups=report.records.filter(g=>g.case==='oblique-reversal'&&g.tolerance===1e-8&&g.partitions===1);
assert.equal(groups.length,1);assert.equal(groups[0].calls.length,3);
report.transaction_prefix=structuredClone(groups[0].calls.slice(0,2));report.recovery_control=structuredClone(groups[0].calls[2]);save();
for(const kind of ['budget','domain','zero']){
 const request=structuredClone(report.recovery_control.request);
 if(kind==='budget')request.settings[4]=3;
 if(kind==='domain')request.strain=[.9,.9,.9,0,0,0];
 if(kind==='zero')request.strain=[0,0,0,0,0,0];
 const response=call(request),row={kind,request,response};report.failure_probes.push(row);save();
 const recoveryRequest=structuredClone(report.recovery_control.request);row.recovery={request:recoveryRequest,response:call(recoveryRequest)};save();
 assert.ok(same(row.recovery,report.recovery_control),'identical same-parent recovery');
 assert.equal(response.ok,kind==='zero');assert.ok(same(response.state,request.initial),'failed/zero caller state unchanged');
}
assert.equal(rawCount,295,'descriptor +288 updates +6 probe/recovery calls');
assert.equal(sha(options['--native-report']),nativeBefore,'native report changed');assert.equal(sha(options['--native-transport']),nativeRawBefore,'native raw changed');
assert.equal(sha(options['--wasm']),loaderBefore,'loader changed');assert.equal(sha(wasmBinary),binaryBefore,'Wasm changed');
assert.equal(sha(ownPath),native.wasm_collector_sha256,'collector changed');for(const [path,expected]of sourcePins)assert.equal(sha(path),expected,'source changed: '+path);
report.persistent_recovery=true;report.transport_sha256=sha(transport);save();
console.log('Retained295 opaque persistent Wasm responses. Independently assess both reports and both explicit raw companions with Python.');
