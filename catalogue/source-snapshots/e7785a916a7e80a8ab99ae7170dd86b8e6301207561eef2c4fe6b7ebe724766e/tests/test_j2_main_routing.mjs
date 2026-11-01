// Source-only merge witnesses: no browser/network/engine or compiled artifacts.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const source=readFileSync(process.argv[2]||new URL('../web/app.js',import.meta.url),'utf8');
function fn(name){let start=source.indexOf(`function ${name}(`);assert.ok(start>=0,name);if(source.slice(start-6,start)==='async ')start-=6;const lineEnd=source.indexOf('\n',start);if(source.slice(start,lineEnd).endsWith('}'))return source.slice(start,lineEnd);const next=source.indexOf('\n}',start);return source.slice(start,next+2);}
class Node{constructor(){this.hidden=false;this.value='';this.children=[];}append(n){this.children.push(n);}replaceChildren(){this.children=[];}remove(){}}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);};
const context={document:{querySelector:node},$:node,element:()=>new Node(),refreshPublicModelSummary:()=>{},trace:[]};
vm.createContext(context);
vm.runInContext(`let experimentLoadSequence=0,sequence=1,compiledCatalogue={};const j2View={modelId:'j2',active:false,select(id){trace.push(['j2',id]);this.active=id===this.modelId;if(this.active)$('model').value=this.modelId;return this.active;}};const timedView={modelId:'burgers',active:false,supports(id){return id==='burgers'||id==='sls';},select(id){trace.push(['burgers',id]);this.active=this.supports(id);document.querySelector('#laboratory > .lab-layout').hidden=this.active;document.querySelector('#laboratory > .workspace-links').hidden=this.active;$('import-run').hidden=this.active;if(this.active){$('model').value=this.modelId;$('model-description').textContent='Burgers';}return this.active;}};
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
for(const marker of ["import {setupTimedLaboratory}","import {setupKelvinVoigtLaboratory}","import {setupJ2Laboratory}","import {setupImplicitPathLaboratory}","id!==j2View?.modelId&&!timedView?.supports(id)","activateLaboratoryModel(entry.id)","activateLaboratoryModel($('model').value)","j2View?.showEquations()||timedView?.showEquations()","requested!==sequence||specialLaboratoryActive()","id!==activeId||specialLaboratoryActive()","revision===experimentLoadSequence&&!specialLaboratoryActive()","finally{if(id===experimentLoadSequence&&!specialLaboratoryActive())$('experiment-file').value='';}","j2View=setupJ2Laboratory({cancelOrdinary:()=>cancel('')})"]){assert.ok(source.includes(marker),marker);checks++;}
// Extensible membership preserves every existing controller and its exact wiring.
const registration=source.match(/timedView=createLaboratoryControllerRouter\(\[([^\n]+?)\]\)/)?.[1];
assert.ok(registration,'Main controller router registration');checks++;
const setups=[...registration.matchAll(/\b(setup[A-Za-z]+Laboratory)\(/g)].map(match=>match[1]);
assert.equal(new Set(setups).size,setups.length,'Duplicate controller registration');checks++;
for(const setup of ['setupTimedLaboratory','setupSlsLaboratory','setupKelvinVoigtLaboratory','setupPathLaboratory','setupMaxwellLaboratory','setupImplicitPathLaboratory']){
 assert.equal(setups.filter(name=>name===setup).length,1,setup);
 assert.ok(registration.includes(`${setup}({chart,cancelOrdinary:()=>cancel('')})`),setup+' exact existing hooks');checks+=2;
}
assert.equal(setups.filter(name=>name==='setupHillLaboratory').length,1);checks++;
assert.ok(registration.includes("setupHillLaboratory({cancelOrdinary:()=>cancel('')})"));checks++;
assert.ok(source.includes("import {setupHillLaboratory} from './hill-laboratory.mjs';"));checks++;
assert.equal(setups.filter(name=>name==='setupOrthotropicLaboratory').length,1);checks++;
assert.ok(registration.includes("setupOrthotropicLaboratory({cancelOrdinary:()=>cancel('')})"));checks++;
assert.ok(source.includes("import {setupOrthotropicLaboratory} from './orthotropic-laboratory.mjs';"));checks++;
// Execute the exact ordinary import function with delayed file text; profile changes and
// newer ordinary revisions must suppress it before parsing/applying a stale request.
const applied=[];context.applied=applied;context.parseLaboratoryDocument=text=>({text});context.applyRunSpecification=spec=>applied.push(spec);context.toast=()=>{throw Error('Unexpected ordinary toast.');};
vm.runInContext(`${fn('importRun')}globalThis.importUnderTest=importRun;globalThis.bumpSequence=()=>sequence++;`,context);
let settle;const file=()=>({size:2,text:()=>new Promise(resolve=>settle=resolve)});
let pending=context.importUnderTest(file());api.select('j2');settle('{}');await pending;assert.equal(applied.length,0);checks++;
api.select('linear-elastic');pending=context.importUnderTest(file());context.bumpSequence();settle('{}');await pending;assert.equal(applied.length,0);checks++;
pending=context.importUnderTest(file());api.select('burgers');settle('{}');await pending;assert.equal(applied.length,0);checks++;
api.select('linear-elastic');pending=context.importUnderTest(file());settle('{}');await pending;assert.equal(applied.length,1);checks++;
// Exercise the exact committed router with inert controllers, using the actual merged
// app coordinator. Router deactivation deliberately restores ordinary visibility.
const {createLaboratoryControllerRouter}=await import(process.argv[3]?pathToFileURL(resolve(process.argv[3])):new URL('../web/laboratory-controller-router.mjs',import.meta.url));
const mixedNodes=new Map(),mixedNode=id=>{if(!mixedNodes.has(id))mixedNodes.set(id,new Node());return mixedNodes.get(id);};
const mixed={document:{querySelector:mixedNode},$:mixedNode,element:()=>new Node(),refreshPublicModelSummary:()=>{},trace:[],createLaboratoryControllerRouter};vm.createContext(mixed);
vm.runInContext(`let experimentLoadSequence=0;function profile(modelId){return {modelId,active:false,select(id){trace.push([modelId,id]);this.active=id===modelId;document.querySelector('#laboratory > .lab-layout').hidden=this.active;document.querySelector('#laboratory > .workspace-links').hidden=this.active;$('import-run').hidden=this.active;if(this.active){$('model').value=modelId;$('model-description').textContent=modelId;}return this.active;}};}const burgers=profile('burgers'),sls=profile('sls');const timedView=createLaboratoryControllerRouter([burgers,sls]);const j2View={modelId:'j2',active:false,select(id){trace.push(['j2',id]);this.active=id==='j2';if(this.active)$('model').value='j2';return this.active;}};
${fn('specialLaboratoryActive')}
${fn('selectJ2')}
${fn('selectLaboratory')}
globalThis.api={select:selectLaboratory,states:()=>[j2View.active,burgers.active,sls.active]};`,mixed);
let mixedTransitions=0;
for(const from of ['ordinary','j2','burgers','sls'])for(const to of ['ordinary','j2','burgers','sls']){
 mixed.api.select(from);mixed.trace.length=0;mixed.api.select(to);mixedTransitions++;
 assert.deepEqual(Array.from(mixed.api.states()),['j2','burgers','sls'].map(id=>id===to));checks++;
 for(const id of ['#laboratory > .lab-layout','#laboratory > .workspace-links','import-run']){assert.equal(mixedNode(id).hidden,to!=='ordinary');checks++;}
 const calls=JSON.parse(JSON.stringify(mixed.trace)),activation=calls.findIndex(([name,id])=>name===to&&id===to);
 if(to!=='ordinary'){assert.ok(activation>=0);assert.ok(calls.slice(activation+1).every(([,id])=>id!==null&&id!==false),'No late deactivation may expose ordinary controls after activation.');checks+=2;}
 if(to==='j2'&&from==='j2'){assert.deepEqual(calls,[['j2','j2']]);checks++;}
}
for(const marker of ["setupSlsLaboratory","createLaboratoryControllerRouter","timedView?.supports(entry.id)"]){assert.ok(source.includes(marker));checks++;}
assert.ok(!source.includes('entry.timedView'));assert.ok(!source.includes('timedView?.modelId'));checks+=2;
console.log(JSON.stringify({passed:true,checks,transitionCalls:11+mixedTransitions,compiledCalls:0,networkCalls:0,scope:'Exact extracted coordinator and delayed-import source under a DOM/profile mock plus the real committed timed router and static hook/async guards; real module/browser/package evidence remains parent-owned.'},null,2));
