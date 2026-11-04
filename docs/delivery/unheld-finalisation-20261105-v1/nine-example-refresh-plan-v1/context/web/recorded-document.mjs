// Pure document boundary; no engine calls or automatic legacy-to-scoped migration.
import {parseRecordedJSON,validateRecordedRun} from './recorded.mjs';
import {validateScopedRecordedModel} from './recorded-scope.mjs';
import {verifyScopedRecordedResponse} from './recorded-scope-execution.mjs';
const legacyRun='experimental-recorded-run-0.1',scopedRun='experimental-recorded-run-0.2';
const legacyExport='experimental-recorded-replay-export-0.1',scopedExport='experimental-recorded-replay-export-0.2';
const require=(value,message)=>{if(!value)throw Error(message);};
function context(specification,catalogue){
 require(catalogue?.schema_version==='0.1'&&/^[a-f0-9]{64}$/.test(catalogue.sha256)&&Array.isArray(catalogue.models),'Compiled catalogue required.');
 const ids=catalogue.models.map(m=>m.id);
 require(ids.every(id=>typeof id==='string')&&new Set(ids).size===ids.length,'Ambiguous compiled catalogue.');
 const model=catalogue.models.find(m=>m.id===specification?.model);
 require(model,'This model is absent from the compiled catalogue.');
 const legacy=specification.version===legacyRun;
 require(legacy||specification.version===scopedRun,'Unsupported recorded document version.');
 if(legacy)validateRecordedRun(specification);
 const scoped=legacy?{...specification,version:scopedRun,stress_scope:'effective'}:specification;
 validateScopedRecordedModel(scoped,model);
 // A legacy request may use declared defaults. Modern scoped requests require
 // explicit v0.3 state, matching the dedicated execution adapter.
 const defaults=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);
 const initial=specification.initial??defaults,fields=Object.values(model.parameters),parameters=specification.parameters??fields.map(f=>f.default);
 const vector=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(x=>typeof x==='number'&&Number.isFinite(x));
 require(vector(initial,defaults.length),'Initial state shape mismatch.');
 require(vector(parameters,fields.length)&&fields.every((f,i)=>parameters[i]>=f.min&&parameters[i]<=f.max),'Parameter shape or bounds mismatch.');
 require(legacy||model.schema_version!=='0.3'||Object.hasOwn(specification,'initial'),'Model0.3 requires explicit state.');
 return {legacy,scope:scoped.stress_scope,scoped:legacy?{...scoped,initial}:scoped};
}
function verifyResult(result,specification,catalogue){
 const c=context(specification,catalogue);
 if(c.legacy){
  require(result?.api_version==='experimental-recorded-replay-0.1'&&!Object.hasOwn(result,'stress'),'Legacy recorded result contract required.');
  // Validate a detached compatibility view using the documented legacy effective
  // contract. The imported/exported bytes retain their original API and scope.
  verifyScopedRecordedResponse({...result,api_version:'experimental-recorded-replay-0.2',stress:{source:'state',name:'sigma',measure:'cauchy',scope:'effective',tensor_representation:'mandel',sign:'compression_positive'}},c.scoped,catalogue);
 }else verifyScopedRecordedResponse(result,c.scoped,catalogue);
 return c;
}
export function parseRecordedDocument(text,catalogue){
 const doc=parseRecordedJSON(text);
 require(doc&&typeof doc==='object'&&!Array.isArray(doc),'Recorded document must be an object.');
 if(Object.hasOwn(doc,'schema_version')){
  const keys=['schema_version','catalogue_hash','specification','result'];
  require(Object.keys(doc).length===keys.length&&keys.every(k=>Object.hasOwn(doc,k)),'Invalid recorded export fields.');
  require(doc.schema_version===legacyExport||doc.schema_version===scopedExport,'Unsupported recorded export version.');
  require(doc.catalogue_hash===catalogue?.sha256,'Recorded export uses a different catalogue.');
  require(doc.specification?.version===(doc.schema_version===legacyExport?legacyRun:scopedRun),'Recorded export/request version mismatch.');
  const c=verifyResult(doc.result,doc.specification,catalogue);
  return {specification:doc.specification,result:doc.result,stress_scope:c.scope};
 }
 const c=context(doc,catalogue);
 return {specification:doc,result:null,stress_scope:c.scope};
}
export function createRecordedDocument(specification,result,catalogue){
 const {legacy}=verifyResult(result,specification,catalogue);
 return structuredClone({schema_version:legacy?legacyExport:scopedExport,catalogue_hash:catalogue.sha256,specification,result});
}
export function recordedDocumentCSV(specification,result,catalogue){
 const {legacy,scope}=verifyResult(result,specification,catalogue);
 const labels=['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz'];
 const header=['coordinate_1',...labels.map(c=>'strain_'+c+'_1'),...labels.map(c=>scope+'_stress_'+c+'_Pa'),'control_error','iterations','substeps'];
 if(!legacy)header.push('stress_scope','pore_pressure_availability','pore_pressure_change_Pa');
 const rows=result.points.map(p=>{
  const row=[p.coordinate,...p.strain,...p.state.slice(0,6),p.control_error,p.diagnostics?.iterations,p.diagnostics?.substeps];
  require(row.every(x=>typeof x==='number'&&Number.isFinite(x)),'Invalid recorded CSV numeric channel.');
  // Recorded mechanics has no pore-pressure reconstruction, even for effective
  // stress. A blank value cannot be mistaken for a measured/reconstructed zero.
  if(!legacy)row.push(scope,'unavailable','');
  return row.join(',');
 });
 return [header.join(','),...rows].join('\n');
}
