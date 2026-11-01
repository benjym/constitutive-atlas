// Exact mixed-root continuations under inert worker/file/timer controls; no actual engine/network.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=readFileSync(new URL('./source/web/app.js',import.meta.url),'utf8');
const freeze=JSON.parse(readFileSync(new URL('./source/mixed-freeze.json',import.meta.url),'utf8'));
assert.equal(createHash('sha256').update(source).digest('hex'),freeze.files['web/app.js']);
const start=source.slice(source.indexOf('function startRun(job){'),source.indexOf('\nfunction simulate('));
const imported=source.slice(source.indexOf('async function importRun(file){'),source.indexOf('\nfunction describeExperiment('));
const lateWorker=Function('assert',`return function(profile,staleBy,callback){
 let special=null,sequence=9,activeId=null,pendingRun=null,worker=null,timer=null;
 const nodes=new Map(),events=[],workers=[],timers=[],compiledCatalogue={},catalogueHash='root';
 const $=id=>{if(!nodes.has(id))nodes.set(id,{hidden:false,disabled:false,textContent:'current',classList:{remove(){}},setAttribute(){}});return nodes.get(id);};
 const specialLaboratoryActive=()=>special!==null;
 const busy=x=>events.push(['busy',x]);const calculationError=e=>events.push(['error',e]);
 const clearTimeout=()=>events.push(['clearTimer']);const setTimeout=fn=>{timers.push(fn);return 1;};
 class Worker{constructor(){workers.push(this);this.terminated=false;}postMessage(m){events.push(['post',m.id]);}terminate(){this.terminated=true;events.push(['terminate']);}}
 ${start}
 startRun({s:{model:'ordinary'},id:9});const old=workers[0];assert.ok(old&&timers[0]);
 if(staleBy==='profile'){special=profile;}else{sequence=10;activeId=10;worker=new Worker();}
 const snapshot=()=>JSON.stringify({nodes:[...nodes],events,terminations:workers.map(w=>w.terminated),sequence,activeId,special});const before=snapshot();
 if(callback==='message')old.onmessage({data:{id:9,error:'Late old worker error'}});else if(callback==='error')old.onerror({message:'Late worker rejection'});else timers[0]();
 assert.equal(snapshot(),before);return {profile,staleBy,callback,noLateMutation:true};
}`)(assert);
const workerCases=[];
for(const profile of ['j2','burgers'])for(const staleBy of ['profile','newOrdinaryGeneration'])for(const callback of ['message','error','timeout'])workerCases.push(lateWorker(profile,staleBy,callback));
const lateImport=Function('assert',`return async function(profile){
 let sequence=9,special=null,rejectRead;const compiledCatalogue={},toasts=[],applied=[];
 const specialLaboratoryActive=()=>special!==null;const toast=m=>toasts.push(m),applyRunSpecification=s=>applied.push(s),parseLaboratoryDocument=x=>x;
 ${imported}
 const pending=importRun({size:2,text:()=>new Promise((resolve,reject)=>rejectRead=reject)});
 if(profile==='newOrdinaryGeneration')sequence++;else if(profile!=='ordinaryControl')special=profile;
 rejectRead(Error('Late file read error'));await pending;
 assert.equal(applied.length,0);assert.equal(toasts.length,profile==='ordinaryControl'?1:0);
 return {profile,suppressed:toasts.length===0,positiveErrorControl:profile==='ordinaryControl'};
}`)(assert);
const importCases=[];for(const profile of ['j2','burgers','newOrdinaryGeneration','ordinaryControl'])importCases.push(await lateImport(profile));
console.log(JSON.stringify({passed:true,source_sha256:freeze.files['web/app.js'],workerCases,importCases,compiledCalls:0,engineCalls:0,networkCalls:0,scope:'Exact frozen startRun/importRun functions, inert fake workers/timers/files. Worker message test supplies a late error payload; onerror and timeout separately checked; actual profile modules/routing require saved browser evidence.'},null,2));
