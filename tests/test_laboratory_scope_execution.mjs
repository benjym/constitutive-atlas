import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateScopedLaboratory,runScopedLaboratory,verifyScopedLaboratory,laboratoryPoreSeries} from '../web/laboratory-scope.mjs';
import {createLoading,controlFromBits} from '../web/loading.mjs';
const {catalogue,rows}=JSON.parse(readFileSync(0,'utf8'));
let rejections=0;
const rejects=fn=>{assert.throws(fn);rejections++;};
for(const row of rows){
 const before=JSON.stringify(row),s=row.request,r=row.response;
 assert.equal(verifyScopedLaboratory(r,s,catalogue),r);
 const calls=[];assert.deepEqual(runScopedLaboratory({ccall(name){calls.push(name);return JSON.stringify(name==='atlas_describe'?catalogue:r);}},s,catalogue),r);assert.deepEqual(calls,['atlas_describe','atlas_run_scope_with_settings']);
 const series=laboratoryPoreSeries(r);
 if(s.stress_scope==='effective'&&[2,3].includes(s.protocol)){assert.equal(series.points.length,r.points.length);assert.equal(series.reason,null);}
 else{assert.deepEqual(series.points,[]);assert.ok(series.reason);}
 for(const change of ['version','scope','stress-extra','pore','pore-extra','u','catalogue','model','settings','settings-extra','parameters','initial','protocol','steps','target','prefix','point-state','point-strain','point-counter','point-initial']){
  const bad=structuredClone(r);
  if(change==='version')bad.api_version='legacy';
  if(change==='scope')bad.stress.scope=s.stress_scope==='total'?'effective':'total';
  if(change==='stress-extra')bad.stress.extra=true;
  if(change==='pore')bad.pore_pressure.availability='other';
  if(change==='pore-extra')bad.pore_pressure.extra=true;
  if(change==='u')bad.points[1].u=r.pore_pressure.availability==='reconstructed'?null:0;
  if(change==='catalogue')bad.catalogue_hash='0'.repeat(64);
  if(change==='model')bad.model='another';
  if(change==='settings')bad.integration_settings.max_depth++;
  if(change==='settings-extra')bad.integration_settings.extra=1;
  if(change==='parameters')bad.parameters[0]++;
  if(change==='initial')bad.initial[0]++;
  if(change==='protocol')bad.protocol=(s.protocol+1)%5;
  if(change==='steps')bad.steps++;
  if(change==='target')bad.target++;
  if(change==='prefix')bad.points.pop();
  if(change==='point-state')bad.points[1].state.pop();
  if(change==='point-strain')bad.points[1].strain[0]='bad';
  if(change==='point-counter')bad.points[1].iterations=true;
  if(change==='point-initial')bad.points[0].state[0]++;
  rejects(()=>verifyScopedLaboratory(bad,s,catalogue));
 }
 const wrong=structuredClone(s);wrong.stress_scope=s.stress_scope==='total'?'effective':'total';let called=false;
 rejects(()=>runScopedLaboratory({ccall(){called=true;}},wrong,catalogue));assert.equal(called,false);
 assert.equal(JSON.stringify(row),before);
}
const row=rows.find(r=>r.label==='scoped-elastic-1'),s=structuredClone(row.request),r=structuredClone(row.response);
s.loading=createLoading(s);delete r.target;delete r.cycles;r.loading={version:s.loading.version,encoding:s.loading.encoding,controls_bits:s.loading.controls_bits,controls:s.loading.controls_bits.map(controlFromBits)};
let calls=[];assert.deepEqual(runScopedLaboratory({ccall(name){calls.push(name);return JSON.stringify(name==='atlas_describe'?catalogue:r);}},s,catalogue),r);assert.deepEqual(calls,['atlas_describe','atlas_run_controls_scope_with_settings']);
const badLoading=structuredClone(r);badLoading.loading.controls_bits[1]='0'.repeat(16);rejects(()=>verifyScopedLaboratory(badLoading,s,catalogue));
for(const request of [row.request,s]){
 calls=[];rejects(()=>runScopedLaboratory({ccall(name){calls.push(name);if(name==='atlas_describe')return JSON.stringify(catalogue);throw Error('missing export');}},request,catalogue));assert.equal(calls.length,2);assert.ok(calls[1].includes('_scope_'));
}
for(const kind of ['hash','order']){
 const bad=structuredClone(catalogue);if(kind==='hash')bad.sha256='0'.repeat(64);else bad.models[0].parameters=Object.fromEntries(Object.entries(bad.models[0].parameters).reverse());
 calls=[];rejects(()=>runScopedLaboratory({ccall(name){calls.push(name);return JSON.stringify(bad);}},row.request,catalogue));assert.deepEqual(calls,['atlas_describe']);
}
for(const kind of ['fields','parameters','initial','scope','target','settings']){
 const bad=structuredClone(row.request);
 if(kind==='fields')bad.extra=true;
 if(kind==='parameters')bad.parameters=[];
 if(kind==='initial')bad.initial=[];
 if(kind==='scope')delete bad.stress_scope;
 if(kind==='target')bad.target=Infinity;
 if(kind==='settings')bad.integration_settings.max_iterations=true;
 rejects(()=>validateScopedLaboratory(bad,catalogue));
}
const reconstructed=rows.find(x=>x.response.pore_pressure.availability==='reconstructed').response;
for(const u of [null,NaN,Infinity,'0',false]){const bad=structuredClone(reconstructed);bad.points[1].u=u;rejects(()=>laboratoryPoreSeries(bad));}
const failed=structuredClone(row.response);failed.ok=false;failed.points.pop();assert.equal(verifyScopedLaboratory(failed,row.request,catalogue),failed);
process.stdout.write(JSON.stringify({saved_cases:10,rejections,exact_routing:true,failed_prefix:true}));
