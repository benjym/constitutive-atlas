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
  assert.equal(catalogueRoute('#recorded').page,'laboratory');
  for(const page of ['catalogue','methods'])assert.equal(catalogueRoute('#'+page).page,page);
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

const review=()=>({catalogue_id:'example',id:'example-source-v1',record_path:'catalogue/reviews/example.json',record_sha256:'c'.repeat(64),definition_path:'models/example.json',definition_sha256:'a'.repeat(64),definition_current:true,status:'pending',independent:false,reviewer:null,reviewed_at:null,dossier:'docs/models/example.md',evidence_ids:['example-failed-v1'],unresolved:['Source ambiguity <b>remains</b>.']});
test('pending source review is separate from a passed numerical outcome and preserves literal questions',()=>{
  const x=index();x.records[0].outcome='passed';x.reviews=[review()];validateEvidenceIndex(x);const section=evidenceSection(document,'example',x);
  assert.match(text(section),/Recorded source-review status: pending/);assert.match(text(section),/Scientific decision pending/);assert.match(text(section),/Independence declared: no/);assert.match(text(section),/Recorded outcome: passed/);assert.match(text(section),/Source ambiguity <b>remains<\/b>/);assert.equal(flatten(section).some(x=>x.tag==='b'),false);
  assert.ok(flatten(section).some(x=>x.href==='./evidence-records/catalogue/reviews/example.json'));
});
test('historical acceptance and current pending review both remain visible without selecting a decision',()=>{
  const x=index(),old=review();Object.assign(old,{id:'old',record_path:'catalogue/reviews/old.json',status:'accepted',independent:true,reviewer:'Synthetic fixture',reviewed_at:'2026-10-30',unresolved:[],definition_current:false});x.reviews=[old,review()];validateEvidenceIndex(x);const shown=text(evidenceSection(document,'example',x));
  assert.match(shown,/status: accepted/);assert.match(shown,/Historical definition/);assert.match(shown,/status: pending/);assert.match(shown,/All retained revisions are shown/);
});
test('malformed, unsigned and unsafe review states reject; unindexed and absent remain distinct',()=>{
  for(const patch of [{status:'passed'},{record_path:'../review.json'},{dossier:'https://example.test/a'},{unresolved:[]},{independent:1},{status:'accepted',unresolved:[]},{reviewer:undefined},{reviewed_at:''}]){
    const x=index();x.reviews=[Object.assign(review(),patch)];assert.throws(()=>validateEvidenceIndex(x));
  }
  const duplicate=index();duplicate.reviews=[review(),review()];assert.throws(()=>validateEvidenceIndex(duplicate));
  assert.match(text(evidenceSection(document,'example',index())),/Source reviews were not indexed/);
  const empty=index();empty.reviews=[];assert.match(text(evidenceSection(document,'example',empty)),/No formal source-review record/);
});
