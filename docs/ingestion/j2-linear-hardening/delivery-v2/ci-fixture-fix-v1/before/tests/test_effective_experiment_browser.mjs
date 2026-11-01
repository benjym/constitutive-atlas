import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import vm from 'node:vm';
import {supportsEffectiveExperiment,compatibleExperiment,comparisonSeries,comparisonMetadata,measuredSeries} from '../web/experiments.mjs';
const read=path=>readFileSync(new URL('../'+path,import.meta.url),'utf8');
const prior=JSON.parse(read('docs/reviews/browser-effective-overlay-scope-v1/previous-sources.json'));
const old=await import(new URL('../'+prior['web/experiments.mjs'].archived_path,import.meta.url));
const models=readdirSync(new URL('../models/',import.meta.url)).filter(n=>n.endsWith('.json')).map(n=>JSON.parse(read('models/'+n)));
const effective=models.find(m=>m.schema_version==='0.3');
const mutate=change=>{const m=structuredClone(effective);change(m);return m;};
const total=mutate(m=>m.formulation.stress.scope='total');
const record={kind:'experiment',protocol:'drained-triaxial',initial:{effective_stress:[130000,100000,100000,0,0,0],void_ratio:.8},rows:[{axial_strain:0,q:0,p:100000,volumetric_strain:0,pore_pressure:0},{axial_strain:.01,q:30000,p:110000,volumetric_strain:.002,pore_pressure:1000}]};
test('all current effective models retain exact prior comparison results',()=>{
 const effectiveModels=models.filter(m=>m.schema_version==='0.1'||m.formulation?.stress?.scope==='effective');
 assert.ok(effectiveModels.length>=9,'retain every original effective model');
 const totalModels=models.filter(m=>m.formulation?.stress?.scope==='total');
 assert.ok(totalModels.some(m=>m.id==='tresca-associated-perfect-bk2022v1-be'));
 for(const model of totalModels){assert.equal(supportsEffectiveExperiment(model),false,model.id);assert.deepEqual(comparisonSeries(record,true,'stress',1,0,model),[]);}
 for(const model of effectiveModels){
  assert.equal(supportsEffectiveExperiment(model),true,model.id);
  for(const input of [record,{...record,protocol:'undrained-triaxial'},{...record,rows:[...record.rows,record.rows[0]]}])for(const protocol of [0,1,2,3,4])for(const cycles of [0,3])for(const plot of ['stress','path','volume','pore']){
   assert.deepEqual(comparisonSeries(input,true,plot,protocol,cycles,model),old.comparisonSeries(input,true,plot,protocol,cycles),model.id);
  }
 }
});
test('missing, total, unknown and observable bindings cannot overlay rows or cached metadata',()=>{
 const cached={kind:record.kind,protocol:record.protocol,comparison:comparisonMetadata(record)};
 const rejected=[null,{},total,mutate(m=>delete m.formulation),mutate(m=>m.formulation.stress.scope='unknown'),mutate(m=>m.formulation.stress.source='observable'),mutate(m=>m.formulation.stress.measure='kirchhoff'),mutate(m=>m.schema_version='0.2')];
 for(const model of rejected){
  assert.equal(supportsEffectiveExperiment(model),false);
  for(const input of [record,cached])assert.equal(compatibleExperiment(input,1,0,model),false);
  for(const plot of ['stress','path','volume','pore'])assert.deepEqual(comparisonSeries(record,true,plot,1,0,model),[]);
 }
 assert.equal(compatibleExperiment(record,1),false); // omission fails closed
 assert.equal(compatibleExperiment(cached,1,0,effective),true);
 // Scope is checked anew after record metadata has already been cached.
 const changed=structuredClone(effective);assert.equal(compatibleExperiment(record,1,0,changed),true);
 changed.formulation.stress.scope='total';assert.equal(compatibleExperiment(record,1,0,changed),false);
 assert.deepEqual(measuredSeries(record,true,'axial_strain','q'),[[0,0],[.01,30000]]);
});
test('actual browser match handler rejects total scope before any input mutation',()=>{
 const app=read('web/app.js');
 const handler=app.slice(app.indexOf('function matchExperiment(){'),app.indexOf('async function loadExperiments('));
 for(const model of [total,effective]){
  const fields=new Map();const field=id=>{if(!fields.has(id))fields.set(id,{value:'untouched'});return fields.get(id);};
  const messages=[];let refreshes=0,updates=0,protocols=0;
  vm.runInNewContext(handler+';matchExperiment();',{
   experiment:structuredClone(record),model:()=>model,supportsEffectiveExperiment,toast:s=>messages.push(s),$:field,
   comparisonMetadata,setProtocol:()=>protocols++,refreshExperimentFilter:()=>refreshes++,scheduleUpdate:()=>updates++
  });
  if(model===total){assert.equal(fields.size,0);assert.equal(refreshes+updates+protocols,0);assert.match(messages[0],/effective-stress/);}
  else{assert.equal(field('protocol').value,'1');assert.equal(field('confinement').value,100);assert.equal(field('stress-ratio').value,1.3);assert.equal(field('state-e').value,.8);assert.equal(refreshes,1);assert.equal(updates,1);assert.equal(messages.length,0);}
 }
});
