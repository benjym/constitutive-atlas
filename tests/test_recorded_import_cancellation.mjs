import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {setupRecordedView} from '../web/recorded-view.mjs';
const example=JSON.parse(readFileSync(new URL('../protocols/recorded-linear-elastic-run.json',import.meta.url)));
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return {promise,resolve,reject};};
function harness(t){
 const saved=Object.fromEntries(['document','Worker','fetch','setTimeout','clearTimeout'].map(k=>[k,globalThis[k]]));
 t.after(()=>{for(const [key,value] of Object.entries(saved))globalThis[key]=value;});
 const elements=new Map(),workers=[],timers=new Map();let timerId=0;
 const get=id=>{if(!elements.has(id))elements.set(id,{value:'0',textContent:'',hidden:true,disabled:true,selectedOptions:[{textContent:'Axial'}],replaceChildren(){},append(){}});return elements.get(id);};
 globalThis.document={getElementById:get};
 globalThis.Worker=class{constructor(){workers.push(this);}postMessage(data){this.request=data;}terminate(){this.terminated=true;}};
 globalThis.setTimeout=(fn)=>{timers.set(++timerId,fn);return timerId;};
 globalThis.clearTimeout=id=>timers.delete(id);
 globalThis.fetch=()=>{throw Error('Unexpected fetch');};
 setupRecordedView({models:[{id:example.model,name:'Test model',sources:[]}],catalogueHash:'fixture-catalogue',chart(){},sourceLinks(){},definitionLink(){return {};}});
 function file(read,size=1){const target={files:[{size,text:read}],value:'selected.json'};return {target,done:get('recorded-file').onchange({target})};}
 const doc=name=>{const d=structuredClone(example);d.path.coordinate.name=name;return JSON.stringify(d);};
 return {get,workers,timers,file,doc};
}
test('latest file wins even when an older read finishes last',async t=>{
 const h=harness(t),old=deferred(),latest=deferred();
 const a=h.file(()=>old.promise),b=h.file(()=>latest.promise);
 latest.resolve(h.doc('Latest'));await b.done;
 old.resolve(h.doc('Superseded'));await a.done;
 assert.equal(h.workers.length,1);assert.equal(h.workers[0].request.specification.path.coordinate.name,'Latest');
 assert.match(h.get('recorded-status').textContent,/Replaying/);
 assert.equal(a.target.value,'');assert.equal(b.target.value,'');
});
test('cancel during a pending example body prevents replay',async t=>{
 const h=harness(t),body=deferred();globalThis.fetch=async()=>({ok:true,text:()=>body.promise});
 const pending=h.get('recorded-example').onclick();
 assert.equal(h.get('recorded-cancel').hidden,false);
 h.get('recorded-cancel').onclick();const status=h.get('recorded-status').textContent;
 body.resolve(h.doc('Cancelled'));await pending;
 assert.equal(h.workers.length,0);assert.equal(h.get('recorded-status').textContent,status);
 assert.equal(h.get('recorded-cancel').hidden,true);
});
test('a new file invalidates a pending example download',async t=>{
 const h=harness(t),response=deferred();globalThis.fetch=()=>response.promise;
 const pending=h.get('recorded-example').onclick();await h.file(async()=>h.doc('File')).done;
 response.resolve({ok:true,text:async()=>h.doc('Old example')});await pending;
 assert.equal(h.workers.length,1);assert.equal(h.workers[0].request.specification.path.coordinate.name,'File');
});
test('superseded read errors do not overwrite the latest status',async t=>{
 const h=harness(t),old=deferred();const pending=h.file(()=>old.promise);
 await h.file(async()=>h.doc('Latest')).done;const status=h.get('recorded-status').textContent;
 old.reject(Error('Late disk failure'));await pending.done;
 assert.equal(h.get('recorded-status').textContent,status);assert.equal(h.workers.length,1);
});
test('new import stops old worker immediately and ignores its late response',async t=>{
 const h=harness(t);await h.file(async()=>h.doc('First')).done;
 const worker=h.workers[0],next=deferred(),pending=h.file(()=>next.promise);
 assert.equal(worker.terminated,true);assert.equal(h.get('recorded-export').disabled,true);
 const status=h.get('recorded-status').textContent;
 worker.onmessage({data:{id:worker.request.id,error:'Stale worker failure'}});
 assert.equal(h.get('recorded-status').textContent,status);
 h.get('recorded-cancel').onclick();next.resolve(h.doc('Never run'));await pending.done;
 assert.equal(h.workers.length,1);
});
test('oversize and malformed imports fail without reading or launching a worker',async t=>{
 const h=harness(t);let read=false;
 await h.file(async()=>{read=true;return h.doc('Too big');},10*1024*1024+1).done;
 assert.equal(read,false);assert.match(h.get('recorded-status').textContent,/10 MB/);
 await h.file(async()=>'{"version":"invalid"}').done;
 assert.match(h.get('recorded-status').textContent,/Import rejected/);
 assert.equal(h.workers.length,0);assert.equal(h.get('recorded-export').disabled,true);
 assert.equal(h.get('recorded-replay').disabled,true);assert.equal(h.get('recorded-cancel').hidden,true);
});
