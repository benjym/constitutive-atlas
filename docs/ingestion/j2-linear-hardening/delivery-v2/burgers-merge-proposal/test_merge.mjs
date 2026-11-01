// Source-only merge witnesses: no browser/network/engine or compiled artifacts.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(process.argv[2]||new URL('./web/app.js',import.meta.url),'utf8');
function fn(name){const start=source.indexOf(`function ${name}(`);assert.ok(start>=0,name);const lineEnd=source.indexOf('\n',start);if(source.slice(start,lineEnd).endsWith('}'))return source.slice(start,lineEnd);const next=source.indexOf('\n}',start);return source.slice(start,next+2);}
class Node{constructor(){this.hidden=false;this.value='';this.children=[];}append(n){this.children.push(n);}replaceChildren(){this.children=[];}}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);};
const context={document:{querySelector:node},$:node,element:()=>new Node(),trace:[]};
vm.createContext(context);
vm.runInContext(`let experimentLoadSequence=0;const j2View={modelId:'j2',active:false,select(id){trace.push(['j2',id]);this.active=id===this.modelId;if(this.active)$('model').value=this.modelId;return this.active;}};const timedView={modelId:'burgers',active:false,select(id){trace.push(['burgers',id]);this.active=id===this.modelId;document.querySelector('#laboratory > .lab-layout').hidden=this.active;document.querySelector('#laboratory > .workspace-links').hidden=this.active;$('import-run').hidden=this.active;if(this.active){$('model').value=this.modelId;$('model-description').textContent='Burgers';}return this.active;}};
${fn('specialLaboratoryActive')}
${fn('selectJ2')}
${fn('selectLaboratory')}
globalThis.api={select:selectLaboratory,active:specialLaboratoryActive,views:()=>[j2View.active,timedView.active],revision:()=>experimentLoadSequence};`,context);
const {api,trace}=context;let checks=0;
function selected(id,flags,hidden,description){trace.length=0;assert.equal(api.select(id),hidden);assert.deepEqual(Array.from(api.views()),flags);assert.equal(node('#laboratory > .lab-layout').hidden,hidden);assert.equal(node('#laboratory > .workspace-links').hidden,hidden);assert.equal(node('import-run').hidden,hidden);if(description)assert.match(node('model-description').textContent,description);checks+=5;return JSON.parse(JSON.stringify(trace));}
assert.deepEqual(selected('j2',[true,false],true,/J2/),[['j2','j2']]);
assert.deepEqual(selected('burgers',[false,true],true,/Burgers/),[['j2',false],['burgers','burgers']]);
assert.deepEqual(selected('j2',[true,false],true,/J2/),[['burgers',false],['j2','j2']]);
assert.deepEqual(selected('j2',[true,false],true,/J2/),[['j2','j2']]);
assert.deepEqual(selected('linear-elastic',[false,false],false),[['j2',false]]);
assert.deepEqual(selected('burgers',[false,true],true,/Burgers/),[['burgers','burgers']]);
assert.deepEqual(selected('linear-elastic',[false,false],false),[['burgers',false]]);
assert.equal(api.revision(),4);checks++;
// The source keeps exact-ID lookup: a special ID cannot masquerade as VW96.
assert.match(source,/function model\(\)\{return models\.find\(x=>x\.id===\$\('model'\)\.value\);\}/);checks++;
for(const name of ['populate','simulate','renderCharts','describeExperiment','experimentOptions','scheduleUpdate','showExperiment','selectExperiment','matchExperiment','applyRunSpecification']){assert.ok(fn(name).includes('if(specialLaboratoryActive())return;'),name);checks++;}
for(const marker of ["import {setupTimedLaboratory}","import {setupJ2Laboratory}","id===j2View?.modelId||id===timedView?.modelId","selectLaboratory(entry.id)","selectLaboratory($('model').value)","j2View?.showEquations()||timedView?.showEquations()","requested!==sequence||specialLaboratoryActive()","id!==activeId||specialLaboratoryActive()","revision===experimentLoadSequence&&!specialLaboratoryActive()","finally{if(id===experimentLoadSequence&&!specialLaboratoryActive())$('experiment-file').value='';}","timedView=setupTimedLaboratory({chart,cancelOrdinary:()=>cancel('')})","j2View=setupJ2Laboratory({cancelOrdinary:()=>cancel('')})"]){assert.ok(source.includes(marker),marker);checks++;}
console.log(JSON.stringify({passed:true,checks,transitionCalls:7,compiledCalls:0,networkCalls:0,scope:'Exact extracted coordinator source under a DOM/profile mock plus static hook/async guards; real module/browser/package evidence remains parent-owned.'},null,2));
