// Frozen Stage B package check. Ordinary GIS default remains a recorded failure.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {webcrypto} from 'node:crypto';
import {validatePackage} from '../../../tools/test_web_package.mjs';
const [directory,output]=process.argv.slice(2),base=resolve(directory),read=n=>JSON.parse(readFileSync(join(base,n),'utf8'));
const catalogue=validatePackage(base),create=(await import(pathToFileURL(join(base,'atlas.js')))).default;
const {runScopedLaboratory,laboratoryStress}=await import(pathToFileURL(join(base,'laboratory-scope.mjs')));
const {normalizeSettings}=await import(pathToFileURL(join(base,'numerics.mjs')));
const {createLoading}=await import(pathToFileURL(join(base,'loading.mjs')));
const {prepareExample}=await import(pathToFileURL(join(base,'laboratory-examples.mjs')));
const pre=JSON.parse(readFileSync(new URL('./pre-install-identities.json',import.meta.url))),oldIDs=Object.keys(pre.existing_models).map(n=>n.slice(0,-5)).sort();
const mid='research-hp-extracted-asbs-gis-2024-v03';
assert.deepEqual(catalogue.models.map(m=>m.id).sort(),[...oldIDs,mid].sort());assert.equal(oldIDs.length,10);
const engine=await create(),report={scope:'Stage B package/Node-Wasm checks, not actual browser B01–B12 or scientific admission',catalogue_hash:catalogue.sha256,existing_ten:[],named_example:null,ordinary_gis_default:null};
const spec=m=>{const s={response_contract:'stress-scope-0.1',stress_scope:laboratoryStress(m).scope,model:m.id,parameters:Object.values(m.parameters).map(p=>p.default),initial:m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol:1,target:.01,steps:100,cycles:0,integration_settings:normalizeSettings()};s.loading=createLoading(s);return s;};
try{
 for(const id of oldIDs){const s=spec(catalogue.models.find(m=>m.id===id)),result=runScopedLaboratory(engine,s,catalogue);report.existing_ten.push({id,specification:s,result});assert.equal(result.ok,true,id);assert.equal(result.catalogue_hash,catalogue.sha256);assert.equal(result.points.length,101,id);assert.deepEqual(result.points[0].state,s.initial);for(const point of result.points){assert.equal(point.state.length,s.initial.length);for(const value of [...point.state,...point.strain,point.p,point.q])assert.ok(Number.isFinite(value));if(result.pore_pressure.availability==='unavailable')assert.equal(point.u,null);else assert.ok(Number.isFinite(point.u));}}
 const index=read('laboratory-examples.json');assert.equal(index.examples.length,1);const prepared=await prepareExample(index.examples[0],index,catalogue,{crypto:webcrypto,fetcher:async url=>({ok:true,text:async()=>readFileSync(join(base,url),'utf8')})});const named=runScopedLaboratory(engine,prepared.specification,catalogue);report.named_example={specification:prepared.specification,result:named};assert.equal(named.ok,true);assert.equal(named.points.length,9);assert.deepEqual(named.points[0].state,prepared.specification.initial);assert.equal(named.points[0].state.length,14);
 const s=spec(catalogue.models.find(m=>m.id===mid)),failed=runScopedLaboratory(engine,s,catalogue);report.ordinary_gis_default={status:'failed-retained',specification:s,result:failed};assert.equal(failed.ok,false);assert.equal(failed.points.length,1);assert.deepEqual(failed.points[0].state,s.initial);assert.equal(s.integration_settings.max_depth,14);
 report.stage_b_status='passed';report.all_eleven_ordinary_defaults='failed; GIS failure retained, not waived or converted to pass';
}catch(error){report.stage_b_status='failed';report.error=String(error);throw error;}
finally{writeFileSync(output,JSON.stringify(report,null,2)+'\n');}
