import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {setupKelvinVoigtLaboratory} from '../web/kelvin-voigt-laboratory.mjs';
import {defaults,modelId,modelSha256,solver,request} from '../web/kelvin-voigt-contract.mjs';
import {createLaboratoryControllerRouter} from '../web/laboratory-controller-router.mjs';
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:'synthetic-transport-only',component_sha256:{'kelvin-voigt-contract.mjs':'fixture'}};
// No material computation: this is deliberately a synthetic transport/DOM fixture.
function result(c){return {ok:true,catalogue_hash:identity.catalogue_hash,model:modelId,units:'SI',schema_version:'0.2',start_time:c.start,parameters:c.parameters,initial:c.initial,initial_strain:c.initial,initial_strain_rate:c.initialRates,solver,points:Array.from({length:c.samples+2},(_,i)=>({time:i<2?c.start:c.start+c.duration*(i-1)/c.samples,side:i===1?'right':'left',segment:i===0?-1:0,state:[...c.initial],strain:[...c.initial],strain_rate:i===0?[...c.initialRates]:i===1&&c.mode==='creep'?Array(6).fill(null):Array(6).fill(0),observables:[1,2,3,4,5,6]}))};}
function harness(){
 const saved=Object.fromEntries(['document','Option','Worker','fetch','setTimeout','clearTimeout'].map(k=>[k,globalThis[k]])),nodes=new Map(),workers=[],plots=[],timers=new Map();let tick=0;
 class Node{constructor(){this.children=[];this.options=[];this.listeners={};this.value='';this.hidden=false;this.disabled=false;this.selectedIndex=0;}set innerHTML(html){this.html=html;for(const m of html.matchAll(/\bid="([^"]+)"/g)){const n=new Node();n.id=m[1];nodes.set(n.id,n);}}get innerHTML(){return this.html;}append(n){this.children.push(n);this.options.push(n);}after(n){nodes.set(n.id,n);}replaceChildren(){this.children=[];}addEventListener(k,fn){this.listeners[k]=fn;}scrollIntoView(){}click(){this.onclick?.();}}
 for(const id of ['model','model-description','model-family','model-status','model-sources','import-run'])nodes.set(id,new Node());const ordinary=new Node(),links=new Node();
 globalThis.document={getElementById:id=>nodes.get(id),querySelector:s=>s.includes('lab-layout')?ordinary:links,createElement:()=>new Node()};globalThis.Option=class{constructor(text,value){this.text=text;this.value=value;}};
 globalThis.Worker=class{constructor(url,options){this.url=url;this.options=options;workers.push(this);}postMessage(data){this.sent=structuredClone(data);}terminate(){this.terminated=true;}};
 globalThis.fetch=async()=>({ok:true,json:async()=>structuredClone(identity)});globalThis.setTimeout=cb=>{const id=++tick;timers.set(id,cb);return id;};globalThis.clearTimeout=id=>timers.delete(id);
 const ui=setupKelvinVoigtLaboratory({chart:(...args)=>plots.push(args)}),$=id=>nodes.get('kelvin-voigt-'+id);
 return {ui,$,nodes,ordinary,workers,plots,timers,reply(w=workers.at(-1),r=result(w.sent.controls)){w.onmessage({data:{id:w.sent.id,identity,args:request(w.sent.controls,identity),result:r}});},restore(){ui.select(null);for(const [k,v]of Object.entries(saved))if(v===undefined)delete globalThis[k];else globalThis[k]=v;}};
}
test('actual panel carries every six-component control and renders full state/stress plus six plot choices',()=>{
 const h=harness();try{h.ui.select(modelId,{auto:false});assert(h.ordinary.hidden);for(const key of ['initial','initialRates','rates','parameters'])assert.deepEqual(JSON.parse(h.$(key).value),defaults[key]);h.ui.run();assert.deepEqual(h.workers[0].sent.controls,defaults);h.reply();assert.equal(h.plots.length,2);assert.equal(h.$('state').children.length,defaults.samples+3);assert.equal(h.$('state').children[0].children.length,14);assert(!h.$('export').disabled);for(let i=0;i<6;i++){h.$('component').selectedIndex=i;h.$('component').onchange();assert.equal(h.plots.at(-2)[3][0][1],(i+1)/1000);}assert.match(h.$('laboratory').innerHTML,/no exponential|does not cause exponential/);assert.match(h.$('laboratory').innerHTML,/Eq3-36/);}finally{h.restore();}
});
test('latest request, reset and outgoing selection reject stale callbacks and clear export',()=>{
 const h=harness();try{h.ui.select(modelId);const first=h.workers[0];h.ui.run();const second=h.workers[1];assert(first.terminated);h.reply(first);assert(h.$('export').disabled);h.reply(second);assert(!h.$('export').disabled);h.$('reset').onclick();const reset=h.workers[2];assert(h.$('export').disabled);h.reply(second);assert(h.$('export').disabled);h.ui.select(null);assert(reset.terminated);h.reply(reset);assert(h.$('export').disabled);assert(!h.ordinary.hidden);assert(h.$('laboratory').hidden);assert.equal(h.ui.showEquations(),false);assert.equal(h.timers.size,0);}finally{h.restore();}
});
test('invalid input, worker error and timeout recover with fresh valid runs',()=>{
 const h=harness();try{h.ui.select(modelId,{auto:false});h.$('initialRates').value='[0]';h.ui.run();assert.equal(h.workers.length,0);assert.match(h.$('status').textContent,/Invalid input/);h.$('reset').onclick();let w=h.workers.at(-1);w.onmessage({data:{id:w.sent.id,error:'synthetic failure'}});assert.match(h.$('status').textContent,/Run failed/);assert(w.terminated);h.ui.run();w=h.workers.at(-1);[...h.timers.values()][0]();assert(w.terminated);assert.match(h.$('status').textContent,/Time limit/);h.ui.run();h.reply();assert(!h.$('export').disabled);assert.equal(h.timers.size,0);}finally{h.restore();}
});
test('verified import replays full saved output; finite tampering fails and stale file read cannot reactivate',async()=>{
 const h=harness();try{h.ui.select(modelId,{auto:false});const file=h.$('file'),c=structuredClone(defaults),doc={kind:'atlas-kelvin-voigt-laboratory-v1',controls:c,provenance:identity,request:{function:'atlas_run_schedule',args:request(c,identity)},result:result(c)};
 async function load(d){const text=JSON.stringify(d);file.files=[{size:text.length,text:async()=>text}];await file.onchange();}
 await load(doc);assert.equal(h.workers.length,1);assert(h.$('export').disabled);h.reply();assert(!h.$('export').disabled);
 const changed=structuredClone(doc);changed.result.points[3].observables[5]+=1;await load(changed);h.reply();assert(h.$('export').disabled);assert.match(h.$('status').textContent,/differs/);
 let finish;const text=JSON.stringify(doc);file.files=[{size:text.length,text:()=>new Promise(r=>finish=r)}];const pending=file.onchange();h.ui.select(null);const count=h.workers.length;finish(text);await pending;assert.equal(h.workers.length,count);assert(h.$('laboratory').hidden);assert(h.$('export').disabled);
 }finally{h.restore();}
});
test('shared controller router deactivates outgoing Kelvin before another timed profile',()=>{
 const h=harness(),events=[];try{const other={modelId:'other-test-profile',active:false,select(id){events.push('other:'+id);this.active=id===this.modelId;return this.active;},run(){},showEquations(){return this.active;}};const router=createLaboratoryControllerRouter([h.ui,other]);assert(router.supports(modelId));router.select(modelId);const w=h.workers.at(-1);assert(router.active);router.select(other.modelId);assert(w.terminated);assert(!h.ui.active);h.reply(w);assert(h.$('export').disabled);router.select(modelId);assert(!other.active);assert(h.ui.active);router.select(false);assert(!router.active);}finally{h.restore();}
});
test('coordinator release hook includes Kelvin in timed router and preserves actual ordinary async guard',()=>{
 const path=process.env.KELVIN_RELEASE_APP||new URL('../web/app.js',import.meta.url);const source=readFileSync(path,'utf8');
 assert.match(source,/setupKelvinVoigtLaboratory\(\{chart,cancelOrdinary:/);assert.match(source,/timedView=createLaboratoryControllerRouter\(/);const guard=source.match(/^function specialLaboratoryActive\(\).*$/m)[0];for(const active of [true,false])assert.equal(vm.runInNewContext(guard+';specialLaboratoryActive();',{j2View:null,timedView:{active}}),active);
 for(const name of ['renderCharts','matchExperiment']){const text=source.slice(source.indexOf('function '+name+'()'));assert.match(text.slice(0,110),/if\(specialLaboratoryActive\(\)\)return;/);}
 assert.match(source,/if\(data.id!==activeId\|\|specialLaboratoryActive\(\)\)return/);assert.match(source,/requested!==sequence\|\|specialLaboratoryActive\(\)/);assert.match(source,/revision===experimentLoadSequence&&!specialLaboratoryActive\(\)/);
});
test('synchronous Worker construction and postMessage faults clean up and recover on valid run',()=>{
 for(const fault of ['constructor','postMessage']){
  const h=harness(),NormalWorker=globalThis.Worker;try{
   h.ui.select(modelId,{auto:false});let broken;
   globalThis.Worker=fault==='constructor'?class{constructor(){throw Error('synthetic constructor fault');}}:class{constructor(){broken=this;}postMessage(){throw Error('synthetic postMessage fault');}terminate(){this.terminated=true;}};
   assert.doesNotThrow(()=>h.ui.run());assert.match(h.$('status').textContent,new RegExp('Run failed: synthetic '+fault+' fault'));assert(h.$('export').disabled);assert(!h.$('run').disabled);assert.equal(h.timers.size,0);if(broken)assert(broken.terminated);
   globalThis.Worker=NormalWorker;h.ui.run();h.reply();assert(!h.$('export').disabled);assert.match(h.$('status').textContent,/Completed/);assert.equal(h.timers.size,0);
  }finally{globalThis.Worker=NormalWorker;h.restore();}
 }
});
