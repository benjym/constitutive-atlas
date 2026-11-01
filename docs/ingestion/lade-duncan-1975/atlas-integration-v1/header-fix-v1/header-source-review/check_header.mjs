// Actual app/implicit/Maxwell selection functions, inert run callbacks and pure DOM.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import{createHash}from'node:crypto';
import{createLaboratoryControllerRouter}from'../../../../../../web/laboratory-controller-router.mjs';
import{catalogueRoute}from'../../../../../../web/catalogue.mjs';
const appPath=process.argv[2],source=fs.readFileSync(appPath,'utf8'),ip=fs.readFileSync('web/implicit-path-laboratory.mjs','utf8'),maxwell=fs.readFileSync('web/maxwell-laboratory.mjs','utf8');
function fn(text,name){const start=text.indexOf('function '+name+'(');assert.ok(start>=0,name);const eol=text.indexOf('\n',start);return text.slice(start,text.slice(start,eol).endsWith('}')?eol:text.indexOf('\n}',start)+2);}
const ipMethod=ip.match(/select\(id,\{auto=true\}=\{\}\)\{[^\n]+?return active;\}/)?.[0];assert.ok(ipMethod);
const maxMethod=maxwell.slice(maxwell.indexOf('  function select(id,'),maxwell.indexOf('\n  return {modelId,select,'));assert.ok(maxMethod.includes('Maxwell continuum'));
class Node{constructor(){this.children=[];this.textContent='';this.value='';this.hidden=false;this.open=false;}append(...ns){this.children.push(...ns);}replaceChildren(...ns){this.children=[...ns];}scrollIntoView(){}}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);};
const id='lade-duncan-1975-midpoint-elastic-eq19-gap-v4';node('model').value='linear-elastic';node('model-description').textContent='stale hypoplastic';node('model-family').textContent='hypoplasticity';node('model-status').textContent='transcribed';
const context={$:node,document:{querySelector:node,querySelectorAll:()=>[],createElement:()=>new Node()},URL,URLSearchParams,location:{hash:''},window:{scrollTo(){}},requestAnimationFrame:f=>f(),createLaboratoryControllerRouter,catalogueRoute,id};vm.createContext(context);
vm.runInContext(`let experimentLoadSequence=0;let evidenceIndex=null,models=[{id:'linear-elastic',description:'Linear ordinary description',family:'Elasticity',status:'transcribed',sources:[{url:'https://example.test/ordinary',role:'Source',locator:'1'}]}],catalogue=[];
function recordedDescription(s){return s;}function registeredModelReview(){return false;}function cancel(){}function simulate(){}function toast(){}function showCatalogueModel(){}function specialLaboratoryActive(){return j2View.active||timedView.active;}
${fn(source,'element')}\n${fn(source,'model')}\n${fn(source,'sourceLinks')}\n${fn(source,'definitionLink')}\n${fn(source,'refreshModelSummary')}
// Ordinary populate projection: exact unchanged summary/family/source statements;
// routing suite separately verifies ordinary populate is called.
function populate(){const m=model();refreshModelSummary();$('model-family').textContent=m.family;const sources=$('model-sources');sources.replaceChildren();sourceLinks(sources,m.sources);sources.append(definitionLink(m.id));}
function implicit(){let active=false;const modelId=id,runner={cancel(){}},panel=new Object(),ordinary=new Object(),links=new Object();function cancelOrdinary(){}function run(){}return{modelId,get active(){return active;},${ipMethod}};}
function maxwellController(){let active=false;const modelId='maxwell-itasca900',runner={cancel(){}},panel=new Object(),ordinary=new Object(),links=new Object();function cancelOrdinary(){}function run(){}${maxMethod}\nreturn{modelId,select,get active(){return active;}};}
const j2View={modelId:'j2',active:false,select(id){this.active=id===this.modelId;return this.active;}};const timedView=createLaboratoryControllerRouter([implicit(),maxwellController()]);
${fn(source,'selectJ2')}\n${fn(source,'selectLaboratory')}\n${fn(source,'activateLaboratoryModel')}\n${fn(source,'route')}
globalThis.api={activate:activateLaboratoryModel,route,refresh:refreshModelSummary};`,context);
function snapshot(){return{selected:node('model').value,description:node('model-description').textContent,family:node('model-family').textContent,status:node('model-status').textContent,links:node('model-sources').children.map(row=>row.href||row.children[0]?.href)};}
const snapshots=[];
context.location.hash='#laboratory?model='+id;context.api.route({initial:true});snapshots.push({action:'initial Lade deeplink',...snapshot()});
context.api.refresh();assert.deepEqual(snapshot(),Object.fromEntries(Object.entries(snapshots[0]).filter(([k])=>k!=='action')));
context.api.activate('maxwell-itasca900');snapshots.push({action:'Maxwell switch',...snapshot()});assert.match(snapshot().description,/Maxwell continuum/);assert.equal(snapshot().family,'Linear viscoelasticity');assert.deepEqual(snapshot().links,['./engine-maxwell/review.html']);
context.api.activate('linear-elastic');snapshots.push({action:'ordinary switch',...snapshot()});assert.equal(snapshot().description,'Linear ordinary description');assert.equal(snapshot().family,'Elasticity');assert.deepEqual(snapshot().links,['https://example.test/ordinary','./models/linear-elastic.json']);
context.api.activate(id);snapshots.push({action:'Lade dropdown equivalent activation',...snapshot()});
if(source.includes("if(active&&id==='"+id+"')")){
 for(const s of[snapshots[0],snapshots.at(-1)]){assert.match(s.description,/Lade–Duncan \(1975\)/);assert.match(s.description,/compression-positive total mechanical stress/);assert.match(s.description,/Custom paths remain exploratory/);assert.equal(s.family,'Soil elastoplasticity');assert.equal(s.status,'Approved bounded numerical scope');assert.deepEqual(s.links,['https://doi.org/10.1061/AJGEB6.0000204','./engine-implicit-path/review.json','./engine-implicit-path/approval.json','./engine-implicit-path/'+id+'.json']);}
}
console.log(JSON.stringify({passed:true,source:appPath,sha256:createHash('sha256').update(source).digest('hex'),snapshots,compiledCalls:0,scope:'Pure actual special-controller selection and app routing; ordinary populate projection only; actual browser qualification separate'},null,2));
