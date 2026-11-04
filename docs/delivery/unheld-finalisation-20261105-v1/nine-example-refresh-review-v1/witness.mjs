import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parity,historicalDifferences,withoutElapsed,journalEngine} from '../nine-example-refresh-plan-v1/collector-core.mjs';
const policy=JSON.parse(fs.readFileSync(new URL('../nine-example-refresh-plan-v1/policy.json',import.meta.url)));let checks=0;
const base={elapsed_ms:1,points:[{state:[1],strain:[0,0,0,0,0,0],p:1,q:0,q_signed:0,u:null,error:0,iterations:0}]};
for(const [name,mutate,reject]of [
 ['physical under budget',x=>x.points[0].p+=5e-11,false],['physical over budget',x=>x.points[0].p+=2e-10,true],['diagnostic exact',x=>x.points[0].iterations=1,true],['extra shape',x=>x.points[0].extra=0,true],['missing shape',x=>delete x.points[0].q,true],['nonfinite',x=>x.points[0].p=NaN,true],['elapsed omitted',x=>x.elapsed_ms=999,false]]){
 const b=structuredClone(base);mutate(b);if(reject)assert.throws(()=>parity(base,b,policy),name);else parity(base,b,policy);checks++;
}
const diffs=historicalDifferences({catalogue_hash:'new',elapsed_ms:2,x:[999],added:true},{catalogue_hash:'old',elapsed_ms:1,x:[1],removed:true});
assert.equal(diffs.length,3);assert.ok(diffs.some(x=>x.old_missing)&&diffs.some(x=>x.current_missing));checks++;
assert.deepEqual(withoutElapsed({nested:{elapsed_ms:1,value:2}}),{nested:{value:2}});checks++;
const raw=[];assert.throws(()=>journalEngine({ccall(){throw Error('original');}},x=>raw.push(x)).ccall('inert'));assert.equal(raw[1].error.message,'original');checks++;
console.log(JSON.stringify({status:'PASS',independent_boundary_witnesses:checks,material_calls:0,actual_generated_module_imports:0}));
