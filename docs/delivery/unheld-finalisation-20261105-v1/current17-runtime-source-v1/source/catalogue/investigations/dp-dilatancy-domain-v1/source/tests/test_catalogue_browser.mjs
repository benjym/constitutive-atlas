import test from 'node:test';
import assert from 'node:assert/strict';
import {catalogueHash,catalogueRoute,validateEvidenceIndex,evidenceSection} from '../web/catalogue.mjs';
const record={catalogue_id:'example',definition_path:'models/research/example.json',definition_sha256:'a'.repeat(64),definition_current:true,record_path:'catalogue/evidence/example.json',record_sha256:'b'.repeat(64),kind:'research-manifest',outcome:null,scope:'Seven-state rates only.',limitations:['No integration or experimental validation.']};
const index=()=>({schema_version:'0.1',kind:'catalogue-evidence-index',coverage_note:'Partial index; original receipts retained.',records:[structuredClone(record)]});
class Element{
  constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];}
  append(...children){this.children.push(...children);}
}
const document={createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
const flatten=node=>[node,...node.children.flatMap(flatten)];
const text=node=>flatten(node).map(x=>x.textContent).join(' ');
test('deep links round-trip identifiers and retain project-relative hash routes',()=>{
  for(const id of ['linear-elastic','oblique / variant','é last'])assert.equal(catalogueRoute(catalogueHash(id)).modelId,id);
  assert.equal(catalogueRoute('#catalogue/example').page,'catalogue');
  assert.deepEqual(catalogueRoute('#catalogue/%E0%A4'),{page:'catalogue',modelId:null,invalid:true});
  assert.equal(catalogueRoute('#catalogue/').invalid,true);
});
test('existing navigation and laboratory anchors retain their page',()=>{
  for(const page of ['catalogue','methods','recorded'])assert.equal(catalogueRoute('#'+page).page,page);
  for(const hash of ['','#laboratory','#equations','#unknown'])assert.equal(catalogueRoute(hash).page,'laboratory');
});
test('index validation rejects unsafe links, missing identity and ambiguous duplicate records',()=>{
  assert.equal(validateEvidenceIndex(index()).records.length,1);
  for(const patch of [{record_path:'../outside.json'},{record_path:'https://example.test/a'},{definition_path:'other.json'},{definition_path:'/models/a.json'},{definition_sha256:'bad'},{definition_current:1},{limitations:'none'},{scope:null},{outcome:undefined}]){
    const x=index();Object.assign(x.records[0],patch);assert.throws(()=>validateEvidenceIndex(x));
  }
  const x=index();x.records.push(structuredClone(x.records[0]));assert.throws(()=>validateEvidenceIndex(x));
});
test('research evidence states scope and limits without promising browser execution',()=>{
  const section=evidenceSection(document,'example',validateEvidenceIndex(index()));
  assert.match(text(section),/Seven-state rates only/);assert.match(text(section),/does not add the formulation to the browser solver/);
  assert.match(text(section),/does not rerun numerical studies/);assert.match(text(section),/No integration or experimental validation/);
  assert.deepEqual(flatten(section).filter(x=>x.tag==='a').map(x=>x.href),['./evidence.json','./evidence-records/catalogue/evidence/example.json','./models/research/example.json']);
});
test('historical definitions never link current bytes as the matched definition',()=>{
  const x=index();x.records[0].definition_current=false;
  const section=evidenceSection(document,'example',x);
  assert.match(text(section),/Historical definition/);assert.equal(flatten(section).filter(x=>x.tag==='a').length,2);
});
test('failed investigations remain visible',()=>{
  const x=index();x.records[0].kind='numerical-evidence';x.records[0].outcome='failed';
  assert.match(text(evidenceSection(document,'example',x)),/Recorded outcome: failed/);
});
test('missing records and fetch failures have distinct honest states',()=>{
  assert.match(text(evidenceSection(document,'absent',index())),/does not establish that an implementation is absent/);
  assert.match(text(evidenceSection(document,'example',null,'failed')),/could not be loaded/);
  assert.match(text(evidenceSection(document,'example',null)),/Loading evidence index/);
});
test('source text stays text even when it contains markup',()=>{
  const x=index();x.records[0].scope='<script>alert(1)</script>';
  const section=evidenceSection(document,'example',x);
  assert.match(text(section),/<script>/);assert.equal(flatten(section).some(x=>x.tag==='script'),false);
});
