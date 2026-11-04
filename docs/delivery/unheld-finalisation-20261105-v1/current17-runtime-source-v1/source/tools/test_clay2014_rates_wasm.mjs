// Collect opaque real-C-ABI responses before parsing, in one module instance.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const options={};for(let i=2;i<process.argv.length;i+=2){const key=process.argv[i];assert.ok(['--native-report','--wasm','--output'].includes(key)&&process.argv[i+1]&&!(key in options));options[key]=resolve(process.argv[i+1]);}
for(const key of ['--native-report','--wasm','--output'])assert.ok(options[key],key+' required');
const nativeBytes=readFileSync(options['--native-report']),nativeBefore=createHash('sha256').update(nativeBytes).digest('hex');
const native=JSON.parse(nativeBytes);assert.equal(native.version,'clay2014-instantaneous-rates-v1');assert.equal(native.backend,'native');
const transport=options['--output'].replace(/\.json$/,'')+'.transport.json', rows=[];
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const wasmBinary=options['--wasm'].replace(/\.m?js$/,'.wasm'),loaderBefore=sha(options['--wasm']),binaryBefore=sha(wasmBinary);
const module=await(await import(pathToFileURL(options['--wasm']))).default();
function rawCall(name,types,args){
 let raw;try{raw=module.ccall(name,'string',types,args);}catch(error){rows.push({name,types,args,raw:null,exception:String(error)});writeFileSync(transport,JSON.stringify(rows)+'\n');throw error;}
 rows.push({name,types,args,raw});writeFileSync(transport,JSON.stringify(rows)+'\n');return JSON.parse(raw);
}
const report={...native,backend:'wasm',calls:[],persistent_instance:false,native_report_sha256:nativeBefore,wasm_loader_sha256:loaderBefore,wasm_binary_sha256:binaryBefore};delete report.native_sha256;delete report.assessment;
const save=()=>writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
report.descriptor=rawCall('atlas_describe',[],[]);save();
const csv=xs=>xs.map(x=>{assert.equal(typeof x,'number');assert.ok(Number.isFinite(x));return x.toString();}).join(',');
for(const call of native.calls){const r=structuredClone(call.request);const response=rawCall('atlas_research_rate',['string','string','string','string'],[r.model,csv(r.parameters),csv(r.state),csv(r.increment)]);report.calls.push({request:r,response});save();}
assert.equal(sha(options['--native-report']),nativeBefore,'native report changed during collection');assert.equal(sha(options['--wasm']),loaderBefore,'loader changed during collection');assert.equal(sha(wasmBinary),binaryBefore,'Wasm changed during collection');
report.persistent_instance=true;report.transport_sha256=sha(transport);save();console.log('Collected persistent Wasm rates and invalid/recovery calls; Python assessment required.');
