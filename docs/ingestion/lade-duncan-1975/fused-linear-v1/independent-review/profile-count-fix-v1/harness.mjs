import test from'node:test';
import assert from'node:assert/strict';
import {readFileSync,readdirSync}from'node:fs';
import {resolve}from'node:path';
import {createHash}from'node:crypto';
import {validateProfileAllocation,loadProfileAllocation,assertDeclaredOrdinaryFailure}from"file:///Users/bmar5496/code/constitutive-atlas/tools/laboratory_profile_policy.mjs";
const root="/Users/bmar5496/code/constitutive-atlas",read=p=>readFileSync(resolve(root,p),'utf8'),hash=s=>createHash('sha256').update(s).digest('hex');
const policy=JSON.parse(read('catalogue/laboratory-profile-policy.json')),supported=JSON.parse(read(policy.supported_policy.path)),cases=JSON.parse(read(policy.cases.path));
const catalogue={schema_version:'0.1',sha256:'0'.repeat(64),models:readdirSync(resolve(root,'models')).filter(p=>p.endsWith('.json')).sort().map(p=>JSON.parse(read('models/'+p)))};
const dep={definitionHash:id=>hash(read('models/'+id+'.json')),readEvidence:read};
const validate=(p=policy,s=supported,c=cases,d=dep)=>validateProfileAllocation(p,s,c,catalogue,d);
test('complete fourteen model allocation validates with every successful scope',()=>{assert.equal(validate().cases.length,36);assert.equal(loadProfileAllocation(resolve(root,'catalogue/laboratory-profile-policy.json'),catalogue).cases.length,36);});
for(const [name,mutate]of Object.entries({
 'missing total rejection':p=>p.legacy_contract_rejections=[],
 'effective model rejection':p=>p.legacy_contract_rejections.push({model:'linear-elastic',message:'legacy laboratory contract requires effective stress'}),
 'relaxed tolerance':p=>p.parity_relative_tolerance=1e-7,
 'unsafe path':p=>p.cases.path='../cases.json',
 'unknown field':p=>p.accept_any_failure=true,
 'wrong count':p=>p.case_count++,
})){test(name,()=>{const p=structuredClone(policy);mutate(p);assert.throws(()=>validate(p));});}
for(const [name,mutate]of Object.entries({
 'duplicate case':c=>c[1]=structuredClone(c[0]),
 'missing model':c=>{const id=c.at(-1).specification.model;for(const x of c)if(x.specification.model===id)x.specification.model='linear-elastic';},
 'wrong scope':c=>c[0].specification.stress_scope='total',
 'unreviewed negative':c=>{c[0].expected_ok=false;c[0].expected_points=1;},
 'wrong success length':c=>c[0].expected_points=1,
 'no successful GIS':c=>{const id=supported.declared_failures[0].model;for(let i=0;i<c.length;i++)if(c[i].specification.model===id)c[i]={...structuredClone(c.find(x=>!x.expected_ok)),id:c[i].id};},
})){test(name,()=>{const c=structuredClone(cases);mutate(c);assert.throws(()=>validate(policy,supported,c));});}
test('stale definition rejected',()=>assert.throws(()=>validate(policy,supported,cases,{...dep,definitionHash:()=> '0'.repeat(64)})));
test('stale evidence rejected',()=>assert.throws(()=>validate(policy,supported,cases,{...dep,readEvidence:()=> '{}'})));
test('ordinary failure requires exact request and preserved initial',()=>{const a=validate(),c=cases.find(c=>!c.expected_ok),result={ok:false,message:c.expected_message,points:[{state:c.specification.initial}]};assertDeclaredOrdinaryFailure(a,c.specification,result);assert.throws(()=>assertDeclaredOrdinaryFailure(a,{...c.specification,target:.02},result));assert.throws(()=>assertDeclaredOrdinaryFailure(a,c.specification,{...result,ok:true}));});
