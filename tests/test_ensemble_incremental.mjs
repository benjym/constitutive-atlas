import test from 'node:test';
import assert from 'node:assert/strict';
import {EnsembleQueue,ensembleConcurrency} from '../web/ensemble-queue.mjs';
const job=(id,value=1)=>({id,model:id.split(':')[0],parameters:{value},history:{},specification:{value},status:'queued',result:null});
const study=jobs=>({catalogue_hash:'catalogue',experiment:{id:'test'},model_definitions:[{id:'a'},{id:'b'}],jobs});

test('editing one case executes only its changed request and retains other outcomes',async()=>{
 const calls=[],queue=new EnsembleQueue(async job=>{calls.push(job.id);return {ok:true,points:[job.specification.value]};});
 const first=study([job('a:baseline'),job('a:variation'),job('b:baseline')]);await queue.run(first);
 const next=queue.reconcile(study([job('a:baseline',2),job('a:variation'),job('b:baseline')]));
 assert.equal(next.jobs[1],first.jobs[1]);assert.equal(next.jobs[2],first.jobs[2]);
 await queue.run(next);assert.deepEqual(calls,['a:baseline','a:variation','b:baseline','a:baseline']);
 assert.deepEqual(next.jobs.map(j=>j.result.points[0]),[2,1,1]);
});

test('an edit aborts its obsolete running request while neighbouring work continues',async()=>{
 const calls=[],signals=new Map(),finish=new Map();
 const queue=new EnsembleQueue((job,signal)=>{calls.push([job.id,job.specification.value]);signals.set(job.id,signal);return new Promise(resolve=>finish.set(job.id,resolve));},()=>{},1000,2);
 const first=study([job('a:baseline'),job('b:baseline')]),running=queue.run(first);
 const aSignal=signals.get('a:baseline'),bSignal=signals.get('b:baseline');
 const next=queue.reconcile(study([job('a:baseline',2),job('b:baseline')]));
 assert.equal(aSignal.aborted,true);assert.equal(bSignal.aborted,false);assert.equal(next.jobs[1],first.jobs[1]);
 await new Promise(resolve=>setImmediate(resolve));
 finish.get('a:baseline')({ok:true,points:[2]});finish.get('b:baseline')({ok:true,points:[1]});await running;
 assert.deepEqual(calls,[['a:baseline',1],['b:baseline',1],['a:baseline',2]]);
 assert.ok(next.jobs.every(job=>job.status==='completed'));
});

test('removed cases stay removed and changed source, catalogue or definition invalidates reuse',async()=>{
 const queue=new EnsembleQueue(async()=>({ok:false,message:'retained stop',points:[1]}));
 const first=study([job('a:baseline'),job('b:baseline')]);await queue.run(first);
 const next=queue.reconcile(study([job('b:baseline')]));assert.equal(next.jobs.length,1);assert.equal(next.jobs[0],first.jobs[1]);
 for(const change of [s=>s.catalogue_hash='different',s=>s.experiment.id='different',s=>s.model_definitions[1].version=2]){
  const fresh=study([job('b:baseline')]);change(fresh);queue.study=first;
  assert.equal(queue.reconcile(fresh).jobs[0].status,'queued');
 }
});

test('worker pool follows available cores with room for the UI and a bounded maximum',()=>{
 assert.deepEqual([1,2,4,8,16,undefined].map(cores=>ensembleConcurrency(cores)),[1,1,3,7,8,3]);
 assert.doesNotThrow(()=>new EnsembleQueue(()=>{},()=>{},1000,8));
 assert.throws(()=>new EnsembleQueue(()=>{},()=>{},1000,9),/one to eight/);
});
