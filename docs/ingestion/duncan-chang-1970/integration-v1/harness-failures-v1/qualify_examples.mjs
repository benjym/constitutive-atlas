import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {runScopedLaboratory} from '../../../../web/laboratory-scope.mjs';
import {parseLaboratoryDocument} from '../../../../web/laboratory-document.mjs';
const [wasmdir,out]=process.argv.slice(2);assert.ok(!existsSync(out));
const here=resolve('docs/ingestion/duncan-chang-1970/integration-v1');
const catalogue=JSON.parse(readFileSync(join(wasmdir,'generated/models.json')));
const engine=await(await import(pathToFileURL(resolve(wasmdir,'atlas.js')))).default();
const report={status:'running',catalogue_hash:catalogue.sha256,examples:[],calls:[]};
const save=()=>writeFileSync(out,JSON.stringify(report)+'\n');
const logged={ccall(name,type,types,args){const raw=engine.ccall(name,type,types,args);report.calls.push({name,args,raw});save();return raw;}};
const digest=b=>createHash('sha256').update(b).digest('hex');
const write=(path,obj)=>{assert.ok(!existsSync(path));writeFileSync(path,JSON.stringify(obj,null,2)+'\n');};
try{
 const native=JSON.parse(readFileSync(join(here,'native-laboratory.json')));
 const e4=JSON.parse(readFileSync('docs/ingestion/duncan-chang-1970/material-v1/execution-v2/wasm-results.json'));
 const index=JSON.parse(readFileSync('catalogue/laboratory-examples.json'));
 assert.equal(digest(readFileSync('catalogue/laboratory-examples.json')),'419121614f81ef3dc7c299ee95825f56b88517439711f3ec3135847b83a4ab40');
 const settings=native.presets[0].specification.integration_settings;
 for(const p of native.presets){
  const s=p.specification,result=runScopedLaboratory(logged,s,catalogue),row={id:p.id,specification:s,result};report.examples.push(row);save();assert.equal(result.ok,true);assert.equal(result.points.length,129);
  const old=e4.presets.find(x=>x.id===p.id).call.response;assert.equal(old.points.length,result.points.length);
  for(let i=0;i<old.points.length;i++)for(const k of ['state','strain','control','p','q','q_signed','error'])assert.deepEqual(result.points[i][k],old.points[i][k],p.id+'/'+i+'/'+k);
  const id='duncan-'+p.id+'-v1',path='protocols/'+id+'.json';
  const doc={schema_version:'atlas-laboratory-export-0.2',catalogue_hash:catalogue.sha256,specification:s,result};parseLaboratoryDocument(doc,catalogue);write(path,doc);
  index.examples.push({id,model:s.model,label:'Duncan–Chang · '+(p.id.startsWith('dense')?'dense':'loose')+' source coefficients · drained',description:'Illustrative Table1 coefficients,0.5% axial strain in128increments at100kPa initial confinement. Complete7component initial state and numerical choices are explicit. Source-law qualification and exact E5 scope are linked; no specimen calibration, experimental validation or FE-host tangent claim.',definition_sha256:'452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0',document_sha256:digest(readFileSync(path)),evidence_url:'https://github.com/benjym/constitutive-atlas/blob/main/docs/ingestion/duncan-chang-1970/material-v1/independent-review/e5-v1/REPORT.md',document_path:path});
 }
 const gis=index.examples.find(x=>x.id==='gis2024-small-drained');const prior=JSON.parse(readFileSync(gis.document_path)),s=prior.specification;
 const result=runScopedLaboratory(logged,s,catalogue);report.examples.push({id:gis.id,specification:s,result});save();assert.equal(result.ok,true);assert.equal(result.points.length,s.steps+1);
 const path='protocols/gis2024-small-drained-fourteen-duncan-v1.json';const doc={schema_version:'atlas-laboratory-export-0.2',catalogue_hash:catalogue.sha256,specification:s,result};parseLaboratoryDocument(doc,catalogue);write(path,doc);
 gis.document_path=path;gis.document_sha256=digest(readFileSync(path));
 writeFileSync('catalogue/laboratory-examples.json',JSON.stringify(index,null,2)+'\n');
 report.status='passed';save();console.log('Two exact E4 Wasm source histories and fresh14catalogue GIS named example passed.');
}catch(e){report.status='failed';report.error=String(e);save();throw e;}
