// Test the completed Pages artifact, including its own Wasm and browser settings module.
import assert from 'node:assert/strict';
import {validateDatabasePackage} from './validate_database_package.mjs';
import {readFileSync,writeFileSync,existsSync,readdirSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';

import {createHash} from 'node:crypto';
import {strictJSON} from '../web/controlled-time-engine.mjs';

const repository=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const componentNames=['controlled-time-engine.mjs','controlled-time-worker.mjs','controlled-time-laboratory.mjs'];
const engineNames=['approval.json','catalogue.json','engine.mjs','engine.wasm','examples.json','expected-results.json','model.json','qualification.json','review.json'];
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
function exactKeys(object,names,label){assert.ok(object&&typeof object==='object'&&!Array.isArray(object),label);assert.deepEqual(Object.keys(object).sort(),[...names].sort(),label);}
export function validateControlledTimeMembership(directory,entries,ordinaryIds){
 const claims=entries.filter(e=>Object.hasOwn(e,'controlled_time_laboratory'));
 if(!claims.length){assert.ok(!existsSync(join(directory,'engine-controlled-time')),'Unclaimed controlled-time package');return [];}
 assert.equal(claims.length,1,'One sealed controlled-time interface required');
 const entry=claims[0];assert.equal(entry.controlled_time_laboratory,'index.html','Unknown controlled-time route');
 assert.equal(entry.executable,true,'Controlled-time entry must be executable');assert.match(entry.id,/^[a-z0-9][a-z0-9-]*$/,'Unsafe controlled-time model ID');
 assert.ok(!ordinaryIds.includes(entry.id),'Controlled-time/ordinary overlap');
 const base=join(directory,'engine-controlled-time'),bytes=name=>readFileSync(join(base,name)),read=name=>strictJSON(bytes(name).toString());
 assert.deepEqual(readdirSync(base).sort(),[...engineNames,'identity.json','package-manifest.json'].sort(),'Controlled-time asset set');
 const identity=read('identity.json'),seal=read('package-manifest.json');
 exactKeys(identity,['profile','model','model_sha256','definition_file_sha256','catalogue_sha256','files','components'],'Controlled-time identity fields');
 assert.equal(identity.profile,'controlled-time-ode-v1','Stale controlled-time profile');assert.equal(identity.model,entry.id,'Controlled-time model identity');
 exactKeys(identity.files,engineNames,'Controlled-time identity file set');exactKeys(identity.components,componentNames,'Controlled-time component set');
 exactKeys(seal,['kind','files'],'Controlled-time seal fields');assert.equal(seal.kind,'controlled-time-mainatlas-package-v1');
 exactKeys(seal.files,[...componentNames,...[...engineNames,'identity.json'].map(n=>'engine-controlled-time/'+n)],'Controlled-time seal file set');
 for(const [name,expected] of Object.entries(identity.files))assert.equal(hash(bytes(name)),expected,'Controlled-time identity file: '+name);
 for(const [name,expected] of Object.entries(identity.components))assert.equal(hash(readFileSync(join(directory,name))),expected,'Controlled-time component: '+name);
 for(const [name,expected] of Object.entries(seal.files))assert.equal(hash(readFileSync(join(directory,name))),expected,'Controlled-time sealed file: '+name);
 const definition=read('model.json'),catalogue=read('catalogue.json'),approval=read('approval.json'),review=read('review.json'),qualification=read('qualification.json');
 const registry=strictJSON(readFileSync(join(repository,'catalogue/approved-models.json'),'utf8'));
 const accepted=registry.models.filter(a=>a.model_id===entry.id&&a.status==='approved'&&a.definition.sha256===hash(bytes('model.json')));
 assert.equal(accepted.length,1,'Exact approved controlled-time model missing/ambiguous');assert.deepEqual(approval,accepted[0],'Untrusted controlled-time approval');
 const pin=(name,p)=>{assert.ok(p&&typeof p.path==='string'&&!p.path.startsWith('/')&&!p.path.split('/').includes('..'),'Unsafe approved source pin');assert.equal(hash(bytes(name)),p.sha256,'Controlled-time approved pin: '+name);};
 pin('model.json',approval.definition);pin('review.json',approval.review);
 assert.equal(definition.id,entry.id);assert.equal(identity.definition_file_sha256,approval.definition.sha256);
 assert.equal(definition.formulation.equation_form,'controlled_ode');assert.equal(definition.formulation.time_dependence,'physical_time');
 assert.equal(review.kind,'agent-model-review');assert.equal(review.status,'accepted');assert.equal(review.reviewer.kind,'agent');assert.deepEqual(review.blocking_findings,[]);
 assert.deepEqual(review.model,{id:entry.id,...approval.definition},'Controlled-time review/model mismatch');
 assert.equal(qualification.kind,'controlled-time-public-engine-qualification-v1');assert.equal(qualification.status,'accepted');assert.equal(qualification.model_id,entry.id);assert.equal(qualification.definition_sha256,approval.definition.sha256);
 const support=p=>{assert.ok(approval.supporting_files.some(q=>q.path===p.path&&q.sha256===p.sha256),'Qualification not bound by approval');return p;};
 pin('qualification.json',support({path:qualification.root_receipt_path,sha256:hash(bytes('qualification.json'))}));
 pin('examples.json',support(qualification.examples));pin('expected-results.json',support(qualification.public_results));
 assert.equal(hash(bytes('engine.mjs')),qualification.artifacts['atlas_controlled_time_capability.mjs']);assert.equal(hash(bytes('engine.wasm')),qualification.artifacts['atlas_controlled_time_capability.wasm']);
 for(const name of componentNames){const pins=qualification.source_files.filter(p=>p.path==='web/'+name);assert.equal(pins.length,1);assert.equal(identity.components[name],pins[0].sha256,'Unqualified controlled-time component');}
 assert.equal(catalogue.profile,identity.profile);assert.equal(catalogue.catalogue_sha256,identity.catalogue_sha256);assert.equal(catalogue.models.length,1);assert.equal(catalogue.models[0].id,entry.id);assert.equal(catalogue.models[0].model_sha256,identity.model_sha256);assert.deepEqual(catalogue.models[0].formulation,definition.formulation);
 assert.deepEqual(bytes('catalogue.json'),readFileSync(join(repository,'web/engines/controlled-time/generated/controlled_time_catalogue.json')),'Stale controlled-time generated catalogue');
 return [entry.id];
}

export function validatePackage(directory){
 const read=name=>JSON.parse(readFileSync(join(directory,name),'utf8'));
 const metadata=read('models.json'),catalogue=read('catalogue.json');
 const models=metadata.models;
 assert.ok(Array.isArray(models)&&models.length>0,'No packaged models');
 const ids=models.map(m=>m.id);
 assert.equal(new Set(ids).size,ids.length,'Duplicate runtime model ID');
 assert.equal(new Set(catalogue.models.map(m=>m.id)).size,catalogue.models.length,'Duplicate catalogue ID');
 const separate=validateControlledTimeMembership(directory,catalogue.models,ids);
 assert.deepEqual(catalogue.models.filter(m=>m.executable&&!separate.includes(m.id)).map(m=>m.id).sort(),[...ids].sort(),'Executable catalogue differs from runtime');
 for(const model of models){
  assert.match(model.id,/^[a-z0-9][a-z0-9-]*$/,'Unsafe model ID');
  assert.deepEqual(read('models/'+model.id+'.json'),model,'Stale packaged definition: '+model.id);
  assert.ok(existsSync(join(directory,'schemas/'+(model.schema_version==='0.1'?'model.schema.json':'model-v'+model.schema_version+'.schema.json'))),'Missing model schema');
  assert.ok(Array.isArray(model.sources)&&model.sources.length>0,'Missing sources: '+model.id);
  for(const source of model.sources){
   const url=new URL(source.url);
   assert.ok(['https:','http:'].includes(url.protocol),'Unsafe source URL');
   assert.ok(url.hostname,'Source URL has no host');
  }
 }
 for(const entry of catalogue.models){
  if(entry.public_timed_laboratory!==true)continue;
  assert.match(entry.timed_laboratory||'',/^[a-z0-9][a-z0-9-]*\.html$/,'Unsafe public timed route');
  assert.ok(existsSync(join(directory,entry.timed_laboratory)),'Missing public timed laboratory: '+entry.id);
  assert.ok(existsSync(join(directory,'timed-route.mjs')),'Missing timed route module');
 }
 const base=new URL('https://example.invalid/constitutive-atlas/');
 for(const file of ['index.html']){
  const html=readFileSync(join(directory,file),'utf8');
  for(const match of html.matchAll(/(?:src|href)=["']([^"']+)["']/g)){
   const href=match[1];if(href.startsWith('#'))continue;
   const url=new URL(href,base);if(url.origin!==base.origin)continue;
   assert.ok(url.pathname.startsWith(base.pathname),'Asset escapes project prefix: '+href);
   assert.ok(existsSync(join(directory,decodeURIComponent(url.pathname.slice(base.pathname.length)))),'Missing linked asset: '+href);
  }
 }
 for(const name of ['atlas.js','atlas.wasm','worker.js','numerics.mjs','loading.mjs','recorded.mjs','state-contract.mjs','.nojekyll'])assert.ok(existsSync(join(directory,name)),'Missing package asset: '+name);
 validateDatabasePackage(directory);
 return metadata;
}

export async function checkPackage(directory){
 const metadata=validatePackage(directory);
 const createAtlas=(await import(pathToFileURL(join(directory,'atlas.js')))).default;
 const {normalizeSettings}=await import(pathToFileURL(join(directory,'numerics.mjs')));
 const {runScopedLaboratory,laboratoryStress}=await import(pathToFileURL(join(directory,'laboratory-scope.mjs')));
 const {createLoading}=await import(pathToFileURL(join(directory,'loading.mjs')));
 const engine=await createAtlas();
 const report={status:'running',scope:'packaged default-run software smoke test; no scientific admission',catalogue_hash:metadata.sha256,models:[]};
 try{for(const model of metadata.models){
  const initial=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);
  assert.ok(initial.every(Number.isFinite),'Nonfinite illustrative state');
  const specification={response_contract:'stress-scope-0.1',stress_scope:laboratoryStress(model).scope,model:model.id,parameters:Object.values(model.parameters).map(p=>p.default),initial,protocol:1,target:0.01,steps:100,cycles:0,integration_settings:normalizeSettings()};
  specification.loading=createLoading(specification);
  const result=runScopedLaboratory(engine,specification,metadata);
  report.models.push({id:model.id,specification,result});
  assert.equal(result.ok,true,model.id+': '+result.message);
  assert.equal(result.catalogue_hash,metadata.sha256,'Stale packaged engine: '+model.id);
  assert.equal(result.points.length,101,'Incomplete default run: '+model.id);
  assert.deepEqual(result.points[0].state,initial,'Unexpected initial state: '+model.id);
  for(const point of result.points){
   assert.equal(point.state.length,initial.length);assert.equal(point.strain.length,6);
   for(const value of [...point.state,...point.strain,point.p,point.q])assert.ok(Number.isFinite(value),'Nonfinite plot channel: '+model.id);
   if(result.pore_pressure.availability==='unavailable')assert.equal(point.u,null,'Fabricated pore pressure: '+model.id);
   else assert.ok(Number.isFinite(point.u),'Invalid available pore pressure: '+model.id);
  }
 }
 }catch(error){report.status='failed';report.error=String(error);error.report=report;throw error;}
 report.status='passed';return report;
}

if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const options={};for(let i=2;i<process.argv.length;i+=2){assert.ok(['--directory','--output'].includes(process.argv[i]));assert.ok(process.argv[i+1]);assert.ok(!options[process.argv[i]]);options[process.argv[i]]=process.argv[i+1];}
 const directory=resolve(options['--directory']||join(dirname(fileURLToPath(import.meta.url)),'../web/dist'));
 let report;try{report=await checkPackage(directory);}catch(error){if(options['--output'])writeFileSync(options['--output'],JSON.stringify(error.report||{status:'failed',error:String(error)},null,2)+'\n');throw error;}
 if(options['--output'])writeFileSync(options['--output'],JSON.stringify(report,null,2)+'\n');
 console.log(`Packaged Pages laboratory passed for ${report.models.length} models (101 points each).`);
}
