import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const P=dirname(fileURLToPath(import.meta.url)),W=join(P,'evidence/source');
const {recordedWire,recordedSettings}=await import(pathToFileURL(join(W,'web/recorded.mjs')));
const {settingsCsv}=await import(pathToFileURL(join(W,'web/numerics.mjs')));
const read=p=>JSON.parse(readFileSync(join(P,p),'utf8')),text=p=>readFileSync(join(P,p),'utf8');
const old=text('original/tools/test_recorded.mjs'),proposed=text('proposed/tools/test_recorded.mjs');
const start='  // Preserve the retained legacy requests;',end='   const {controls,knots}=recordedWire(s)';
assert.equal(proposed.slice(0,proposed.indexOf(start))+ '  for(const {request:s} of [...retained,...restartRetained,{request:example}]){\n'+proposed.slice(proposed.indexOf(end)),old);
const retained=JSON.parse(gunzipSync(readFileSync(join(P,'evidence/catalogue/investigations/recorded-replay-api-v1/responses.json.gz'))));
const restartRetained=JSON.parse(gunzipSync(readFileSync(join(P,'evidence/catalogue/investigations/recorded-restarts-v1/responses.json.gz'))));
const example=read('evidence/protocols/recorded-dp-restart-run.json');
const all=[...retained,...restartRetained,{request:example}],before=JSON.stringify(all);
assert.equal(all.length,46);assert.equal(all.filter(x=>!x.request.initial).length,35);
const flat=m=>m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);
for(const row of read('evidence/default-equivalence.json')){
 const a=read('evidence/legacy/'+row.model+'.json'),b=read('evidence/current/'+row.model+'.json');
 assert.deepEqual(flat(a),row.flattened_initial);assert.deepEqual(flat(b),row.flattened_initial);
 assert.equal(createHash('sha256').update(readFileSync(join(P,'evidence/legacy/'+row.model+'.json'))).digest('hex'),row.legacy_sha256);
}
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
async function run(source,corrupt=false){
 let block=source.slice(source.indexOf("if(options['--wasm']||options['--native']){")+"if(options['--wasm']||options['--native']){".length,source.indexOf("\nif(options['--output'])"));
 block=block.slice(0,block.lastIndexOf('}')).replace("(await import(pathToFileURL(resolve(options['--wasm'])))).default",'mockFactory');
 const report={pairs:[]};let index=0,wires=0,current;
 const spawnSync=(exe,args)=>{const at=args.indexOf('--initial');assert.ok(at>=0,'explicit native initial');assert.ok(args[at+1]);const req=all[index].request;const defaults=read('evidence/default-equivalence.json').find(r=>r.model===req.model).flattened_initial;assert.deepEqual(args[at+1].split(',').map(Number),req.initial||defaults);wires++;current=structuredClone(all[index++].response||{ok:true,failed_knot:null,material_trials:1,attempted_substeps:2,finite_difference_probes:3});return {status:current.ok?0:1,stderr:'',stdout:JSON.stringify(current)};};
 const runRecorded=(engine,s)=>{assert.ok(s.initial?.length,'explicit Wasm initial');wires++;const r=structuredClone(current);if(corrupt)r.material_trials=123456789;return r;};
 await new AsyncFunction('assert','options','mockFactory','resolve','recordedWire','recordedSettings','settingsCsv','mkdtempSync','tmpdir','join','writeFileSync','rmSync','retained','restartRetained','example','spawnSync','runRecorded','report',block)(assert,{'--wasm':'mock','--native':'mock'},async()=>({}),resolve,recordedWire,recordedSettings,settingsCsv,mkdtempSync,tmpdir,join,writeFileSync,rmSync,retained,restartRetained,example,spawnSync,runRecorded,report);
 assert.equal(index,46);assert.equal(wires,92);assert.equal(report.pairs.length,46);return {pairs:index,explicit_wires:wires};
}
await assert.rejects(()=>run(old),/explicit native initial/);
const result=await run(proposed);await assert.rejects(()=>run(proposed,true));assert.equal(JSON.stringify(all),before);
console.log(JSON.stringify({status:'passed',...result,missing_requests_adapted:35,already_explicit:11,original_byte_reverse_proof:true,original_missing_wire_rejected:true,corrupted_response_rejected:true,retained_packets_unchanged:true,compiled_calls:0}));
