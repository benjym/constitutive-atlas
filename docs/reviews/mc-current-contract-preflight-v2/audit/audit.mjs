import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createLaboratoryDocument,parseLaboratoryDocument} from './snapshot/current/frozen-web/laboratory-document.mjs';
import {runScopedLaboratory} from './snapshot/current/frozen-web/laboratory-scope.mjs';
import {createLoading,controlBits,controlFromBits} from './snapshot/current/frozen-web/loading.mjs';
const read=n=>JSON.parse(readFileSync(new URL(n,import.meta.url),'utf8'));
const cat=read('./snapshot/current/catalogue.json'),rows=read('./snapshot/current/contracts.json'),frames=read('./snapshot/current/source-ideal.json').frames,source=read('./snapshot/mc-browser-loading-paths-v1/source-input.json');
const observations=[],witnesses=[],settingsKeys=['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'];
let count=0;
for(let j=0;j<rows.length;j++){
 const {id,specification:s}=rows[j],r=frames[j].result;
 const exact=source.paths.find(p=>p.id===id);assert.deepEqual(s.loading,createLoading(s));assert.deepEqual(s.loading.controls_bits,exact.controls_bits);
 const engine={ccall(name,type,types,args){
  count++;assert.equal(type,'string');
  if(name==='atlas_describe'){assert.deepEqual(types,[]);assert.deepEqual(args,[]);return JSON.stringify(cat);}
  assert.equal(name,'atlas_run_controls_scope_with_settings');assert.deepEqual(types,['string','string','string','number','string','string']);
  assert.deepEqual(args,[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.loading.controls_bits.join(','),settingsKeys.map(k=>s.integration_settings[k]).join(',')]);return JSON.stringify(r);
 }};
 assert.deepEqual(runScopedLaboratory(engine,s,cat),r);
 const doc=createLaboratoryDocument(s,r,cat),raw=JSON.stringify(doc);assert.deepEqual(parseLaboratoryDocument(raw,cat),s);
 const changes=[['scope',d=>d.result.stress.scope='total'],['pore',d=>{d.result.pore_pressure={quantity:'change',availability:'unavailable',reason:'not_reconstructed_for_protocol'};for(const p of d.result.points)p.u=0;}],['control',d=>d.result.loading.controls_bits[1]=d.result.loading.controls_bits[1]==='0000000000000000'?'0000000000000001':'0000000000000000'],['state',d=>d.result.points[0].state.pop()],['catalogue',d=>d.catalogue_hash='bad']];
 for(const [kind,change] of changes){const d=structuredClone(doc);change(d);assert.notDeepEqual(d,doc);assert.throws(()=>parseLaboratoryDocument(JSON.stringify(d),cat));observations.push({id,kind,changed:true,rejected:true});}
 const duplicate='{"schema_version":"duplicate",'+raw.slice(1),overflow=raw.replace('"result":{','"result":{"unused":1e999,');
 assert.notEqual(duplicate,raw);assert.notEqual(overflow,raw);assert.equal((duplicate.match(/"schema_version":/g)||[]).length,(raw.match(/"schema_version":/g)||[]).length+1);assert.equal(JSON.parse(overflow).result.unused,Infinity);
 for(const [kind,text] of [['duplicate',duplicate],['overflow',overflow]]){assert.deepEqual(parseLaboratoryDocument(text,cat),s);witnesses.push({id,kind,changed:true,accepted:true});if(id==='zero-hold')writeFileSync(new URL('./witness-'+kind+'.json',import.meta.url),text+'\n');}
 if(id==='zero-hold'){
  const old=structuredClone(doc);old.result.loading.controls_bits[1]='0000000000000000';assert.deepEqual(old,doc);
  observations.push({id,kind:'retained-old-control-probe',changed:false,note:'Old replacement is a no-op; final replacement above is nonidentical and rejected.'});
 }
}
assert.equal(rows.length,14);assert.equal(witnesses.length,28);assert.equal(observations.filter(x=>x.rejected).length,70);assert.equal(count,28);
writeFileSync(new URL('./independent-js-results.json',import.meta.url),JSON.stringify({manufactured_only:true,models:cat.models.length,rows:rows.length,exact_CAPI_type_and_argument_callback_checks:count,real_backend_calls:0,document_mutations:observations,parser_false_passes:witnesses},null,2)+'\n');
