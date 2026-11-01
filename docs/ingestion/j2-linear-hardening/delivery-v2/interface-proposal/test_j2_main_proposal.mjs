// Pure DOM/API proposal test. No engine, Wasm compilation, network or browser execution.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const base=resolve(process.argv[2]||resolve(dirname(fileURLToPath(import.meta.url)),'..'));
const source=readFileSync(resolve(base,'web/j2-laboratory.mjs'),'utf8');
let assertions=0,fetches=0,cancelled=0,compiled=0;
class Element{
 constructor(tag='div'){this.tagName=tag;this.children=[];this.listeners={};this.hidden=false;this.value='';this.textContent='';this.disabled=false;this.selectedIndex=0;}
 setAttribute(k,v){this[k]=v;}
 append(...nodes){this.children.push(...nodes);}
 replaceChildren(...nodes){this.children=[...nodes];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 scrollIntoView(){this.scrolled=true;}
 attachShadow(){const map=new Map();this.shadowRoot={getElementById:id=>map.get(id),set innerHTML(text){for(const m of text.matchAll(/\bid="([^"]+)"/g))map.set(m[1],new Element());}};return this.shadowRoot;}
 after(node){mounted=node;}
}
let mounted=null;
const ordinary=new Element(),model=new Element('select');ordinary.hidden=false;
const concurrent=new Element();concurrent.hidden=false;
globalThis.document={querySelector:q=>q==='#laboratory > .lab-layout'?ordinary:null,getElementById:id=>id==='model'?model:id==='j2-material-laboratory'?mounted:null,createElement:tag=>new Element(tag)};
globalThis.Option=class{constructor(text,value){this.text=text;this.value=value;}};
let settleFetch;globalThis.fetch=()=>{fetches++;return new Promise(resolve=>settleFetch=resolve);};
const compile=WebAssembly.compile;WebAssembly.compile=()=>{compiled++;throw Error('No compiled execution authorized.');};
const {setupJ2Laboratory}=await import(pathToFileURL(resolve(base,'web/j2-laboratory.mjs')));
const api=setupJ2Laboratory({cancelOrdinary:()=>cancelled++});
assert.equal(api.modelId,'j2-linear-isotropic-hardening-be');assert.equal(api.active,false);assert.equal(mounted.hidden,true);assert.equal(model.children.length,1);assertions+=4;
assert.equal(mounted.shadowRoot.getElementById('initial').value,'0,0,0,0,0,0,0,0');assert.equal(mounted.shadowRoot.getElementById('increments').value.split('\n').length,3);assert.equal(fetches,0);assertions+=3;
assert.equal(api.showEquations(),false);assert.equal(api.select(api.modelId),true);assert.equal(api.active,true);assert.equal(mounted.hidden,false);assert.equal(model.value,api.modelId);assert.equal(cancelled,1);assert.equal(fetches,1);assertions+=7;
assert.equal(api.showEquations(),true);assert.equal(mounted.shadowRoot.getElementById('equations').open,true);assertions+=2;
assert.equal(api.select(false),false);assert.equal(api.active,false);assert.equal(mounted.hidden,true);assert.equal(ordinary.hidden,false);assert.equal(concurrent.hidden,false);assert.equal(api.showEquations(),false);assertions+=6;
// Pending engine initialization does not refetch or expose another interface on rapid switching.
api.select(api.modelId);api.select('linear-elastic');assert.equal(fetches,1);assert.equal(ordinary.hidden,false);assert.equal(concurrent.hidden,false);assert.equal(compiled,0);assertions+=4;
const before=mounted.shadowRoot.getElementById('status').textContent;settleFetch({ok:false});await new Promise(resolve=>setImmediate(resolve));assert.equal(mounted.shadowRoot.getElementById('status').textContent,before);assert.equal(ordinary.hidden,false);assert.equal(concurrent.hidden,false);assertions+=3;
api.select(api.modelId);assert.equal(fetches,2);assert.equal(api.active,true);api.select(false);assertions+=2;
// An older pending file import must not clear a newly selected file after deactivation/reselection.
api.select(api.modelId);const imported=mounted.shadowRoot.getElementById('import');let settleText;
imported.files=[{size:2,text:()=>new Promise(resolve=>settleText=resolve)}];imported.value='old.json';
const pendingImport=imported.listeners.change();api.select(false);api.select(api.modelId);imported.value='new.json';
const latestStatus=mounted.shadowRoot.getElementById('status').textContent;settleText('{}');await pendingImport;
assert.equal(imported.value,'new.json');assert.equal(mounted.shadowRoot.getElementById('status').textContent,latestStatus);assert.equal(compiled,0);assertions+=3;api.select(false);
assert.throws(()=>setupJ2Laboratory());assertions++;
for(const marker of ["attachShadow({mode:'open'})","material-point-j2/identity.json","material-point-j2/approval.json","material-point-j2/review.json",'material-point-j2/review.html#law-review','material-point-j2/review.html#interface-review','URL.createObjectURL','instantiateWasm(imports,receive)','wasmBinary:verifiedWasm','runPath(','replayRequest(','Full state','Complete state at every accepted row']){
 if(marker==='Full state')continue;
 assert.ok(source.includes(marker),marker);assertions++;
}
for(const retired of ['j2.html','engine-j2/','j2-review.html','j2-delivery.html','j2-approval.json','j2-agent-review.json']){assert.ok(!source.includes(retired),retired);assertions++;}
assert.ok(source.includes("finally{if(mine===token&&active)$('import').value='';}"));assertions++;
assert.ok(!source.includes('ordinary.hidden='));assert.ok(!source.includes("document.getElementById('controls')"));assertions+=2;
WebAssembly.compile=compile;
console.log(JSON.stringify({passed:true,assertions,engineCalls:0,compiledCalls:compiled,networkCalls:0,scope:'Pure shadow-DOM mounting/select API, lazy initialization and source-contract checks; actual packaged browser qualification remains pending.'},null,2));
