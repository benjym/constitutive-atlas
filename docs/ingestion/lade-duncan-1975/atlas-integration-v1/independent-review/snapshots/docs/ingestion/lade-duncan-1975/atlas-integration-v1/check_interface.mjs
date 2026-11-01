// Pure transport/lifecycle tests against saved qualified native output; no Wasm calls.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import * as c from '../../../../web/implicit-path-contract.mjs';
import {createImplicitPathRunner} from '../../../../web/implicit-path-runner.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..'),checks=[];
const test=(name,fn)=>{try{fn();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,error:String(error)});}};
const read=p=>c.parseRunJSON(fs.readFileSync(path.join(root,p),'utf8'));
const report=read('docs/ingestion/lade-duncan-1975/outer-predictor-v1/native-triaxial-fixed-results.json');
const row=report.requests.find(x=>x.set==='dense'&&x.target===.005&&x.steps===400),result=read(row.raw_path),input=c.preset(),identity={profile:'implicit-path-v1',model:c.modelId,model_sha256:c.modelSha256,public_models:[c.modelId],catalogue_hash:result.catalogue_hash};
test('source400 response accepted',()=>assert.equal(c.verifyResult(result,identity,input),result));
test('settings wire uses declared order',()=>{const q=structuredClone(input);q.settings=Object.fromEntries(Object.entries(q.settings).reverse());assert.deepEqual(c.request(q,identity),c.request(input,identity));});
test('signed zero CSV and export survive',()=>{const q=structuredClone(input);q.initial[3]=-0;assert.equal(c.request(q,identity)[2].split(',')[3],'-0');assert(Object.is(c.parseRunJSON(c.stringifyRun(q)).initial[3],-0));assert(!c.equal(-0,0));});
test('complete export import replay',()=>{const saved=c.exportRun(input,result,identity),back=c.importRun(c.stringifyRun(saved),identity);assert(c.equal(back.controls,input));c.verifyReplay(back.result,result);});
for(const [name,mutate] of Object.entries({catalogue:r=>r.catalogue_hash='stale',model:r=>r.model='linear-elastic',scope:r=>r.stress.scope='effective',pore:r=>r.points[0].u=0,settings:r=>r.integration_settings.increment_tolerance=0,nonfinite:r=>r.points[1].state[1]=NaN,initial:r=>r.points[0].state[0]+=1,truncated:r=>r.points.pop(),loading:r=>r.points[2].control+=.001,elapsed:r=>r.elapsed_ms=Infinity}))test('reject altered '+name,()=>{const q=structuredClone(result);mutate(q);assert.throws(()=>c.verifyResult(q,identity,input));});
for(const text of ['{"a":1,"a":2}','{"a":1,"\\u0061":2}','{"a":1e999}','{"a":9007199254740993}','{"a":1,}'])test('strict JSON '+text,()=>assert.throws(()=>c.parseRunJSON(text)));
test('tampered result rejected on replay',()=>{const q=structuredClone(result);q.points[1].state[0]+=1;assert.throws(()=>c.verifyReplay(result,q));});
test('failure preserves valid prefix',()=>{const q={...structuredClone(result),ok:false,message:'last committed point retained',points:result.points.slice(0,2)};c.verifyResult(q,identity,input);assert.throws(()=>c.exportRun(input,q,identity));});
test('witness public route rejected',()=>assert.throws(()=>c.request({...input,model:'linear-elastic'},identity)));
test('latest-request cancellation timeout recovery',()=>{
 const workers=[],events=[],timers=new Map();let counter=0;
 const runner=createImplicitPathRunner({createWorker:()=>{const w={terminated:false,terminate(){this.terminated=true;},postMessage(m){this.request=m;}};workers.push(w);return w;},notify:e=>events.push(e),setTimer:f=>{timers.set(++counter,f);return counter;},clearTimer:id=>timers.delete(id)});
 runner.run(input);const old=workers.at(-1),oldId=old.request.id;runner.run(input);assert(old.terminated);old.onmessage({data:{id:oldId,result,identity,args:c.request(input,identity)}});assert.equal(events.at(-1).state,'running');
 const current=workers.at(-1);current.onmessage({data:{id:current.request.id,result,identity,args:c.request(input,identity)}});assert.equal(events.at(-1).state,'complete');assert(current.terminated);assert.equal(timers.size,0);
 runner.run(input);const timed=workers.at(-1);[...timers.values()][0]();assert(timed.terminated);assert.equal(events.at(-1).state,'error');assert.equal(runner.last,null);
 runner.run(input);const recovered=workers.at(-1);recovered.onmessage({data:{id:recovered.request.id,result,identity,args:c.request(input,identity)}});assert.equal(events.at(-1).state,'complete');runner.cancel();assert.equal(runner.last,null);
});
test('signed-zero UI hydration and runner replay preserve request bits',()=>{
 const q=structuredClone(input);q.initial[3]=-0;
 const hydration={...q,parameters:c.parseRunJSON(c.controlText(q.parameters)),initial:c.parseRunJSON(c.controlText(q.initial)),target:Number(c.controlText(q.target))};assert(c.equal(hydration,q));assert(Object.is(Number(c.controlText(-0)),-0));
 const r=structuredClone(result);r.initial[3]=-0;r.points[0].state[3]=-0;const expected=c.exportRun(q,r,identity);let w,event;
 const runner=createImplicitPathRunner({createWorker:()=>w={terminate(){},postMessage(m){this.request=m;}},notify:e=>event=e,setTimer:()=>1,clearTimer(){}});
 runner.run(hydration,{expected});w.onmessage({data:{id:w.request.id,result:r,identity,args:c.request(q,identity)}});assert.equal(event.state,'complete');assert(Object.is(event.run.controls.initial[3],-0));
});
test('elapsed deadline rejects message even if timer has not fired',()=>{
 let t=0,w,event;const runner=createImplicitPathRunner({createWorker:()=>w={terminate(){},postMessage(m){this.request=m;}},notify:e=>event=e,setTimer:()=>1,clearTimer(){},now:()=>t});runner.run(input);t=120000;w.onmessage({data:{id:w.request.id,result,identity,args:c.request(input,identity)}});assert.equal(event.state,'error');assert.equal(runner.last,null);
});
test('worker creation is inside elapsed budget',()=>{
 let t=0,event,terminated=false,posted=false;const runner=createImplicitPathRunner({now:()=>t,createWorker:()=>{t=120000;return {terminate(){terminated=true;},postMessage(){posted=true;}};},notify:e=>event=e,setTimer:()=>1,clearTimer(){}});runner.run(input);assert.equal(event.state,'error');assert(terminated);assert(!posted);
});
const output={scope:'pure interface/saved-response fixtures; no compiled calls or browser approval',passed:checks.every(x=>x.passed),checks};fs.writeFileSync(path.join(here,'interface-results.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));process.exitCode=output.passed?0:1;
