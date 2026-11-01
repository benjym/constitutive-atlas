// Execute actual app routing/selection hooks with inert material controllers.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {createLaboratoryControllerRouter} from '../web/laboratory-controller-router.mjs';
import {catalogueRoute} from '../web/catalogue.mjs';
const source=readFileSync(process.argv[2]||new URL('../web/app.js',import.meta.url),'utf8');
const ids=Object.keys(JSON.parse(readFileSync(new URL('../catalogue/laboratory-package-policy.json',import.meta.url),'utf8')).models);
function fn(name){const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);const line=source.indexOf('\n',start);if(source.slice(start,line).endsWith('}'))return source.slice(start,line);return source.slice(start,source.indexOf('\n}',start)+2);}
const nodes=new Map();
const node=id=>{if(!nodes.has(id))nodes.set(id,{value:'',hidden:false,textContent:'',open:false,replaceChildren(){},append(){},focus(){}});return nodes.get(id);};
const $=id=>['model','import-run','model-description','model-family','model-status','model-sources','catalogue-dialog','breadcrumb','catalogue-detail-body'].includes(id)?node(id):null;
const c={$,document:{querySelector:node,querySelectorAll:()=>[]},location:{hash:''},window:{scrollTo(){}},requestAnimationFrame:f=>f(),URLSearchParams,encodeURIComponent,catalogueRoute,createLaboratoryControllerRouter,ids,trace:[],toasts:[],element:()=>node('element')};
vm.createContext(c);
vm.runInContext([
"let experimentLoadSequence=0,models=ids.map(id=>({id})),catalogue=[],runs=0,populations=0,cancels=0;",
"function profile(modelId){return {modelId,active:false,select(id){this.active=id===modelId;document.querySelector('#laboratory > .lab-layout').hidden=this.active;document.querySelector('#laboratory > .workspace-links').hidden=this.active;$('import-run').hidden=this.active;if(this.active)$('model').value=modelId;return this.active;}};}",
"const timedView=createLaboratoryControllerRouter(['burgers','sls','maxwell','norsand'].map(profile)),j2View=profile('j2');",
"function cancel(){++cancels;}function populate(){++populations;}function simulate(){++runs;}",
"function toast(message){toasts.push(message);}function showCatalogueModel(){throw Error('Unexpected catalogue detail');}",
...['specialLaboratoryActive','selectJ2','selectLaboratory','activateLaboratoryModel','route'].map(fn),
"globalThis.api={route,activate:activateLaboratoryModel,metrics:()=>({runs,populations,cancels}),states:()=>[j2View.active,timedView.active]};"
].join('\n'),c);
const onChange=source.slice(source.indexOf("$('model').onchange="),source.indexOf(";$('protocol').onchange="))+';';
vm.runInContext(onChange,c);
let checks=0;
function route(id,options){c.location.hash='#laboratory?model='+encodeURIComponent(id);c.api.route(options);}
for(const id of ids){
 node('model').value='initial-sentinel';const before=c.api.metrics();
 route(id,{initial:true});assert.equal(node('model').value,id);assert.equal(c.api.metrics().runs,before.runs);assert.equal(c.api.metrics().populations,before.populations+1);checks+=3;
 const same=c.api.metrics();c.api.route();assert.deepEqual(c.api.metrics(),same);checks++;
}
const a=ids[0],b=ids.find(id=>id!==a);
route(a);const before=c.api.metrics();node('model').value=b;node('model').onchange();
assert.equal(c.location.hash,'laboratory?model='+encodeURIComponent(b));assert.equal(c.api.metrics().runs,before.runs+1);
const settled=c.api.metrics();c.api.route();assert.deepEqual(c.api.metrics(),settled);checks+=3;
for(const id of [a,b,a]){route(id);assert.equal(node('model').value,id);checks++;}
for(const query of ['model=missing-model','model=','model=__proto__','model='+a+'&model='+b]){
 const before=c.api.metrics(),selected=node('model').value,count=c.toasts.length;
 c.location.hash='#laboratory?'+query;c.api.route();
 assert.equal(node('model').value,selected);assert.deepEqual(c.api.metrics(),before);assert.equal(c.toasts.length,count+1);checks+=3;
}
const special=['j2','burgers','sls','maxwell','norsand'];
for(const from of [a,...special])for(const to of [b,...special]){
 route(from);route(to);assert.equal(node('model').value,to);assert.deepEqual(Array.from(c.api.states()),[to==='j2',special.includes(to)&&to!=='j2']);checks+=2;
 for(const id of ['#laboratory > .lab-layout','#laboratory > .workspace-links','import-run']){assert.equal(node(id).hidden,special.includes(to));checks++;}
}
assert.ok(source.includes("if(activateLaboratoryModel(entry.id))location.hash='laboratory?model='+encodeURIComponent(entry.id)"));checks++;
assert.ok(source.includes('route({initial:true});simulate();'));checks++;
console.log(JSON.stringify({passed:true,ordinaryModels:ids.length,specialProfiles:special.length,checks,profileTransitions:36,compiledCalls:0,scope:'Actual source route/dropdown hooks plus real router, inert material views; real browser history/engine evidence separate.'},null,2));
