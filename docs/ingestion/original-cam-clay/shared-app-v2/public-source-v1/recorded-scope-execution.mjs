// Explicit scoped adapter. The existing browser view keeps its legacy contract.
import {validateScopedRecordedModel,scopedRecordedWire} from './recorded-scope.mjs';
import {recordedSettings,verifyRecordedResponse} from './recorded.mjs';
import {settingsCsv} from './numerics.mjs';
const require=(value,message)=>{if(!value)throw Error(message);};
const stable=value=>JSON.stringify(value&&typeof value==='object'?Array.isArray(value)?value.map(v=>JSON.parse(stable(v))):Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(stable(value[k]))])):value);
const same=(a,b)=>stable(a)===stable(b);
const vector=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(x=>typeof x==='number'&&Number.isFinite(x));
function context(s,catalogue){
 require(catalogue?.schema_version==='0.1'&&/^[a-f0-9]{64}$/.test(catalogue.sha256)&&Array.isArray(catalogue.models),'Compiled catalogue required.');
 const ids=catalogue.models.map(m=>m.id);require(ids.every(x=>typeof x==='string')&&new Set(ids).size===ids.length,'Ambiguous compiled catalogue.');
 const model=catalogue.models.find(m=>m.id===s?.model);require(model,'Model absent from compiled catalogue.');validateScopedRecordedModel(s,model);
 const wire=scopedRecordedWire(s,model),fields=Object.values(model.parameters),parameters=s.parameters??fields.map(p=>p.default);
 require(vector(parameters,fields.length)&&fields.every((p,i)=>parameters[i]>=p.min&&parameters[i]<=p.max),'Parameter shape or bounds mismatch.');
 const defaults=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);require(model.schema_version!=='0.3'||Object.hasOwn(s,'initial'),'Model0.3 requires explicit state.');
 const initial=s.initial??defaults;require(vector(initial,defaults.length),'Initial state shape mismatch.');return {model,wire,parameters,initial};
}
export function verifyScopedRecordedResponse(r,s,catalogue){
 const {parameters,initial}=context(s,catalogue);
 require(r&&typeof r.ok==='boolean'&&r.api_version==='experimental-recorded-replay-0.2','Matching scoped recorded engine required.');
 require(r.catalogue_hash===catalogue.sha256&&r.model===s.model,'Scoped recorded catalogue/model mismatch.');
 require(same(r.stress,{source:'state',name:'sigma',measure:'cauchy',scope:s.stress_scope,tensor_representation:'mandel',sign:'compression_positive'}),'Scoped recorded stress mismatch.');
 const {stress_scope,...legacy}=s;legacy.version='experimental-recorded-run-0.1';
 verifyRecordedResponse({...r,api_version:'experimental-recorded-replay-0.1'},legacy);
 const settings=recordedSettings(s);require(same(r.control_settings,settings.control)&&same(r.integration_settings,settings.material),'Scoped recorded settings mismatch.');
 if(settings.restarts)require(same(r.restart_settings,settings.restarts),'Scoped recorded restart mismatch.');
 require(vector(r.parameters,parameters.length)&&same(r.parameters,parameters)&&vector(r.initial,initial.length)&&same(r.initial,initial),'Scoped recorded parameter/initial mismatch.');
 require(Number.isInteger(r.material_trials)&&r.material_trials>=0,'Invalid scoped material trial count.');
 const points=r.points,n=s.path.knots.length,f=r.failed_knot;
 require(Array.isArray(points)&&Number.isInteger(f)&&((r.ok&&f===-1&&points.length===n)||(!r.ok&&((!points.length&&f===-1)||(f>=1&&f<n&&points.length===f)))),'Incomplete scoped recorded result.');
 for(let i=0;i<points.length;i++)require(points[i].coordinate===s.path.knots[i].coordinate&&vector(points[i].state,initial.length)&&vector(points[i].strain,6),'Invalid scoped recorded point.');
 require(vector(r.state,initial.length)&&vector(r.strain,6),'Invalid scoped final state.');
 if(points.length)require(same(points[0].state,initial)&&same(points[0].strain,s.path.initial_strain)&&same(r.state,points.at(-1).state)&&same(r.strain,points.at(-1).strain),'Scoped recorded prefix mismatch.');
 else require(same(r.state,initial)&&same(r.strain,s.path.initial_strain),'Invalid empty scoped failure state.');
 return r;
}
export function runScopedRecorded(engine,s,catalogue){
 s=structuredClone(s);catalogue=structuredClone(catalogue);const {wire}=context(s,catalogue),settings=recordedSettings(s);
 const described=JSON.parse(engine.ccall('atlas_describe','string',[],[]));
 require(same(described,catalogue),'Native compiled catalogue mismatch.');
 require(described.models.every((m,i)=>Object.keys(m.parameters).join(',')===Object.keys(catalogue.models[i].parameters).join(',')),'Compiled parameter order mismatch.');
 const args=[s.model,s.parameters?.join(',')??'',s.initial?.join(',')??'',s.path.initial_strain.join(','),wire.controls.join(','),wire.knots.join(','),settingsCsv(settings.material),Object.values(settings.control).join(',')];
 if(settings.restarts)args.push(Object.values(settings.restarts).join(','));args.push(s.stress_scope);
 const name=settings.restarts?'atlas_replay_recorded_scope_with_restarts':'atlas_replay_recorded_scope';
 const r=JSON.parse(engine.ccall(name,'string',Array(args.length).fill('string'),args));return verifyScopedRecordedResponse(r,s,catalogue);
}
