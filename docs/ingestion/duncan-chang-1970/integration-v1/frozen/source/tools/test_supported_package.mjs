// Distinct supported-input release check. The strict all-default checker is unchanged.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,realpathSync}from'node:fs';
import {createHash,webcrypto}from'node:crypto';
import {resolve,join,dirname,sep}from'node:path';
import {pathToFileURL,fileURLToPath}from'node:url';
import {validatePackage}from'./test_web_package.mjs';
const digest=text=>createHash('sha256').update(text).digest('hex');
const keys=(value,expected)=>{assert.ok(value&&typeof value==='object'&&!Array.isArray(value));assert.deepEqual(Object.keys(value).sort(),[...expected].sort(),'Unexpected policy fields');};
export function validatePolicy(policy,catalogue,{definitionHash,readEvidence}){
 keys(policy,['schema_version','kind','id','ordinary','models','declared_failures','limitations']);
 assert.equal(policy.schema_version,'0.1');assert.equal(policy.kind,'supported-laboratory-package-policy');assert.match(policy.id,/^[a-z][a-z0-9-]*$/);
 assert.equal(policy.ordinary,'drained-1pct-100-current-settings');assert.ok(Array.isArray(policy.limitations)&&policy.limitations.length>0&&policy.limitations.every(x=>typeof x==='string'&&x.length));
 const ids=catalogue.models.map(m=>m.id);assert.equal(new Set(ids).size,ids.length);
 assert.deepEqual(Object.keys(policy.models).sort(),[...ids].sort(),'Policy must bind every current model exactly');
 for(const id of ids){assert.match(policy.models[id],/^[a-f0-9]{64}$/);assert.equal(definitionHash(id),policy.models[id],'Stale policy definition: '+id);}
 assert.ok(Array.isArray(policy.declared_failures));const seen=new Set();
 for(const entry of policy.declared_failures){
  keys(entry,['model','ordinary_specification','message','committed_points','named_example','evidence']);
  assert.ok(ids.includes(entry.model)&&!seen.has(entry.model),'Unknown or duplicate declared failure');seen.add(entry.model);
  assert.equal(entry.ordinary_specification.model,entry.model);assert.ok(typeof entry.message==='string'&&entry.message.length);
  assert.equal(entry.committed_points,1,'Only the retained initial-point failure is admitted by policy v0.1');assert.match(entry.named_example,/^[a-z0-9][a-z0-9-]*$/);
  keys(entry.evidence,['path','sha256']);assert.match(entry.evidence.path,/^docs\/[a-zA-Z0-9_./-]+\.json$/);assert.ok(!entry.evidence.path.split('/').includes('..'));assert.match(entry.evidence.sha256,/^[a-f0-9]{64}$/);
  const body=readEvidence(entry.evidence.path);assert.equal(digest(body),entry.evidence.sha256,'Failure evidence changed');
  const evidence=JSON.parse(body);assert.equal(evidence.status,'failed');assert.ok(Array.isArray(evidence.models));const rows=evidence.models.filter(r=>r.id===entry.model);assert.equal(rows.length,1);const row=rows[0];
  assert.deepEqual(row.specification,entry.ordinary_specification);assert.equal(row.result.ok,false);assert.equal(row.result.message,entry.message);assert.equal(row.result.points.length,entry.committed_points);assert.deepEqual(row.result.points[0].state,row.specification.initial);
 }
 return policy;
}
function history(result,s,catalogue,count){
 assert.equal(result.catalogue_hash,catalogue.sha256);assert.equal(result.model,s.model);assert.deepEqual(result.initial,s.initial);assert.deepEqual(result.parameters,s.parameters);assert.deepEqual(result.integration_settings,s.integration_settings);assert.equal(result.protocol,s.protocol);assert.equal(result.steps,s.steps);
 assert.equal(result.points.length,count);assert.deepEqual(result.points[0].state,s.initial);
 for(const p of result.points){assert.equal(p.state.length,s.initial.length);assert.equal(p.strain.length,6);assert.ok([...p.state,...p.strain,p.p,p.q,p.q_signed].every(Number.isFinite));assert.ok(p.u===null||Number.isFinite(p.u));}
}
export async function assessSupportedPackage({catalogue,policy,index,ordinary,run,prepareExample,definitionHash,readEvidence}){
 const report={status:'running',scope:'Supported ordinary or explicitly registered example inputs; not all-default success or scientific admission',policy_id:policy.id,catalogue_hash:catalogue.sha256,ordinary:[],named:[]};
 try{
  validatePolicy(policy,catalogue,{definitionHash,readEvidence});assert.equal(index.catalogue_hash,catalogue.sha256);assert.equal(index.schema_version,'0.1');assert.ok(Array.isArray(index.examples));
  for(const model of catalogue.models){
   const s=ordinary(model),declared=policy.declared_failures.find(e=>e.model===model.id);if(declared)assert.deepEqual(s,declared.ordinary_specification,'Ordinary request changed');
   const result=await run(s);report.ordinary.push({id:model.id,specification:s,result,expected_outcome:declared?'declared-failure':'success'});
   if(!declared){assert.equal(result.ok,true,model.id+': unexpected ordinary failure');history(result,s,catalogue,s.steps+1);continue;}
   assert.equal(result.ok,false,'Known limitation changed to success; review policy');assert.equal(result.message,declared.message,'Failure signature changed');history(result,s,catalogue,declared.committed_points);
   const matches=index.examples.filter(e=>e.id===declared.named_example&&e.model===model.id);assert.equal(matches.length,1,'Declared named example missing or duplicated');const entry=matches[0];assert.equal(entry.definition_sha256,policy.models[model.id],'Named example definition changed');
   const prepared=await prepareExample(entry,index,catalogue);assert.equal(prepared.specification.model,model.id);const named=await run(prepared.specification);report.named.push({id:entry.id,specification:prepared.specification,result:named});assert.equal(named.ok,true,'Named example failed');history(named,prepared.specification,catalogue,prepared.specification.steps+1);
  }
  report.status='passed';return report;
 }catch(error){report.status='failed';report.error=String(error);error.report=report;throw error;}
}
export async function checkSupportedPackage(directory,policyFile){
 directory=realpathSync(directory);const catalogue=validatePackage(directory),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
 const inside=(base,name)=>{const path=realpathSync(resolve(base,name));assert.ok(path.startsWith(base+sep),'Asset escapes root');return path;};
 const policyText=readFileSync(policyFile,'utf8'),policy=JSON.parse(policyText),index=JSON.parse(readFileSync(join(directory,'laboratory-examples.json'),'utf8'));
 const createAtlas=(await import(pathToFileURL(join(directory,'atlas.js')))).default;
 const {runScopedLaboratory,laboratoryStress}=await import(pathToFileURL(join(directory,'laboratory-scope.mjs')));
 const {normalizeSettings}=await import(pathToFileURL(join(directory,'numerics.mjs')));
 const {createLoading}=await import(pathToFileURL(join(directory,'loading.mjs')));
 const {prepareExample}=await import(pathToFileURL(join(directory,'laboratory-examples.mjs')));
 const ordinary=m=>{const s={response_contract:'stress-scope-0.1',stress_scope:laboratoryStress(m).scope,model:m.id,parameters:Object.values(m.parameters).map(p=>p.default),initial:m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol:1,target:.01,steps:100,cycles:0,integration_settings:normalizeSettings()};s.loading=createLoading(s);return s;};
 // Validate all prospective identity/evidence bindings before initializing compiled code.
 const dependencies={definitionHash:id=>digest(readFileSync(inside(directory,'models/'+id+'.json'))),readEvidence:name=>readFileSync(inside(realpathSync(root),name),'utf8')};validatePolicy(policy,catalogue,dependencies);
 const engine=await createAtlas();const report=await assessSupportedPackage({catalogue,policy,index,ordinary,run:s=>runScopedLaboratory(engine,s,catalogue),prepareExample:(entry,index,catalogue)=>prepareExample(entry,index,catalogue,{crypto:webcrypto,fetcher:async url=>({ok:true,text:async()=>readFileSync(inside(directory,url),'utf8')})}),...dependencies});
 report.policy_sha256=digest(policyText);return report;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const options={};for(let i=2;i<process.argv.length;i+=2){assert.ok(['--directory','--policy','--output'].includes(process.argv[i]));assert.ok(process.argv[i+1]&&!options[process.argv[i]]);options[process.argv[i]]=process.argv[i+1];}
 const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');let report;try{report=await checkSupportedPackage(resolve(options['--directory']||join(root,'web/dist')),resolve(options['--policy']||join(root,'catalogue/laboratory-package-policy.json')));}catch(error){if(options['--output'])writeFileSync(options['--output'],JSON.stringify(error.report||{status:'failed',error:String(error)},null,2)+'\n');throw error;}
 if(options['--output'])writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');console.log(`Supported-input package passed: ${report.ordinary.length} ordinary requests, ${report.named.length} named examples; strict-default result unchanged.`);
}
