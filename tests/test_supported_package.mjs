import test from'node:test';
import assert from'node:assert/strict';
import {createHash}from'node:crypto';
import {assessSupportedPackage,validatePolicy}from'../tools/test_supported_package.mjs';
const sha=x=>createHash('sha256').update(x).digest('hex');
function fixture(failure=true){
 const h='a'.repeat(64),catalogue={sha256:'catalogue',models:[{id:'one'}]};
 const s={model:'one',initial:[100,100,100,0,0,0],parameters:[1],protocol:1,steps:100,integration_settings:{version:'test'}};
 const named={...structuredClone(s),steps:2};
 function response(spec,ok=true){return{ok,message:ok?'':'known first-point failure',catalogue_hash:'catalogue',model:spec.model,initial:structuredClone(spec.initial),parameters:[...spec.parameters],protocol:spec.protocol,steps:spec.steps,integration_settings:structuredClone(spec.integration_settings),points:Array.from({length:ok?spec.steps+1:1},()=>({state:[...spec.initial],strain:[0,0,0,0,0,0],p:100,q:0,q_signed:0,u:null}))};}
 const evidence=JSON.stringify({status:'failed',models:[{id:'one',specification:s,result:response(s,false)}]});
 const policy={schema_version:'0.1',kind:'supported-laboratory-package-policy',id:'test-policy',ordinary:'drained-1pct-100-current-settings',models:{one:h},declared_failures:failure?[{model:'one',ordinary_specification:structuredClone(s),message:'known first-point failure',committed_points:1,named_example:'one-small',evidence:{path:'docs/failure.json',sha256:sha(evidence)}}]:[],limitations:['Software inputs only']};
 return {catalogue,policy,index:{schema_version:'0.1',catalogue_hash:'catalogue',examples:[{id:'one-small',model:'one',definition_sha256:h}]},ordinary:()=>structuredClone(s),run:spec=>response(spec,!failure||spec.steps===2),prepareExample:async()=>({specification:structuredClone(named)}),definitionHash:()=>h,readEvidence:()=>evidence,response,s};
}
test('all ordinary successes need no declarations',async()=>{const r=await assessSupportedPackage(fixture(false));assert.equal(r.status,'passed');assert.equal(r.ordinary.length,1);assert.equal(r.named.length,0);});
test('declared failure and registered named success remain separate results',async()=>{const r=await assessSupportedPackage(fixture());assert.equal(r.status,'passed');assert.equal(r.ordinary[0].result.ok,false);assert.equal(r.named[0].result.ok,true);});
const invalid=[
 ['unexpected ordinary failure',f=>{f.run=s=>f.response(s,false);},false],
 ['changed ordinary request',f=>{f.ordinary=()=>({...f.s,steps:101});}],
 ['stale definition',f=>{f.definitionHash=()=>'b'.repeat(64);}],
 ['missing policy model',f=>{delete f.policy.models.one;}],
 ['extra policy model',f=>{f.policy.models.two='a'.repeat(64);}],
 ['duplicate runtime model',f=>{f.catalogue.models.push({id:'one'});}],
 ['duplicate declaration',f=>{f.policy.declared_failures.push(structuredClone(f.policy.declared_failures[0]));}],
 ['unknown policy field',f=>{f.policy.ignore_failures=true;}],
 ['unknown declaration field',f=>{f.policy.declared_failures[0].optional=true;}],
 ['missing evidence',f=>{f.readEvidence=()=>{throw Error('missing');};}],
 ['corrupt evidence',f=>{f.readEvidence=()=>'{"status":"failed"}';}],
 ['unsafe evidence path',f=>{f.policy.declared_failures[0].evidence.path='docs/../private.json';}],
 ['unregistered named example',f=>{f.index.examples=[];}],
 ['duplicate named example',f=>{f.index.examples.push(f.index.examples[0]);}],
 ['stale named definition',f=>{f.index.examples[0].definition_sha256='b'.repeat(64);}],
 ['invalid named document',f=>{f.prepareExample=async()=>{throw Error('document hash mismatch');};}],
 ['changed failure signature',f=>{f.run=s=>({...f.response(s,false),message:'different failure'});}],
 ['unexpected committed progress',f=>{f.run=s=>{const r=f.response(s,false);r.points.push(structuredClone(r.points[0]));return r;};}],
 ['initial state altered',f=>{f.run=s=>{const r=f.response(s,false);r.points[0].state[0]=999;return r;};}],
 ['named failure',f=>{f.run=s=>f.response(s,false);}],
 ['unexpected default success',f=>{f.run=s=>f.response(s,true);}],
 ['nonfinite history',f=>{f.run=s=>{const r=f.response(s,true);r.points[1].q=Infinity;return r;};},false],
 ['wrong response catalogue',f=>{f.run=s=>({...f.response(s,true),catalogue_hash:'other'});},false],
 ['wrong response parameters',f=>{f.run=s=>({...f.response(s,true),parameters:[9]});},false],
 ['wrong named model',f=>{f.prepareExample=async()=>({specification:{...f.s,model:'other'}});}],
 ['unknown committed-point policy',f=>{f.policy.declared_failures[0].committed_points=2;}],
];
for(const [name,mutate,failure=true]of invalid)test(name+' rejects release',async()=>{const f=fixture(failure);mutate(f);await assert.rejects(assessSupportedPackage(f));});
test('failed execution retains partial ordinary observation',async()=>{const f=fixture(false);f.run=s=>f.response(s,false);await assert.rejects(assessSupportedPackage(f),error=>{assert.equal(error.report.status,'failed');assert.equal(error.report.ordinary.length,1);return true;});});
test('all prospective identity checks precede material execution',async()=>{const f=fixture();f.policy.models.one='b'.repeat(64);let calls=0;f.run=()=>{calls++;throw Error('must not run');};await assert.rejects(assessSupportedPackage(f));assert.equal(calls,0);});
