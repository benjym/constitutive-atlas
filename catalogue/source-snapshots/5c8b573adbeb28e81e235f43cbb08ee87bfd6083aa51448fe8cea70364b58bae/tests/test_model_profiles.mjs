import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import vm from 'node:vm';
import {modelProfile,modelProfileSection,validateModelProfiles} from '../web/model-profiles.mjs';
const root=new URL('../',import.meta.url);
const read=path=>JSON.parse(readFileSync(new URL(path,root),'utf8'));
const entries=read('catalogue/manifest.json').models;
const definitions=readdirSync(new URL('models/',root)).filter(name=>name.endsWith('.json')).map(name=>read('models/'+name));
class Element{
  constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.textContent='';this.open=false;this.scrollTop=0;}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=[...nodes];}
}
const document={createElement:tag=>new Element(tag),createTextNode:text=>Object.assign(new Element('#text'),{textContent:text})};
const flatten=node=>[node,...node.children.flatMap(flatten)];
const text=node=>flatten(node).map(item=>item.textContent).join(' ');
test('all catalogue entries have source-backed profiles and valid related identities',()=>{
  assert.equal(validateModelProfiles(entries,definitions),entries.length);
  assert.equal(validateModelProfiles([...entries,...definitions.filter(model=>!entries.some(entry=>entry.id===model.id))],definitions),entries.length+definitions.filter(model=>!entries.some(entry=>entry.id===model.id)).length);
  assert.equal(modelProfile('__proto__'),null);assert.equal(modelProfile('constructor'),null);
  for(const entry of entries)for(const path of modelProfile(entry.id).contentSources)assert.ok(readFileSync(new URL(path,root)).length,entry.id+': '+path);
  assert.throws(()=>validateModelProfiles([...entries,{id:'new-unexplained-model'}]),/Missing public model profile/);
});
test('every profile renders its own mechanics without altering definitions or promising candidate runs',()=>{
  const before=JSON.stringify(definitions);
  for(const entry of entries){
    const spec=definitions.find(model=>model.id===entry.id)??entry,profile=modelProfile(entry.id),section=modelProfileSection(document,spec,{catalogue:entries});
    const rendered=text(section);assert.ok(rendered.includes(profile.summary),entry.id);
    assert.ok(rendered.includes(profile.scope),entry.id);assert.ok(rendered.includes(profile.preparation),entry.id);
    assert.doesNotMatch(rendered,/Recorded description|reviewer run|SHA-256|Independent agent checklist/i);
    const equations=flatten(section).filter(node=>node.tagName==='DETAILS');assert.ok(equations.every(node=>!node.open));
    if(!spec.parameters)assert.doesNotMatch(rendered,/Example value|Not supplied/);
  }
  assert.equal(JSON.stringify(definitions),before);
  assert.doesNotMatch(text(modelProfileSection(document,{id:'maxwell-itasca900-zero-spin-ode'})),/overconsolidation|dimensionless example values/i);
  assert.doesNotMatch(text(modelProfileSection(document,{id:'sanisand-2004'})),/Choose Drained|Example value/);
});
test('public parameter examples use packaged values and physical units',()=>{
  const elastic=definitions.find(model=>model.id==='linear-elastic'),modified=structuredClone(elastic);modified.parameters.E.default=123456;
  assert.match(text(modelProfileSection(document,modified)),/123456 · Pa/);
  const sand=text(modelProfileSection(document,definitions.find(model=>model.id==='hypoplastic-sand-vw96')));
  assert.match(sand,/rad/);assert.match(sand,/Pa/);
  assert.throws(()=>validateModelProfiles(entries,[{...elastic,parameters:{nu:elastic.parameters.nu}}]),/unknown parameter E/);
});

// Exercise the actual detail-dialog hook: every flavour puts the old records
// inside a closed disclosure, while related-profile navigation resets scroll.
const app=readFileSync(new URL('web/app.js',root),'utf8');
const hook=app.slice(app.indexOf('function showCatalogueModel('),app.indexOf('function download('));
for(const id of ['modified-cam-clay','maxwell-itasca900-zero-spin-ode','sanisand-2004','original-cam-clay']){
  test('actual dialog presents the profile first with technical records closed: '+id,()=>{
    const nodes=new Map(),$=id=>{if(!nodes.has(id))nodes.set(id,new Element('div'));return nodes.get(id);};
    $('catalogue-detail-body').scrollTop=200;$('catalogue-dialog').showModal=()=>{$('catalogue-dialog').open=true;};
    const context={$,document,modelProfile,modelProfileSection,catalogue:entries,j2View:null,timedView:null,
      timedLaboratoryRoute:()=>null,refreshCatalogueStatus:()=>{},technicalReviewLinks:()=>new Element('p'),element:(tag,value,className)=>Object.assign(new Element(tag),{textContent:value??'',className}),
      recordedDescription:value=>value,formulationSection:()=>new Element('section'),evidenceSection:()=>new Element('section'),applicabilitySection:()=>new Element('section'),
      evidenceIndex:null,evidenceState:'loaded',applicabilityMatrix:null,applicabilityState:'loaded',definitionLink:()=>new Element('a'),catalogueModelHash:id=>'#catalogue/'+id,URL};
    vm.runInNewContext(hook+';showCatalogueModel(entry,spec);',{...context,entry:entries.find(entry=>entry.id===id)??{id,name:modelProfile(id).title,family:'Viscoelasticity'},spec:definitions.find(model=>model.id===id)});
    const body=$('catalogue-detail-body');assert.equal(body.children[0].className,'model-profile');
    assert.equal(body.children[1].tagName,'DETAILS');assert.equal(body.children[1].open,false);assert.equal(body.scrollTop,0);
    assert.ok(text(body.children[1]).includes('Technical details, implementation and checks'));
    assert.ok(text(body.children[0]).includes(modelProfile(id).summary));
    if(id==='sanisand-2004'||id==='original-cam-clay')assert.equal($('catalogue-explore').hidden,true);
  });
}
