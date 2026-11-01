import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {validateReview,renderReview} from '../web/reporting-review.mjs';
const data=JSON.parse(execFileSync('python3',['-B','-c','import json; from pathlib import Path; from tools.build_reporting_review import projection; print(json.dumps(projection(Path.cwd())))'],{encoding:'utf8'}));
test('exact scoped review retains seven claims and mandatory qualifications',()=>{assert.equal(validateReview(data),data);assert.equal(data.claims.length,7);assert.ok(data.qualifications.some(x=>x.includes('FAIL')));});
test('unsafe links, broad approval and incomplete qualifications reject',()=>{
 for(const mutate of [v=>v.decision_url='javascript:alert(1)',v=>v.model_admission=true,v=>v.redistribution_permission=true,v=>v.claims.pop(),v=>v.claims[0].id='C2',v=>v.qualifications=[],v=>v.decision_sha256='bad']){const v=structuredClone(data);mutate(v);assert.throws(()=>validateReview(v));}
});
test('renderer exposes exact source links and qualifications using text only',()=>{
 class Node{constructor(){this.children=[];this.textContent='';}replaceChildren(...c){this.children=c;}append(...c){this.children.push(...c);}}
 const nodes=new Map();const doc={getElementById:id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);},createElement:()=>new Node(),createTextNode:text=>({textContent:text})};
 const v=structuredClone(data);v.claims[0].reason='<img src=x onerror=alert(1)>';renderReview(doc,v);
 assert.match(nodes.get('reporting-review-status').textContent,/Model admission.*remain open/);assert.match(nodes.get('reporting-review-scope').textContent,/does not review.*pressure3/);
 assert.equal(nodes.get('reporting-review-claims').children[0].textContent.includes('<img'),true);assert.equal(nodes.get('reporting-review-qualifications').children.length,v.qualifications.length);
 assert.equal(nodes.get('reporting-review-links').children[0].href,v.review_url);
});
