// Explicit test allocation; never filter models or infer exceptions from failures.
import assert from'node:assert/strict';
import {readFileSync,realpathSync}from'node:fs';
import {createHash}from'node:crypto';
import {resolve,dirname,sep}from'node:path';
import {fileURLToPath}from'node:url';
import {validatePolicy as validateSupportedPolicy}from'./test_supported_package.mjs';
import {laboratoryStress,validateScopedLaboratory}from'../web/laboratory-scope.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const hash=x=>createHash('sha256').update(x).digest('hex');
const keys=(x,names)=>{assert.ok(x&&typeof x==='object'&&!Array.isArray(x));assert.deepEqual(Object.keys(x).sort(),[...names].sort());};
export function validateProfileAllocation(policy,supported,cases,catalogue,dependencies){
 keys(policy,['schema_version','kind','id','supported_policy','cases','case_count','legacy_contract_rejections','parity_relative_tolerance','limitations']);assert.equal(policy.schema_version,'0.1');assert.equal(policy.kind,'laboratory-profile-test-allocation');assert.match(policy.id,/^[a-z][a-z0-9-]*$/);assert.equal(policy.parity_relative_tolerance,1e-10,'Do not relax the existing current-profile parity budget');assert.ok(Array.isArray(policy.limitations)&&policy.limitations.length);
 for(const p of [policy.supported_policy,policy.cases]){keys(p,['path','sha256']);assert.ok(typeof p.path==='string'&&!p.path.startsWith('/')&&!p.path.split('/').some(x=>!x||x==='..'||x==='.')&&!p.path.includes('\\'));assert.match(p.sha256,/^[a-f0-9]{64}$/);}
 validateSupportedPolicy(supported,catalogue,dependencies);assert.ok(Array.isArray(policy.legacy_contract_rejections));const rejected=new Set();
 for(const e of policy.legacy_contract_rejections){keys(e,['model','message']);assert.ok(!rejected.has(e.model));rejected.add(e.model);assert.equal(e.message,'legacy laboratory contract requires effective stress');}
 const total=catalogue.models.filter(m=>laboratoryStress(m).scope==='total').map(m=>m.id).sort();assert.deepEqual([...rejected].sort(),total,'Every total model needs an explicit legacy rejection; no effective model may be rejected');
 assert.ok(Number.isInteger(policy.case_count)&&policy.case_count>0);assert.ok(Array.isArray(cases));assert.equal(cases.length,policy.case_count);const ids=new Set(),covered=new Set(),successful=new Set(),negative=[];
 for(const c of cases){keys(c,['id','specification','expected_ok','expected_message','expected_points']);assert.ok(typeof c.id==='string'&&c.id.length&&!ids.has(c.id));ids.add(c.id);validateScopedLaboratory(c.specification,catalogue);assert.equal(typeof c.expected_ok,'boolean');assert.ok(Number.isInteger(c.expected_points));covered.add(c.specification.model);
  if(c.expected_ok){successful.add(c.specification.model);assert.equal(c.expected_message,'');assert.equal(c.expected_points,c.specification.steps+1);}
  else{const declaration=supported.declared_failures.find(e=>e.model===c.specification.model);assert.ok(declaration,'Unreviewed negative case');assert.deepEqual(c.specification,declaration.ordinary_specification);assert.equal(c.expected_message,declaration.message);assert.equal(c.expected_points,declaration.committed_points);negative.push(c.specification.model);}
 }
 const all=catalogue.models.map(m=>m.id).sort();assert.deepEqual([...covered].sort(),all,'Scoped cases must cover every model');assert.deepEqual([...successful].sort(),all,'Every model needs a successful scoped case');assert.deepEqual(negative.sort(),supported.declared_failures.map(e=>e.model).sort());
 return {policy,supported,cases};
}
export function loadProfileAllocation(file,catalogue){
 const read=name=>{const target=realpathSync(resolve(root,name));assert.ok(target.startsWith(root+sep),'Policy path escapes source root');return readFileSync(target,'utf8');};
 const policy=JSON.parse(readFileSync(file,'utf8'));for(const pin of [policy.supported_policy,policy.cases])assert.equal(hash(read(pin.path)),pin.sha256,'Allocation input changed');const supported=JSON.parse(read(policy.supported_policy.path)),cases=JSON.parse(read(policy.cases.path));
 for(const model of catalogue.models)assert.deepEqual(model,JSON.parse(read('models/'+model.id+'.json')),'Compiled definition differs from current source');
 return validateProfileAllocation(policy,supported,cases,catalogue,{definitionHash:id=>hash(read('models/'+id+'.json')),readEvidence:read});
}
export function assertDeclaredOrdinaryFailure(allocation,s,result){
 const e=allocation.supported.declared_failures.find(e=>e.model===s.model);assert.ok(e,'No declared ordinary failure');assert.deepEqual(s,e.ordinary_specification);assert.equal(result.ok,false,'Known ordinary limitation changed; review policy');assert.equal(result.message,e.message);assert.equal(result.points.length,e.committed_points);assert.deepEqual(result.points[0].state,s.initial);return e;
}
