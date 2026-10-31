// Explicit scoped laboratory transport; the live view remains legacy-only.
import {normalizeSettings,settingsCsv,verifyReturnedSettings} from './numerics.mjs';
import {normalizeLoading,createLoading,verifyReturnedLoading} from './loading.mjs';
const require=(v,message)=>{if(!v)throw Error(message);};
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const vector=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(finite);
const stable=v=>JSON.stringify(v&&typeof v==='object'?Array.isArray(v)?v.map(x=>JSON.parse(stable(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(stable(v[k]))])):v);
const same=(a,b)=>stable(a)===stable(b);
export function laboratoryStress(model){
 const f=model?.formulation,b=model?.schema_version==='0.1'?{source:'state',name:'sigma',measure:'cauchy',scope:'effective'}:f?.stress;
 const first=model?.state?.[0],role=first?.semantics?.role??(first?.transient||first?.multiplier?'temporary':'persistent');
 require(['0.1','0.3'].includes(model?.schema_version)&&(model.schema_version==='0.1'||f?.time_dependence==='strain_path'),'Laboratory requires a strain-path model.');
 require(b&&Object.keys(b).sort().join(',')==='measure,name,scope,source'&&b.source==='state'&&b.name==='sigma'&&b.measure==='cauchy'&&['effective','total'].includes(b.scope)&&first?.name==='sigma'&&first.shape==='sym'&&first.unit==='Pa'&&role==='persistent','Unsupported laboratory stress binding.');
 require(model.schema_version==='0.1'||(f.tensor_representation==='mandel'&&f.stress_sign==='compression_positive'&&f.strain_sign==='compression_positive'),'Unsupported laboratory stress convention.');
 return {...b,tensor_representation:'mandel',sign:'compression_positive'};
}
function poreContract(scope,protocol){
 require(['effective','total'].includes(scope)&&Number.isInteger(protocol)&&protocol>=0&&protocol<=4,'Invalid laboratory pore context.');
 return scope==='effective'&&[2,3].includes(protocol)?{quantity:'change',availability:'reconstructed',assumption:'fixed_radial_total_stress_incompressible_fluid_and_grains'}:{quantity:'change',availability:'unavailable',reason:scope==='total'?'total_stress_without_pore_pressure_law':'not_reconstructed_for_protocol'};
}
function context(s,catalogue){
 require(catalogue?.schema_version==='0.1'&&/^[a-f0-9]{64}$/.test(catalogue.sha256)&&Array.isArray(catalogue.models),'Compiled catalogue required.');
 const ids=catalogue.models.map(m=>m.id);require(ids.every(id=>typeof id==='string')&&new Set(ids).size===ids.length,'Ambiguous compiled catalogue.');
 const keys=['response_contract','stress_scope','model','parameters','initial','protocol','target','steps','cycles','integration_settings','loading'];
 require(s&&typeof s==='object'&&!Array.isArray(s)&&Object.keys(s).every(k=>keys.includes(k))&&s.response_contract==='stress-scope-0.1','Explicit laboratory scope contract required.');
 const model=catalogue.models.find(m=>m.id===s.model);require(model,'Model absent from compiled catalogue.');
 const stress=laboratoryStress(model);require(stress.scope===s.stress_scope,'Laboratory stress scope/model mismatch.');
 const fields=Object.values(model.parameters),n=model.state.reduce((n,f)=>n+(f.shape==='sym'?6:1),0);
 require(vector(s.parameters,fields.length)&&fields.every((f,i)=>s.parameters[i]>=f.min&&s.parameters[i]<=f.max),'Parameter shape or bounds mismatch.');
 require(vector(s.initial,n),'Explicit finite initial state required.');
 createLoading(s); // Validate protocol/amplitude/sample bounds without changing legacy loading.
 return {stress,n,settings:normalizeSettings(s.integration_settings),loading:normalizeLoading(s)};
}
export function validateScopedLaboratory(s,catalogue){context(s,catalogue);return s;}
export function laboratoryPoreSeries(result){
 const expected=poreContract(result?.stress?.scope,result?.protocol);
 require(same(result.pore_pressure,expected)&&Array.isArray(result.points),'Invalid pore-pressure availability descriptor.');
 const reconstructed=expected.availability==='reconstructed';
 for(const p of result.points)require(reconstructed?finite(p.u):p.u===null,'Invalid pore-pressure channel for declared availability.');
 if(reconstructed)require(result.points.every(p=>vector(p.strain,6)),'Invalid pore-pressure strain axis.');
 return {points:reconstructed?result.points.map(p=>[p.strain[0]*100,p.u/1000]):[],reason:expected.reason??null};
}
export function verifyScopedLaboratory(r,s,catalogue){
 const {stress,n,settings,loading}=context(s,catalogue);
 require(r&&typeof r.ok==='boolean'&&r.schema_version==='0.1'&&r.api_version==='experimental-laboratory-scope-0.1','Matching scoped laboratory engine required.');
 require(r.catalogue_hash===catalogue.sha256&&r.model===s.model&&same(r.stress,stress),'Laboratory response identity mismatch.');
 require(vector(r.parameters,s.parameters.length)&&same(r.parameters,s.parameters)&&vector(r.initial,n)&&same(r.initial,s.initial),'Laboratory parameter/initial mismatch.');
 verifyReturnedSettings(r,settings);
 require(same(r.integration_settings,settings),'Laboratory settings mismatch.');
 require(r.protocol===s.protocol&&r.steps===s.steps&&!Object.hasOwn(r,'research_scope'),'Laboratory protocol/range mismatch.');
 if(loading)verifyReturnedLoading({...r,api_version:'experimental-laboratory-controls-0.1'},s,catalogue.sha256);
 else require(r.loading===undefined&&r.target===s.target&&r.cycles===s.cycles,'Laboratory loading mismatch.');
 const points=r.points;
 require(Array.isArray(points)&&points.length<=s.steps+1&&(r.ok?points.length===s.steps+1:points.length<s.steps+1),'Invalid laboratory committed prefix.');
 for(const p of points){
  require(p&&vector(p.state,n)&&vector(p.strain,6)&&['control','p','q','q_signed','error'].every(k=>finite(p[k])),'Invalid laboratory point.');
  require(['iterations','substeps','rejected'].every(k=>Number.isInteger(p[k])&&p[k]>=0),'Invalid laboratory diagnostics.');
 }
 if(points.length)require(same(points[0].state,s.initial)&&points[0].strain.every(x=>x===0)&&points[0].control===0,'Laboratory initial point mismatch.');
 laboratoryPoreSeries(r);
 if(r.pore_pressure.availability==='reconstructed'&&points.length)require(points[0].u===0,'Pore-pressure change must start at zero.');
 return r;
}
export function runScopedLaboratory(engine,s,catalogue){
 s=structuredClone(s);catalogue=structuredClone(catalogue);const {settings,loading}=context(s,catalogue);
 const described=JSON.parse(engine.ccall('atlas_describe','string',[],[]));
 require(same(described,catalogue)&&described.models.every((m,i)=>Object.keys(m.parameters).join(',')===Object.keys(catalogue.models[i].parameters).join(',')),'Compiled laboratory catalogue/order mismatch.');
 const common=[s.model,s.parameters.join(','),s.initial.join(','),s.protocol];
 const args=loading?[...common,loading.controls_bits.join(','),settingsCsv(settings)]:[...common,s.target,s.steps,s.cycles,settingsCsv(settings)];
 const types=loading?['string','string','string','number','string','string']:['string','string','string','number','number','number','number','string'];
 const name=loading?'atlas_run_controls_scope_with_settings':'atlas_run_scope_with_settings';
 return verifyScopedLaboratory(JSON.parse(engine.ccall(name,'string',types,args)),s,catalogue);
}
