// Exact frozen run/select/invalidate continuations; inert deferred runPath, no engine execution.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=readFileSync(new URL('./source-r3/web/j2-laboratory.mjs',import.meta.url),'utf8');
const freeze=JSON.parse(readFileSync(new URL('./source-r3/interface-freeze-r3.json',import.meta.url),'utf8'));
assert.equal(createHash('sha256').update(source).digest('hex'),freeze.files['web/j2-laboratory.mjs']);
const invalidate=source.slice(source.indexOf('function invalidate(){'),source.indexOf('\nfunction fail(error)'));
const run=source.slice(source.indexOf('async function run(event){'),source.indexOf('\nform.addEventListener'));
const select=source.slice(source.indexOf(' function select(id){'),source.indexOf('\n return {modelId:MODEL'));
const execute=Function('assert',`return async function(mode){
 let token=0,active=true,lastResult=null,engine={ccall(){throw Error('No engine call authorized.');}},identity={},MODEL='j2',renders=0,failures=0,settle,rejectPath,beforeStep;
 const nodes=new Map(),rootHeader={textContent:'Ordinary model'},rootExport={disabled:false},panel={hidden:false};
 const $=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'old',disabled:false,className:'',children:['old'],replaceChildren(){this.children=[];}});return nodes.get(id);};
 const request=()=>({model:'j2',increments:[[1,0,0,0,0,0]]});
 const runPath=(call,r,i,options)=>{beforeStep=options.beforeStep;return new Promise((resolve,reject)=>{settle=resolve;rejectPath=reject;});};
 const render=()=>{renders++;$('stressValue').textContent='STALE RESULT';};
 const fail=error=>{failures++;$('status').textContent=error.message;};
 const ensureEngine=()=>{throw Error('Unexpected initialization');},cancelOrdinary=()=>{throw Error('Unexpected ordinary cancellation');};
 const document={getElementById(){throw Error('Unexpected outer DOM mutation');}};
 ${invalidate}
 ${run}
 ${select}
 const pending=run();assert.equal(typeof settle,'function');
 assert.equal(select('linear-elastic'),false);assert.equal(active,false);assert.equal(panel.hidden,true);
 const snapshot=()=>JSON.stringify({nodes:[...nodes],rootHeader,rootExport,panel});const afterDeactivation=snapshot();
 await assert.rejects(beforeStep(),/Superseded inputs/);
 if(mode==='resolve')settle({ok:true,points:[{step:0,state:Array(8).fill(0)},{step:1,state:Array(8).fill(1)}]});else rejectPath(Error('Late rejected solve'));
 await pending;
 assert.equal(snapshot(),afterDeactivation);assert.equal(renders,0);assert.equal(failures,0);assert.equal(lastResult,null);assert.equal($('download').disabled,true);
 return {mode,settledAfterDeactivation:true,lateBeforeStepRejected:true,postDeactivationDOMUnchanged:true,publicHeaderUnchanged:true,publicExportUnchanged:true,noResultPublished:true,renders,failures};
}`)(assert);
const cases=[await execute('resolve'),await execute('reject')];
console.log(JSON.stringify({passed:true,source_sha256:freeze.files['web/j2-laboratory.mjs'],cases,engineCalls:0,compiledCalls:0,networkCalls:0,scope:'Exact run/select/invalidate function source with inert deferred runPath. Tests stale completion and rejection; main-root DOM and route behavior remains actual browser evidence.'},null,2));
