// Exact unchanged SLS view's run/select/invalidate; inert worker controls, no engine.
import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {createHash} from 'node:crypto';
const source=readFileSync(new URL('./source/web/sls-laboratory.mjs',import.meta.url),'utf8');
const freeze=JSON.parse(readFileSync(new URL('./source/ship-freeze.json',import.meta.url),'utf8'));
assert.equal(createHash('sha256').update(source).digest('hex'),freeze.files['web/sls-laboratory.mjs']);
const invalidate=source.slice(source.indexOf(' function invalidate('),source.indexOf('\n function render('));
const run=source.slice(source.indexOf(' function run('),source.indexOf('\n set(defaults);')).replaceAll('import.meta.url',"'file:///inert/sls-laboratory.mjs'");
const select=source.slice(source.indexOf(' function select('),source.indexOf('\n return {modelId'));
const execute=Function('assert','URL',`return function(callback){
 let active=true,worker=null,generation=0,last=null,timer=null;const modelId='sls',nodes=new Map(),workers=[],timers=[],events=[],ordinary={hidden:true},links={hidden:true},panel={hidden:false};
 const $=id=>{if(!nodes.has(id))nodes.set(id,{hidden:false,disabled:false,textContent:'',children:[],replaceChildren(){this.children=[];}});return nodes.get(id);};
 const clearTimeout=()=>events.push('clear');const setTimeout=f=>{timers.push(f);return 1;};
 const read=()=>({mode:'creep',duration:1,samples:1});const validateControls=x=>x;const chart=()=>events.push('chart');const render=()=>events.push('render');const verifyReplay=()=>{};const cancelOrdinary=()=>{};
 class Worker{constructor(){workers.push(this);this.terminated=false;}terminate(){this.terminated=true;events.push('terminate');}postMessage(m){this.request=m;}}
 ${invalidate}
 ${run}
 ${select}
 run();const old=workers[0],id=old.request.id;assert.ok(old&&timers[0]);
 assert.equal(select('j2'),false);assert.equal(active,false);assert.equal(old.terminated,true);
 // Incoming J2 dispatcher has now finalized workspace/header/export ownership.
 ordinary.hidden=links.hidden=true;$('import-run').hidden=true;$('model-description').textContent='J2';const publicExport={disabled:false};
 const snapshot=()=>JSON.stringify({nodes:[...nodes],events,ordinary,links,panel,publicExport,last,generation});const before=snapshot();
 const point={time:1,state:Array(12).fill(1),strain:Array(6).fill(2),strain_rate:Array(6).fill(3)};
 if(callback==='success')old.onmessage({data:{id,result:{points:[point]},identity:{},args:[]}});
 else if(callback==='messageError')old.onmessage({data:{id,error:'Late timed rejection'}});
 else if(callback==='workerError')old.onerror({message:'Late timed worker error'});else timers[0]();
 assert.equal(snapshot(),before);assert.equal(last,null);assert.equal($('sls-export').disabled,true);
 return {callback,workerTerminatedOnDeactivation:true,noLateMutation:true,noResultPublished:true};
}`)(assert,URL);
const cases=['success','messageError','workerError','timeout'].map(execute);
console.log(JSON.stringify({passed:true,source_sha256:freeze.files['web/sls-laboratory.mjs'],cases,engineCalls:0,compiledCalls:0,networkCalls:0,scope:'Exact committed timed-view lifecycle with inert workers and synthetic incoming-J2 header/visibility. Combined dispatch verified separately; no actual SLS simulation.'},null,2));
