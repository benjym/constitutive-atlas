import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash,webcrypto} from 'node:crypto';
import {modelId,modelSha256,request,exportRun} from '../web/maxwell-atlas-contract.mjs';
import {runMaxwellSchedule,components} from '../web/maxwell-atlas-engine.mjs';
import {createMaxwellRunner} from '../web/maxwell-atlas-runner.mjs';
import {setupMaxwellLaboratory} from '../web/maxwell-laboratory.mjs';
const read=path=>readFileSync(new URL('../'+path,import.meta.url));
const row=JSON.parse(read('docs/ingestion/maxwell-itasca900/integration-v1/native-raw.json')).find(r=>r.id==='load-hold-reverse');
const result=JSON.parse(row.calls[0].stdout),keys=['schema_version','units','model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments','solver'];
const controls=Object.fromEntries(keys.map(k=>[k,structuredClone(result[k])]));
const sha=b=>createHash('sha256').update(b).digest('hex');
const encode=o=>Buffer.from(JSON.stringify(o));
function packageFixture() {
 const catalogue={sha256:result.catalogue_hash,models:[JSON.parse(read('models/research/maxwell/'+modelId+'.json'))]},assets=new Map();
 const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:result.catalogue_hash,release_revision:'mocked-package-transport-only',component_sha256:{}};
 function put(path,bytes,key){assets.set(path,Buffer.from(bytes));if(key)identity[key]=sha(bytes);}
 put('engine-maxwell/maxwell.mjs',Buffer.from('verified module fixture'),'module_sha256');put('engine-maxwell/maxwell.wasm',Buffer.from('verified Wasm fixture'),'wasm_sha256');
 put('engine-maxwell/models.json',encode(catalogue),'catalogue_file_sha256');put('engine-maxwell/'+modelId+'.json',read('models/research/maxwell/'+modelId+'.json'));
 put('engine-maxwell/approval.json',read('docs/admission/maxwell-agent-v2/approval.json'),'approval_sha256');put('engine-maxwell/review.json',read('catalogue/agent-reviews/maxwell-agent-v2.json'),'review_sha256');put('engine-maxwell/review.html',Buffer.from('review fixture'),'review_html_sha256');
 for(const name of components){put(name,read('web/'+name));identity.component_sha256[name]=sha(assets.get(name));}
 const requests=[],calls=[],imported=[];
 const fetchAsset=async(url,options)=>{assert.equal(options.cache,'no-store');const path=url.pathname.replace('/atlas/','');requests.push(path);const b=path==='engine-maxwell/identity.json'?encode(identity):assets.get(path);return {ok:!!b,text:async()=>b.toString(),arrayBuffer:async()=>Uint8Array.from(b).buffer};};
 const importModule=async bytes=>{imported.push(Buffer.from(bytes));assert.deepEqual(Buffer.from(bytes),assets.get('engine-maxwell/maxwell.mjs'));return async options=>{await new Promise(resolve=>options.instantiateWasm({fixture:'imports'},resolve));return {ccall(name,returnType,types,args){calls.push({name,returnType,types,args});return JSON.stringify(name==='atlas_describe'?catalogue:result);}};};};
 return {identity,assets,requests,calls,imported,put,catalogue,options:{fetchAsset,cryptoApi:webcrypto,importModule,instantiateBinary:async(bytes,imports)=>{assert.deepEqual(Buffer.from(bytes),assets.get('engine-maxwell/maxwell.wasm'));assert.deepEqual(imports,{fixture:'imports'});return {instance:{fixture:'instance'},module:{fixture:'module'}};},base:new URL('https://test.invalid/atlas/')}};
}
function harness(){const workers=[],events=[],timers=new Map();let next=0;const runner=createMaxwellRunner({createWorker(){const worker={terminated:false,postMessage(data){this.sent=data;},terminate(){this.terminated=true;}};workers.push(worker);return worker;},notify:event=>events.push(event),setTimer(cb){const id=++next;timers.set(id,cb);return id;},clearTimer:id=>timers.delete(id)});return {runner,workers,events,timers};}
const reply=(worker,identity=packageFixture().identity,r=result)=>worker.onmessage({data:{id:worker.sent.id,identity,result:structuredClone(r),args:request(controls,identity)}});
test('verified assets reach mocked factory exactly once with complete ABI and no unchecked module refetch',async()=>{
 const p=packageFixture(),out=await runMaxwellSchedule(controls,p.options);assert.deepEqual(out.result,result);assert.deepEqual(out.args,request(controls,p.identity));assert.equal(p.imported.length,1);assert.deepEqual(p.calls.map(c=>c.name),['atlas_describe','atlas_run_schedule']);assert.equal(p.requests.filter(n=>n==='engine-maxwell/maxwell.mjs').length,1);assert.equal(p.requests.length,8+components.length);
});
test('bad asset hashes, missing components/files and wrong model stop before factory/material call',async()=>{
 for(const mutate of [p=>p.assets.set('engine-maxwell/maxwell.mjs',Buffer.from('changed')),p=>p.assets.delete('engine-maxwell/maxwell.wasm'),p=>delete p.identity.component_sha256['maxwell-atlas-worker.mjs'],p=>p.identity.component_sha256['maxwell-atlas-worker.mjs']='wrong',p=>p.identity.model_sha256='0'.repeat(64),p=>p.assets.set('maxwell-laboratory.mjs',Buffer.from('changed'))]){const p=packageFixture();mutate(p);await assert.rejects(runMaxwellSchedule(controls,p.options));assert.equal(p.imported.length,0);assert.equal(p.calls.length,0);}
});
test('review/approval/catalogue semantic mismatches reject even when their new bytes are hashed',async()=>{
 for(const [path,key,mutate]of [['engine-maxwell/approval.json','approval_sha256',x=>x.definition.sha256='0'.repeat(64)],['engine-maxwell/review.json','review_sha256',x=>x.status='pending'],['engine-maxwell/models.json','catalogue_file_sha256',x=>x.models.push({id:'other'})],['engine-maxwell/models.json','catalogue_file_sha256',x=>x.models[0].description+=' altered model metadata']]){const p=packageFixture(),obj=JSON.parse(p.assets.get(path));mutate(obj);p.put(path,encode(obj),key);if(path.includes('review.json')){const a=JSON.parse(p.assets.get('engine-maxwell/approval.json'));a.review.sha256=p.identity.review_sha256;p.put('engine-maxwell/approval.json',encode(a),'approval_sha256');}await assert.rejects(runMaxwellSchedule(controls,p.options));assert.equal(p.calls.length,0);}
 const p=packageFixture();p.options.importModule=async()=>async options=>{await new Promise(resolve=>options.instantiateWasm({fixture:'imports'},resolve));return {ccall:()=>JSON.stringify({...p.catalogue,sha256:'0'.repeat(64)})};};await assert.rejects(runMaxwellSchedule(controls,p.options),/embedded catalogue/);
});
test('invalid input rejects before any engine acquisition',async()=>{const p=packageFixture();await assert.rejects(runMaxwellSchedule({...controls,initial:[]},p.options));assert.equal(p.requests.length,0);});
test('latest request alone can complete; cancellation clears worker/timer/export and stale messages',()=>{
 const h=harness();h.runner.run(controls);const first=h.workers[0];h.runner.run(controls);const second=h.workers[1];assert(first.terminated);reply(first);assert.equal(h.runner.last,null);reply(second);assert(h.runner.last);assert.equal(h.timers.size,0);assert(second.terminated);const count=h.events.length;reply(second);assert.equal(h.events.length,count);h.runner.cancel();assert.equal(h.runner.last,null);
});
test('invalid input, timeout and engine error recover with a subsequent valid run',()=>{
 const h=harness();h.runner.run({...controls,parameters:[]});assert.equal(h.workers.length,0);assert.equal(h.events.at(-1).state,'error');h.runner.run(controls);const timed=h.workers.at(-1);[...h.timers.values()][0]();assert(timed.terminated);assert.equal(h.runner.last,null);h.runner.run(controls);h.workers.at(-1).onmessage({data:{id:h.workers.at(-1).sent.id,error:'saved failure'}});assert.equal(h.events.at(-1).state,'error');h.runner.run(controls);reply(h.workers.at(-1));assert.equal(h.events.at(-1).state,'complete');const saved=h.runner.last;saved.result.points[0].state[0]=0;assert.notEqual(h.runner.last.result.points[0].state[0],0);
});
test('main thread revalidates result/args and exact imported provenance/replay',()=>{
 const identity=packageFixture().identity;
 for(const mutate of [data=>data.result.points.pop(),data=>data.args[5]='bad']){const h=harness();h.runner.run(controls);const w=h.workers[0],data={id:w.sent.id,identity,result:structuredClone(result),args:request(controls,identity)};mutate(data);w.onmessage({data});assert.equal(h.runner.last,null);assert.equal(h.events.at(-1).state,'error');}
 for(const mutate of [saved=>saved.provenance.release_revision='other',saved=>saved.result.points[2].strain[5]+=1e-9]){const saved=exportRun(controls,result,identity);mutate(saved);const h=harness();h.runner.run(controls,{expected:saved});reply(h.workers[0],identity);assert.equal(h.runner.last,null);assert.equal(h.events.at(-1).state,'error');}
 const h=harness();h.runner.run(controls,{expected:exportRun(controls,result,identity)});reply(h.workers[0],identity);assert.equal(h.events.at(-1).state,'complete');
});
// A small DOM adapter exercises actual controller handlers; real-browser qualification is separate.
function domFixture(){const nodes=new Map();class Node{constructor(tag='div'){this.tag=tag;this.children=[];this.options=[];this._value='';this.hidden=false;this.disabled=false;this.selectedIndex=0;this.listeners={};}set value(v){this._value=String(v);}get value(){return this._value;}set innerHTML(html){this.html=html;for(const m of html.matchAll(/<([a-z]+)\b[^>]*\bid="([^"]+)"[^>]*>/g)){const n=new Node(m[1]);n.id=m[2];nodes.set(n.id,n);}nodes.get('maxwell-preset').value='relaxation';}get innerHTML(){return this.html;}append(n){this.children.push(n);if(n.value!==undefined)this.options.push(n);}after(n){nodes.set(n.id,n);}replaceChildren(){this.children=[];}addEventListener(name,fn){this.listeners[name]=fn;}scrollIntoView(){}click(){this.onclick?.();}}
 for(const id of ['model','model-description','model-family','model-status','model-sources','import-run'])nodes.set(id,new Node());const ordinary=new Node(),links=new Node();globalThis.document={getElementById:id=>nodes.get(id),querySelector:selector=>selector.includes('lab-layout')?ordinary:links,createElement:tag=>new Node(tag)};globalThis.Option=class{constructor(text,value){this.text=text;this.value=value;}};return {nodes,ordinary,links,restore(){delete globalThis.document;delete globalThis.Option;}};}
test('main panel exposes four presets, complete table/source scope, reset and inactive cancellation',()=>{
 const dom=domFixture(),workers=[],plots=[];try{
 const ui=setupMaxwellLaboratory({chart:(...args)=>plots.push(args),createWorker:()=>{const w={postMessage(data){this.sent=data;},terminate(){this.terminated=true;}};workers.push(w);return w;}}),$=id=>dom.nodes.get('maxwell-'+id);
 assert.equal(ui.select(modelId,{auto:false}),true);assert(dom.ordinary.hidden);assert(!$('laboratory').hidden);assert.equal(workers.length,0);$('preset').value='load-hold-reverse';$('preset').onchange();ui.run();reply(workers.at(-1));assert.equal(plots.length,3);assert.equal($('state').children.length,result.points.length+1);assert(!$('export').disabled);assert.match($('laboratory').innerHTML,/https:\/\/docs.itascacg.com/);assert.match($('laboratory').innerHTML,/No calibration or experimental validation/);
 $('initial').value='[]';ui.run();assert($('export').disabled);assert.match($('status').textContent,/Invalid input/);$('reset').onclick();assert.equal(workers.length,2);ui.select(null);assert(workers.at(-1).terminated);assert(!dom.ordinary.hidden);assert($('laboratory').hidden);assert($('export').disabled);assert.equal(ui.showEquations(),false);
 }finally{dom.restore();}
});
test('all four main-panel presets retain complete explicit source histories',()=>{
 const dom=domFixture(),workers=[];try{
 const ui=setupMaxwellLaboratory({chart:()=>{},createWorker:()=>{const w={postMessage(data){this.sent=data;},terminate(){}};workers.push(w);return w;}});ui.select(modelId,{auto:false});
 for(const name of ['relaxation','creep','oedometer','load-hold-reverse']){const select=dom.nodes.get('maxwell-preset');select.value=name;select.onchange();ui.run();const source=JSON.parse(read('examples/maxwell/'+name+'.json'));assert.deepEqual(workers.at(-1).sent.controls,{...source,solver:controls.solver});}ui.select(null);
 }finally{dom.restore();}
});
test('asynchronous import cannot reactivate a deselected panel; valid import binds replay before export',async()=>{
 const dom=domFixture(),workers=[],identity=packageFixture().identity,oldFetch=globalThis.fetch;
 globalThis.fetch=async()=>({ok:true,text:async()=>JSON.stringify(identity)});
 try{
 const ui=setupMaxwellLaboratory({chart:()=>{},createWorker:()=>{const w={postMessage(data){this.sent=data;},terminate(){this.terminated=true;}};workers.push(w);return w;}});ui.select(modelId,{auto:false});
 const file=dom.nodes.get('maxwell-file'),saved=JSON.stringify(exportRun(controls,result,identity));let finish;
 file.value='pending.json';file.files=[{size:saved.length,text:()=>new Promise(resolve=>finish=resolve)}];const pending=file.onchange();ui.select(null);finish(saved);await pending;assert.equal(workers.length,0);assert(dom.nodes.get('maxwell-export').disabled);
 ui.select(modelId,{auto:false});file.value='valid.json';file.files=[{size:saved.length,text:async()=>saved}];await file.onchange();assert.equal(workers.length,1);assert.equal(file.value,'');assert(dom.nodes.get('maxwell-export').disabled);reply(workers[0],identity);assert(!dom.nodes.get('maxwell-export').disabled);ui.select(null);
 }finally{globalThis.fetch=oldFetch;dom.restore();}
});
test('worker acquisition and postMessage failures leave a recoverable error without timers',()=>{
 for(const createWorker of [()=>{throw Error('worker blocked');},()=>({terminate(){},postMessage(){throw Error('message blocked');}})]){const events=[],timers=new Map();const runner=createMaxwellRunner({createWorker,notify:e=>events.push(e),setTimer:cb=>{timers.set(1,cb);return 1;},clearTimer:id=>timers.delete(id)});runner.run(controls);assert.equal(events.at(-1).state,'error');assert.equal(runner.last,null);assert.equal(timers.size,0);}
});

test('verified Wasm hook propagates asynchronous failure and rejects a factory that ignores the hook',async()=>{
 const failed=packageFixture();failed.options.instantiateBinary=async()=>{throw Error('mocked invalid Wasm');};await assert.rejects(runMaxwellSchedule(controls,failed.options),/mocked invalid Wasm/);assert.equal(failed.calls.length,0);
 const ignored=packageFixture();ignored.options.importModule=async()=>async()=>({ccall(){throw Error('must not call material');}});await assert.rejects(runMaxwellSchedule(controls,ignored.options),/did not complete verified Wasm/);
 const fallback=packageFixture();fallback.options.importModule=async()=>async options=>options.locateFile('maxwell.wasm');await assert.rejects(runMaxwellSchedule(controls,fallback.options),/Unverified engine file/);
});

test('premature factory completion cannot invoke an uninitialized material engine',async()=>{
 const p=packageFixture();p.options.instantiateBinary=()=>new Promise(()=>{});p.options.importModule=async()=>async options=>{options.instantiateWasm({fixture:'imports'},()=>{});return {ccall(){throw Error('must not call material');}};};await assert.rejects(runMaxwellSchedule(controls,p.options),/did not complete verified Wasm/);
});
