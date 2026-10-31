import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateApplicability,applicabilitySection} from '../web/applicability-view.mjs';
const fixture=()=>JSON.parse(readFileSync(new URL('../catalogue/applicability/kfs-development-v1.json',import.meta.url)));
class Element{constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.style={};}append(...children){this.children.push(...children);}}
const document={createElement:tag=>new Element(tag)};
const flatten=x=>[x,...x.children.flatMap(flatten)];
const text=x=>flatten(x).map(n=>n.textContent).join(' ');
test('conditional evidence preserves pending eligibility and current/archive limitations',()=>{
 const matrix=validateApplicability(fixture()),section=applicabilitySection(document,'hypoplastic-sand-vw96',matrix);
 assert.match(text(section),/conditional development evidence/);assert.match(text(section),/eligibility: undetermined/);
 assert.match(text(section),/TMD7.*2%/);assert.match(text(section),/archived executable/);assert.match(text(section),/not general current-engine equivalence/);
 const links=flatten(section).filter(x=>x.tag==='a');assert.ok(links.some(x=>x.href==='./models/hypoplastic-sand-vw96.json'));
 assert.ok(links.some(x=>x.href==='./applicability.json'));assert.ok(links.some(x=>x.href.startsWith('./applicability-records/docs/')));
});
test('unassessed pair, absent formulation and unavailable inventory remain distinct',()=>{
 const matrix=validateApplicability(fixture());assert.match(text(applicabilitySection(document,'linear-elastic',matrix)),/Pair assessment: not assessed/);
 assert.match(text(applicabilitySection(document,'candidate',matrix)),/No model–experiment assessment is indexed/);
 assert.match(text(applicabilitySection(document,'candidate',null,'failed')),/could not be loaded/);
 assert.match(text(applicabilitySection(document,'candidate',null)),/Loading applicability/);
});
test('unsafe links, promoted scientific status and ambiguous rows are rejected',()=>{
 for(const mutate of [m=>m.rows[0].model.id='../outside',m=>m.rows[0].model.path='/models/a.json',m=>m.rows[0].model.sha256='bad',m=>m.rows[0].evidence[0].path='docs/../outside',m=>m.dataset.source_url='javascript:alert(1)',m=>m.rows[0].scientific_eligibility='eligible',m=>m.independent_review='accepted',m=>m.rows.push(m.rows[0])]){
  const matrix=fixture();mutate(matrix);assert.throws(()=>validateApplicability(matrix));
 }
});
test('source text remains literal text rather than executable markup',()=>{
 const matrix=fixture();matrix.rows[0].prerequisites=['<img src=x onerror=alert(1)>'];
 const section=applicabilitySection(document,matrix.rows[0].model.id,validateApplicability(matrix));
 assert.match(text(section),/<img/);assert.equal(flatten(section).some(x=>x.tag==='img'),false);
});
