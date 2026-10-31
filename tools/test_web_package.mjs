// Test the completed Pages artifact, including its own Wasm and browser settings module.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';

export function validatePackage(directory){
 const read=name=>JSON.parse(readFileSync(join(directory,name),'utf8'));
 const metadata=read('models.json'),catalogue=read('catalogue.json');
 const models=metadata.models;
 assert.ok(Array.isArray(models)&&models.length>0,'No packaged models');
 const ids=models.map(m=>m.id);
 assert.equal(new Set(ids).size,ids.length,'Duplicate runtime model ID');
 assert.equal(new Set(catalogue.models.map(m=>m.id)).size,catalogue.models.length,'Duplicate catalogue ID');
 assert.deepEqual(catalogue.models.filter(m=>m.executable).map(m=>m.id).sort(),[...ids].sort(),'Executable catalogue differs from runtime');
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
 const base=new URL('https://example.invalid/constitutive-atlas/');
 for(const file of ['index.html','publications.html']){
  const html=readFileSync(join(directory,file),'utf8');
  for(const match of html.matchAll(/(?:src|href)=["']([^"']+)["']/g)){
   const href=match[1];if(href.startsWith('#'))continue;
   const url=new URL(href,base);if(url.origin!==base.origin)continue;
   assert.ok(url.pathname.startsWith(base.pathname),'Asset escapes project prefix: '+href);
   assert.ok(existsSync(join(directory,decodeURIComponent(url.pathname.slice(base.pathname.length)))),'Missing linked asset: '+href);
  }
 }
 for(const name of ['atlas.js','atlas.wasm','worker.js','numerics.mjs','recorded.mjs','state-contract.mjs','.nojekyll'])assert.ok(existsSync(join(directory,name)),'Missing package asset: '+name);
 return metadata;
}

export async function checkPackage(directory){
 const metadata=validatePackage(directory);
 const createAtlas=(await import(pathToFileURL(join(directory,'atlas.js')))).default;
 const {runLaboratory,normalizeSettings}=await import(pathToFileURL(join(directory,'numerics.mjs')));
 const engine=await createAtlas();
 const report={status:'running',scope:'packaged default-run software smoke test; no scientific admission',catalogue_hash:metadata.sha256,models:[]};
 try{for(const model of metadata.models){
  const initial=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);
  assert.ok(initial.every(Number.isFinite),'Nonfinite illustrative state');
  const specification={model:model.id,parameters:Object.values(model.parameters).map(p=>p.default),initial,protocol:1,target:0.01,steps:100,cycles:0,integration_settings:normalizeSettings()};
  const result=runLaboratory(engine,specification);
  report.models.push({id:model.id,specification,result});
  assert.equal(result.ok,true,model.id+': '+result.message);
  assert.equal(result.catalogue_hash,metadata.sha256,'Stale packaged engine: '+model.id);
  assert.equal(result.points.length,101,'Incomplete default run: '+model.id);
  assert.deepEqual(result.points[0].state,initial,'Unexpected initial state: '+model.id);
  for(const point of result.points){
   assert.equal(point.state.length,initial.length);assert.equal(point.strain.length,6);
   for(const value of [...point.state,...point.strain,point.p,point.q,point.u])assert.ok(Number.isFinite(value),'Nonfinite plot channel: '+model.id);
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
