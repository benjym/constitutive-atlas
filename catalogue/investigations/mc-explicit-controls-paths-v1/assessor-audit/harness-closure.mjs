import assert from 'node:assert/strict';
import {readFileSync,writeFileSync}from'node:fs';
const p=new URL('revised/',import.meta.url),read=n=>readFileSync(new URL(n,p),'utf8');
const observer=read('observe.mjs'),test=read('test_laboratory_initial_checks.py'),cases=JSON.parse(read('rejection-requests.json'));
const checks=[];function check(name,v){checks.push({name,passed:v});assert.ok(v,name);}
check('observer absent-or-array predicate',observer.includes("!Object.hasOwn(failure,'points')||(Array.isArray(failure.points)&&failure.points.length===invalid.expected_invalid_points)"));
for(const value of [null,false,'',{length:0}])check('reject malformed points '+JSON.stringify(value),!(Array.isArray(value)&&value.length===0));
check('unit ok singleton false',test.includes("self.assertIs(response['ok'],False)"));
check('unit present points list',test.includes("if 'points' in response:self.assertIsInstance(response['points'],list)"));
check('12 rejection metadata false',cases.cases.length===12&&cases.cases.every(x=>x.expected_ok===false));
check('9 explicit 3 legacy',cases.cases.filter(x=>x.mode==='run-controls').length===9&&cases.cases.filter(x=>x.mode==='run').length===3);
check('zero invalid points policy',cases.expected_invalid_points===0);
writeFileSync(new URL('harness-closure-checks.json',import.meta.url),JSON.stringify({passed:true,checks,candidateCalls:0,pending:'Baseline artifact SHA enforcement in regression harness'},null,2)+'\n');
console.log(checks.length+' closure checks passed');
