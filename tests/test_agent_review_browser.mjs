import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEvidenceIndex,evidenceSection} from '../web/catalogue.mjs';
const ids=['source_provenance','equation_fidelity','conventions_dimensions','initialization_domain','integration_transactions','independent_numerical_evidence','backend_delivery','applicability_claims','reproducibility_rights'];
const review=()=>({catalogue_id:'elastic',id:'elastic-agent-v1',record_path:'catalogue/agent-reviews/elastic-agent-v1.json',record_sha256:'a'.repeat(64),definition_path:'models/elastic.json',definition_sha256:'b'.repeat(64),current_definition_sha256:'b'.repeat(64),definition_record_path:'catalogue/agent-reviews/definitions/elastic-agent-v1.json',definition_current:true,status:'accepted',reviewer:{kind:'agent',name:'Reviewer <script>literal</script>',run_id:'review-run',independence_basis:'Separate run'},created_at:'2026-11-01',scope:'Bounded elastic scope.',limitations:['No experimental validation.'],blocking_findings:[],checklist:ids.map(id=>({id,outcome:'pass',reason:'Checked fixture',evidence:['receipt.json#locator']})),registered_approval_id:'elastic-agent-v1-approval'});
const index=()=>({schema_version:'0.1',kind:'catalogue-evidence-index',coverage_note:'Integrity only.',records:[],reviews:[],agent_reviews:[review()]});
class Element{constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];}append(...children){this.children.push(...children);}}
const document={createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
const flatten=node=>[node,...node.children.flatMap(flatten)];
const text=node=>flatten(node).map(x=>x.textContent).join(' ');

test('accepted exact registry approval shows scope, declarations, limits and original JSON safely',()=>{
  const section=evidenceSection(document,'elastic',validateEvidenceIndex(index()));
  const shown=text(section);
  assert.match(shown,/Recorded agent-review status: accepted/);assert.match(shown,/Registered project approval for this exact definition and scope/);
  assert.match(shown,/Bounded elastic scope/);assert.match(shown,/No experimental validation/);assert.match(shown,/does not authenticate the reviewer/);
  assert.equal(flatten(section).some(x=>x.tag==='script'),false);assert.match(shown,/<script>literal<\/script>/);
  assert.deepEqual(flatten(section).filter(x=>x.tag==='a').map(x=>x.href),['./evidence.json','./evidence-records/catalogue/agent-reviews/elastic-agent-v1.json','./evidence-records/catalogue/agent-reviews/definitions/elastic-agent-v1.json','./evidence-records/catalogue/approved-models.json']);
});
test('historical acceptance explicitly excludes approval of changed current bytes',()=>{
  const x=index();x.agent_reviews[0].definition_current=false;x.agent_reviews[0].current_definition_sha256='c'.repeat(64);
  const section=evidenceSection(document,'elastic',validateEvidenceIndex(x));
  assert.match(text(section),/Historical registered approval; it does not approve the current definition/);
  assert.doesNotMatch(text(section),/Registered project approval for this exact definition and scope/);
  assert.equal(flatten(section).some(x=>x.href==='./models/elastic.json'),false);
});
test('accepted review without registry entry and historical pending source reviews remain distinct',()=>{
  const x=index();x.agent_reviews[0].registered_approval_id=null;
  x.reviews=[{catalogue_id:'elastic',id:'old-source',record_path:'catalogue/reviews/old.json',record_sha256:'d'.repeat(64),definition_path:'models/elastic.json',definition_sha256:'b'.repeat(64),definition_current:true,status:'pending',independent:false,reviewer:null,reviewed_at:null,dossier:'docs/models/elastic.md',evidence_ids:[],unresolved:['Old pending question.']}];
  const shown=text(evidenceSection(document,'elastic',validateEvidenceIndex(x)));
  assert.match(shown,/No matching registry approval/);assert.match(shown,/agent-review status: accepted/);assert.match(shown,/source-review status: pending/);assert.match(shown,/Old pending question/);
});
test('unsafe paths, incomplete decisions and mismatched current identity fail closed',()=>{
  for(const patch of [{record_path:'../review.json'},{definition_record_path:'javascript:alert(1)'},{definition_record_path:'models/elastic.json'},{reviewer:null},{current_definition_sha256:'c'.repeat(64)},{definition_current:false},{scope:''},{limitations:[]},{registered_approval_id:1},{status:'pending'},{blocking_findings:['Unresolved']}]){
    const x=index();Object.assign(x.agent_reviews[0],patch);assert.throws(()=>validateEvidenceIndex(x));
  }
  for(const mutate of [r=>r.checklist.pop(),r=>r.checklist[0].outcome='fail',r=>r.checklist[0].outcome='not-applicable',r=>r.checklist[0]=r.checklist[1]]){
    const x=index();mutate(x.agent_reviews[0]);assert.throws(()=>validateEvidenceIndex(x));
  }
  const duplicate=index();duplicate.agent_reviews.push(review());assert.throws(()=>validateEvidenceIndex(duplicate));
});
test('unindexed versus no agent review and backend-only inapplicability remain explicit',()=>{
  const x=index();x.agent_reviews=[];assert.match(text(evidenceSection(document,'elastic',x)),/No independent-agent checklist/);
  delete x.agent_reviews;assert.match(text(evidenceSection(document,'elastic',x)),/were not indexed/);
  const y=index();y.agent_reviews[0].checklist.find(r=>r.id==='backend_delivery').outcome='not-applicable';assert.equal(validateEvidenceIndex(y),y);
});
