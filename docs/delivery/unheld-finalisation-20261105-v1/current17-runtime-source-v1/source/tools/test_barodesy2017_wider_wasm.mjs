// Same-instance full seven-state path collection. Python independently assesses.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,appendFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};for(let i=2;i<process.argv.length;i+=2){const key=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(key)&&process.argv[i+1]&&!(key in options));options[key]=resolve(process.argv[i+1]);}
for(const key of['--native-report','--wasm','--output'])assert.ok(options[key],`${key} required`);
const native=JSON.parse(readFileSync(options['--native-report']));assert.equal(native.version,'barodesy2017-wider-integration-v1');assert.equal(native.backend,'native');assert.equal(native.records.length,48);assert.equal(native.records.reduce((n,g)=>n+g.calls.length,0),576);assert.equal(native.failure_probes.length,3);
const transport=options['--output'].replace(/\.json$/, '')+'.transport.jsonl';writeFileSync(transport,'');
const rawCall=(name,types,args,request)=>{
 let raw;try{raw=module.ccall(name,'string',types,args);}catch(error){appendFileSync(transport,JSON.stringify({backend:'wasm',name,types,args,request,raw:null,exception:String(error)})+'\n');throw error;}
 appendFileSync(transport,JSON.stringify({backend:'wasm',name,types,args,request,raw})+'\n');return JSON.parse(raw);
};
const module=await(await import(pathToFileURL(options['--wasm']))).default();
const descriptor=rawCall('atlas_describe',[],[],{mode:'describe'});writeFileSync(options['--output']+'.descriptor.raw.json',JSON.stringify(descriptor)+'\n');assert.deepEqual(descriptor.models,[native.model_definition]);assert.equal(descriptor.sha256,native.catalogue_hash);
const csv=x=>x.map(v=>{assert.equal(typeof v,'number');assert.ok(Number.isFinite(v));return v.toString();}).join(',');
const call=r=>rawCall('atlas_integrate_with_settings',['string','string','string','string','string'],[r.model,csv(r.parameters),csv(r.initial),csv(r.strain),csv(r.settings)],r);
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const report={...native,backend:'wasm',runtime_descriptor:descriptor,records:[],failure_probes:[],native_report_sha256:sha(options['--native-report']),wasm_loader_sha256:sha(options['--wasm']),wasm_binary_sha256:sha(options['--wasm'].replace(/\.m?js$/,'.wasm'))};delete report.native_sha256;delete report.assessment;
const save=()=>writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
for(const group of native.records){
 const out={case:group.case,tolerance:group.tolerance,partitions:group.partitions,calls:[]};report.records.push(out);let state=structuredClone(group.calls[0].request.initial);
 for(const recorded of group.calls){
  const request=structuredClone(recorded.request);request.initial=structuredClone(state);const response=call(request);out.calls.push({request,response});save();assert.equal(response.ok,true);assert.ok(Array.isArray(response.state)&&response.state.length===7&&response.state.every(x=>typeof x==='number'&&Number.isFinite(x)));state=structuredClone(response.state);
 }
}
const controlGroup=report.records.find(g=>g.case==='london-nonproportional'&&g.tolerance===1e-8&&g.partitions===1);assert.ok(controlGroup&&controlGroup.calls.length===3);
report.transaction_prefix=structuredClone(controlGroup.calls.slice(0,2));report.recovery_control=structuredClone(controlGroup.calls[2]);save();
for(const kind of ['budget','domain','zero']){
 const request=structuredClone(report.recovery_control.request);
 if(kind==='budget')request.settings[4]=3;
 if(kind==='domain')request.strain=[.9,.9,.9,0,0,0];
 if(kind==='zero')request.strain=[0,0,0,0,0,0];
 const response=call(request),row={kind,request,response};report.failure_probes.push(row);save();
 const recoveryRequest=structuredClone(report.recovery_control.request);row.recovery={request:recoveryRequest,response:call(recoveryRequest)};save();assert.deepEqual(row.recovery,report.recovery_control);
}
report.persistent_recovery=true;report.transport_sha256=sha(transport);save();console.log('Saved48trajectories/576actual chainedWasmcalls plus3transaction/recovery probes. Run Python verifier with --native-report.');
