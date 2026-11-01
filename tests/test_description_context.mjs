import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {recordedDescription,formulationSection} from '../web/formulation-view.mjs';

const original='Not scientifically reviewed. <script>literal()</script>';
const accepted={catalogue_id:'model',status:'accepted',definition_current:true,registered_approval_id:'approval'};
const index=(...reviews)=>({agent_reviews:reviews});
test('only current registered acceptance adds context, preserving original text',()=>{
  const evidence=index(accepted),before=JSON.stringify(evidence);
  const result=recordedDescription(original,'model',evidence);
  assert.ok(result.endsWith(original));assert.match(result,/see the accepted review for its current scope/);
  assert.equal(JSON.stringify(evidence),before);
  for(const patch of [{catalogue_id:'other'},{status:'pending'},{status:'rejected'},{definition_current:false},{definition_current:undefined},{registered_approval_id:null},{registered_approval_id:''}]){
    assert.equal(recordedDescription(original,'model',index({...accepted,...patch})),original,JSON.stringify(patch));
  }
  for(const evidence of [null,{},index()])assert.equal(recordedDescription(original,'model',evidence),original);
  assert.equal(recordedDescription('','model',index(accepted)),'');
});
test('historical approvals do not hide a current acceptance or confer it on another model',()=>{
  const evidence=index({...accepted,definition_current:false},accepted);
  assert.notEqual(recordedDescription(original,'model',evidence),original);
  assert.equal(recordedDescription(original,'other',evidence),original);
});
class Element{constructor(tag){this.tag=tag;this.children=[];this.textContent='';}append(...nodes){this.children.push(...nodes);}}
const document={createElement:tag=>new Element(tag)};
const flatten=node=>[node,...node.children.flatMap(flatten)];
test('formulation view renders contextual description literally without altering the definition',()=>{
  const spec={id:'model',status:'draft',description:original,parameters:{},state:[]};
  const before=JSON.stringify(spec),nodes=flatten(formulationSection(document,spec,{evidenceIndex:index(accepted)}));
  const description=nodes.find(n=>n.className==='definition-description');
  assert.equal(description.textContent,recordedDescription(original,'model',index(accepted)));
  assert.equal(nodes.some(n=>n.tag==='script'),false);assert.equal(JSON.stringify(spec),before);
  assert.equal(flatten(formulationSection(document,spec)).find(n=>n.className==='definition-description').textContent,original);
});

// Execute the actual application refresh function, with DOM nodes retaining user state.
// This tests the asynchronous handoff without loading a material engine.
const source=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
const refresh=source.slice(source.indexOf('function refreshRecordedDescriptions(){'),source.indexOf('function restoreCatalogueFocus(){'));
function fixture(open=true){
  const note={textContent:original},description={textContent:original},equation={textContent:original};
  const control={value:'1.3831693930553504'},body={scrollTop:137,querySelector:selector=>({'.catalogue-detail-note':note,'.definition-description':description}[selector])};
  const nodes={model:{value:'model'},'model-description':{textContent:original},'equation-content':{querySelector:()=>equation},'catalogue-dialog':{open},'catalogue-detail-body':body};
  const context=vm.createContext({models:[{id:'model',description:original}],catalogue:[{id:'model',note:original}],location:{hash:'#catalogue/model'},catalogueRoute:()=>({modelId:'model'}),evidenceIndex:null,recordedDescription,$:id=>nodes[id]});
  vm.runInContext(refresh,context);
  return {context,nodes,note,description,equation,body,control};
}
test('delayed evidence updates open descriptions without replacing controls or scroll position',()=>{
  const f=fixture();vm.runInContext('refreshRecordedDescriptions()',f.context);assert.equal(f.note.textContent,original);
  f.context.evidenceIndex=index(accepted);vm.runInContext('refreshRecordedDescriptions()',f.context);
  for(const node of [f.note,f.description,f.equation,f.nodes['model-description']])assert.equal(node.textContent,recordedDescription(original,'model',index(accepted)));
  assert.equal(f.control.value,'1.3831693930553504');assert.equal(f.body.scrollTop,137);
  vm.runInContext('refreshRecordedDescriptions()',f.context);assert.equal(f.note.textContent,recordedDescription(original,'model',index(accepted)));
});
test('late historical evidence leaves text unchanged and a closed dialog is untouched',()=>{
  const f=fixture();f.context.evidenceIndex=index({...accepted,definition_current:false});vm.runInContext('refreshRecordedDescriptions()',f.context);assert.equal(f.note.textContent,original);
  const closed=fixture(false);closed.context.evidenceIndex=index(accepted);vm.runInContext('refreshRecordedDescriptions()',closed.context);assert.equal(closed.note.textContent,original);assert.notEqual(closed.equation.textContent,original);
});
