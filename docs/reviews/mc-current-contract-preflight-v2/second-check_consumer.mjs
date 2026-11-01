import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createLoading,controlBits,controlFromBits} from '../../../web/loading.mjs';
import {runScopedLaboratory} from '../../../web/laboratory-scope.mjs';
import {createLaboratoryDocument,parseLaboratoryDocument} from '../../../web/laboratory-document.mjs';
const read=n=>JSON.parse(readFileSync(new URL(n,import.meta.url),'utf8'));
const catalogue=read('./catalogue.json'),specs=read('./contracts.json'),frames=read('./source-ideal.json').frames,input=read('../mc-browser-loading-paths-v1/source-input.json');
const negatives=[],falsePasses=[];let controls=0,deltas=0,points=0,calls=0;
for(let j=0;j<specs.length;j++){
 const {id,specification:s}=specs[j],result=frames[j].result,path=input.paths.find(x=>x.id===id);assert.equal(frames[j].id,id);
 assert.deepEqual(createLoading(s),s.loading);
 for(let i=0;i<s.loading.controls_bits.length;i++){assert.equal(s.loading.controls_bits[i],path.controls_bits[i]);controls++;if(i){assert.equal(controlBits(controlFromBits(path.controls_bits[i])-controlFromBits(path.controls_bits[i-1])),path.control_delta_bits[i-1]);deltas++;}}
 const engine={ccall(name,type,types,args){calls++;if(name==='atlas_describe'){assert.deepEqual(args,[]);return JSON.stringify(catalogue);}assert.equal(name,'atlas_run_controls_scope_with_settings');assert.equal(args.length,6);assert.equal(args[0],s.model);assert.equal(args[1],s.parameters.join(','));assert.equal(args[2],s.initial.join(','));assert.equal(args[3],s.protocol);assert.equal(args[4],s.loading.controls_bits.join(','));assert.equal(args[5],['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'].map(k=>s.integration_settings[k]).join(','));return JSON.stringify(result);}};
 const observed=runScopedLaboratory(engine,s,catalogue);assert.deepEqual(observed,result);points+=observed.points.length;
 const document=createLaboratoryDocument(s,observed,catalogue),text=JSON.stringify(document),imported=parseLaboratoryDocument(text,catalogue);assert.deepEqual(imported,s);assert.deepEqual(runScopedLaboratory(engine,imported,catalogue),result);
 for(const [label,mutate] of [['wrong scope',d=>d.result.stress.scope='total'],['unavailable pore pressure made zero',d=>{d.result.pore_pressure={quantity:'change',availability:'unavailable',reason:'not_reconstructed_for_protocol'};d.result.points.forEach(p=>p.u=0);}],['wrong control bits',d=>d.result.loading.controls_bits[1]='0000000000000000'],['missing state component',d=>d.result.points[0].state.pop()],['wrong catalogue',d=>d.catalogue_hash='wrong']]){
  const bad=structuredClone(document);mutate(bad);assert.throws(()=>parseLaboratoryDocument(JSON.stringify(bad),catalogue));negatives.push(id+': '+label);
 }
 for(const [label,text] of [['duplicate envelope key','{"schema_version":"duplicate",'+JSON.stringify(document).slice(1)],['overflow unused result field',JSON.stringify(document).replace('"result":{','"result":{"unused":1e999,')]]){let rejected=false;try{parseLaboratoryDocument(text,catalogue);}catch{rejected=true;}if(rejected)negatives.push(id+': '+label);else falsePasses.push(id+': '+label);}
}
assert.equal(specs.length,14);assert.equal(points,834);assert.equal(controls,834);assert.equal(deltas,820);assert.equal(calls,56);
const report={passed:falsePasses.length===0,false_passes:falsePasses,scope:'manufactured source-ideal transport and document preflight; no material engine',models:catalogue.models.length,paths:14,points,controls,deltas,synthetic_callback_calls:calls,negative_checks:negatives.length,negatives,constitutive_calls:0};
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');else console.log(JSON.stringify(report));
