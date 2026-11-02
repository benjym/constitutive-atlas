import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {defaults,solver,modelId,modelSha256,validateControls,request,importRun,verifyResult,verifyReplay,verifyApproval,verifyBuildReceipt,parseRunJSON} from '../web/bingham-atlas-contract.mjs';
import {setupBinghamLaboratory} from '../web/bingham-laboratory.mjs';
const cases=JSON.parse(readFileSync(new URL('../docs/ingestion/bingham-comsol63/execution-v1/cases.json',import.meta.url))).cases;
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:'synthetic-transport-fixture',review_sha256:'review',wasm_sha256:'wasm'};
const controls=(mode='relaxation')=>({...structuredClone(defaults),mode});
function fixture(mode='relaxation'){
 const c=controls(mode),spec=cases.find(x=>x.id==='public-'+mode),refs=spec.references;
 const points=[refs[0],...refs].map((p,i)=>({time:p.time,side:i===1?'right':'left',segment:i===0?-1:0,state:p.state,strain:p.state.slice(0,6),strain_rate:i===1&&mode==='creep'?Array(6).fill(null):Array(6).fill(0),observables:p.stress}));
 return {ok:true,message:'',catalogue_hash:identity.catalogue_hash,model:modelId,units:'SI',schema_version:'0.2',start_time:c.start,parameters:c.parameters,initial:c.initial,initial_strain:c.initial.slice(0,6),initial_strain_rate:Array(6).fill(0),solver:{...solver},points};
}
const documentFor=(mode='relaxation')=>({kind:'atlas-bingham-laboratory-v1',controls:controls(mode),provenance:identity,request:{function:'atlas_run_schedule',args:request(controls(mode),identity)},result:fixture(mode)});
test('three mode transports preserve13state/all-six physical controls',()=>{
 for(const mode of ['relaxation','creep','rate']){const c=controls(mode),args=request(c,identity),wire=args[5].split(',').map(Number);assert.equal(args[2].split(',').length,13);assert.equal(args[7],0);assert.equal(wire[0],2);assert.equal(wire[1],4);for(let i=0;i<6;i++){assert.equal(wire[2+3*i],+(mode==='creep'));assert.equal(wire[3+3*i],+(mode==='rate'));assert.equal(wire[4+3*i],mode==='rate'?c.rates[i]:0);}verifyResult(fixture(mode),identity,c);assert.deepEqual(importRun(JSON.stringify(documentFor(mode)),identity),c);}
});
test('invalid controls and traces reject before transport; caller/defaults preserved',()=>{
 const original=JSON.stringify(defaults);
 for(const delta of [{mode:'unknown'},{duration:0},{duration:Infinity},{duration:10001},{samples:1.5},{samples:201},{start:-1},{start:1e30,duration:1},{parameters:[20e6,10e6,0,20e6]},{parameters:[20e6,10e6,1e31,20e6]},{rates:[0]},{initial:Array(13).fill(NaN)},{initial:[...defaults.initial.slice(0,12),-1]},{initial:defaults.initial.map((v,i)=>i===6?1e-9:v)},{extra:1}])assert.throws(()=>validateControls({...structuredClone(defaults),...delta}));
 const copy=validateControls(defaults);copy.initial[0]=99;assert.equal(JSON.stringify(defaults),original);
 assert.throws(()=>request(defaults,{...identity,model_sha256:'other'}));
});
test('JSON rejects ambiguous numerical/document identities',()=>{
 for(const text of ['{"x":1,"x":2}','{"x":1,"\\u0078":2}','{"x":1e999}','{"x":9007199254740993}'])assert.throws(()=>parseRunJSON(text));
 assert.deepEqual(parseRunJSON('{"x":1,"nested":{"x":2},"text":"1e999"}'),{x:1,nested:{x:2},text:'1e999'});
 for(const mutate of [d=>d.provenance.model='other',d=>d.provenance.wasm_sha256='other',d=>d.provenance.extra=1,d=>d.extra=1,d=>d.request.args[14]=39,d=>d.controls.initial.pop(),d=>d.result.points[2].state.pop(),d=>d.result.points[2].observables[0]=null,d=>d.result.points[2].time=3,d=>d.result.solver.maximum_depth=39,d=>d.result.points[1].side='left',d=>d.result.points[0].strain[0]=9,d=>d.result.points[2].strain_rate=Array(6).fill(null),d=>d.result.points[2].state[12]=-1]){const d=structuredClone(documentFor());mutate(d);assert.throws(()=>importRun(JSON.stringify(d),identity));}
});
test('full-result replay rejects finite later state/stress tampering',()=>{
 const doc=documentFor(),changed=structuredClone(doc);changed.result.points[2].state[12]+=.1;changed.result.points[2].observables[3]+=100;
 const imported=importRun(JSON.stringify(changed),identity,{withResult:true});assert.throws(()=>verifyReplay(doc.result,imported.result));assert.deepEqual(verifyReplay(doc.result,Object.fromEntries(Object.entries(doc.result).reverse())),doc.result);
});
test('approved scope requires exact separate-agent accepted nine-item bundle',()=>{
 const definition={id:modelId,schema_version:'0.3'},approval={model_id:modelId,status:'approved',definition:{sha256:modelSha256},review:{sha256:identity.review_sha256},approval_authority:{kind:'independent-agent-review'}},review={status:'accepted',model:{id:modelId,sha256:modelSha256},blocking_findings:[],reviewer:{run_id:'reviewer'},author_run_ids:['author'],checklist:['source_provenance','equation_fidelity','conventions_dimensions','initialization_domain','integration_transactions','independent_numerical_evidence','backend_delivery','applicability_claims','reproducibility_rights'].map(id=>({id,outcome:'pass'}))};
 assert.equal(verifyApproval(identity,approval,review,definition),true);
 for(const mutate of [r=>r.status='pending',r=>r.blocking_findings=['gap'],r=>r.reviewer.run_id='author',r=>r.checklist.pop(),r=>r.checklist[0].outcome='fail',r=>r.model.sha256='other']){const changed=structuredClone(review);mutate(changed);assert.throws(()=>verifyApproval(identity,approval,changed,definition));}
});
// A deliberately small DOM/Worker test double checks controller ownership/races,
// not browser layout or scientific integration. No engine module is instantiated.
test('controller cancels stale workers, rejects invalid edits and recovers by reset',()=>{
 const saved={document:globalThis.document,Worker:globalThis.Worker,Option:globalThis.Option};const elements=new Map(),workers=[];
 class Element{constructor(){this.value='';this.options=[];this.children=[];this.events={};this.selectedIndex=0;this.textContent='';}set innerHTML(text){for(const [,id]of text.matchAll(/id="([^"]+)"/g))elements.set(id,new Element());}append(...items){this.children.push(...items);if(this===elements.get('model'))this.options.push(...items);}after(){}replaceChildren(...items){this.children=items;}addEventListener(name,fn){this.events[name]=fn;}scrollIntoView(){}}
 for(const id of ['model','model-description','model-family','model-status','model-sources','import-run'])elements.set(id,new Element());
 globalThis.document={getElementById:id=>elements.get(id),querySelector:()=>new Element(),createElement:()=>new Element()};globalThis.Option=class{constructor(text,value){this.text=text;this.value=value;}};
 globalThis.Worker=class{constructor(){workers.push(this);}postMessage(message){this.message=message;}terminate(){this.terminated=true;}emit(){this.onmessage({data:{id:this.message.id,result:fixture(),identity,args:request(defaults,identity)}});}};
 let controller;try{
  controller=setupBinghamLaboratory({chart:()=>{}});controller.select(modelId);const first=workers.at(-1);assert.equal(elements.get('model-status').textContent,'Verification pending');
  elements.get('bingham-controls').events.input({target:{id:'bingham-duration'}});assert.equal(first.terminated,true);controller.run();const second=workers.at(-1);first.emit();assert.equal(elements.get('bingham-export').disabled,true);second.emit();assert.equal(elements.get('bingham-export').disabled,false);assert.equal(elements.get('model-status').textContent,'Approved bounded scope');
  controller.run();const cancelled=workers.at(-1);elements.get('bingham-cancel').onclick();assert.equal(cancelled.terminated,true);cancelled.emit();assert.equal(elements.get('bingham-export').disabled,true);assert.match(elements.get('bingham-status').textContent,/cancelled/);
  const count=workers.length;elements.get('bingham-initial').value=JSON.stringify([...defaults.initial.slice(0,12),-1]);controller.run();assert.match(elements.get('bingham-status').textContent,/Invalid input/);assert.equal(workers.length,count);
  elements.get('bingham-reset').onclick();workers.at(-1).emit();assert.equal(elements.get('bingham-export').disabled,false);controller.select('other');assert.equal(controller.active,false);assert.equal(elements.get('bingham-export').disabled,true);
 }finally{controller?.select('other');Object.assign(globalThis,saved);}
});

test('engine receipt rejects unreviewed or substituted artifact bytes',()=>{
 const sha='1'.repeat(64),id={...identity,module_sha256:sha,wasm_sha256:sha,catalogue_file_sha256:sha,build_receipt_sha256:sha},receipt={kind:'bingham-qualified-engine-build-v1',model:{id:modelId,sha256:modelSha256},artifacts:Object.fromEntries(['module','wasm','metadata'].map(k=>[k,{path:'original/'+k,sha256:sha}]))},review={artifacts:[{path:'docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json',sha256:sha}]};
 assert.equal(verifyBuildReceipt(id,review,receipt),true);
 for(const mutate of [r=>r.model.sha256='other',r=>r.artifacts.wasm.sha256='2'.repeat(64),r=>delete r.artifacts.metadata,r=>r.artifacts.module.path='',r=>r.kind='unreviewed']){const changed=structuredClone(receipt);mutate(changed);assert.throws(()=>verifyBuildReceipt(id,review,changed));}
 assert.throws(()=>verifyBuildReceipt(id,{artifacts:[]},receipt));assert.throws(()=>verifyBuildReceipt({...id,wasm_sha256:'2'.repeat(64)},review,receipt));
});
