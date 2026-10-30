// Ordered recorded-run contract. No constitutive equations are evaluated here.
import {normalizeSettings,settingFields,settingsCsv,verifyReturnedSettings} from './numerics.mjs';
export const recordedVersion='experimental-recorded-run-0.1';
export const controlDefaults=Object.freeze({control_tolerance:1e-10,max_iterations:30,max_backtracks:10,max_material_trials:20000,finite_difference_step:1e-7});
export const restartDefaults=Object.freeze({max_restarts:1,restart_step:1e-4,restart_levels:8});
function object(v,allowed,required=allowed){
 if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!allowed.includes(k))||required.some(k=>!Object.hasOwn(v,k)))throw Error('Invalid recorded-run fields.');
}
function vector(v,n){if(!Array.isArray(v)||(n!==undefined&&v.length!==n)||v.some(x=>typeof x!=='number'||!Number.isFinite(x)))throw Error('Expected finite recorded numeric components.');}
function rank(rows){
 const a=rows.map(row=>{const scale=Math.max(...row.map(Math.abs));return row.map(x=>x/scale);});
 for(let k=0;k<6;k++){let p=k;for(let i=k+1;i<6;i++)if(Math.abs(a[i][k])>Math.abs(a[p][k]))p=i;
  if(Math.abs(a[p][k])<1e-14)return false;[a[p],a[k]]=[a[k],a[p]];
  for(let i=k+1;i<6;i++){const f=a[i][k]/a[k][k];for(let j=k+1;j<6;j++)a[i][j]-=f*a[k][j];a[i][k]=0;}
 }return true;
}
export function parseRecordedJSON(text){
 // JSON.parse rounds integer literals beyond binary64 precision. Reject such
 // literals before parsing, matching Python's explicit integer transport check.
 for(const token of text.matchAll(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/g)){
  const value=token[0];if(value[0]!=='"'&&!/[.eE]/.test(value)&&(!Number.isFinite(Number(value))||BigInt(value)!==BigInt(Number(value))))throw Error('Integer input is not exactly representable in binary64.');
 }
 return JSON.parse(text);
}
export function recordedSettings(s){
 const materialKeys=settingFields.map(f=>f.key),m=s.integration_settings===undefined?{}:s.integration_settings;object(m,materialKeys,[]);
 const material=normalizeSettings({...normalizeSettings(),...m});
 const supplied=s.control_settings===undefined?{}:s.control_settings;object(supplied,Object.keys(controlDefaults),[]);
 const control={...controlDefaults,...supplied};
 for(const [key,value] of Object.entries(control))if(typeof value!=='number'||!Number.isFinite(value))throw Error('Invalid recorded control setting: '+key);
 if(control.control_tolerance<=0||control.control_tolerance>1e-3||control.finite_difference_step<=0||control.finite_difference_step>1e-2)throw Error('Invalid recorded tolerance or probe step.');
 for(const [key,min,max] of [['max_iterations',1,1000],['max_backtracks',0,30],['max_material_trials',1,1000000]])if(!Number.isInteger(control[key])||control[key]<min||control[key]>max)throw Error('Invalid recorded control setting: '+key);
 let restarts;
 if(Object.hasOwn(s,'restart_settings')){
  object(s.restart_settings,Object.keys(restartDefaults),[]);restarts={...restartDefaults,...s.restart_settings};
  for(const [key,value] of Object.entries(restarts))if(typeof value!=='number'||!Number.isFinite(value))throw Error('Invalid recorded restart setting: '+key);
  if(!Number.isInteger(restarts.max_restarts)||restarts.max_restarts<0||restarts.max_restarts>16||!Number.isInteger(restarts.restart_levels)||restarts.restart_levels<1||restarts.restart_levels>16||restarts.restart_step<=0||restarts.restart_step>1e-2)throw Error('Invalid recorded restart policy.');
 }
 return {material,control,restarts};
}
export function validateRecordedRun(s){
 object(s,['version','model','path','parameters','initial','integration_settings','control_settings','restart_settings'],['version','model','path']);
 if(s.version!==recordedVersion||typeof s.model!=='string'||!s.model.length)throw Error('Unsupported recorded run or model.');
 for(const key of ['parameters','initial'])if(Object.hasOwn(s,key)){vector(s[key]);if(!s[key].length)throw Error('Omit '+key+' to use defaults.');}
 const p=s.path;object(p,['version','coordinate','initial_strain','controls','knots']);
 if(p.version!=='experimental-recorded-path-0.1')throw Error('Unsupported recorded path version.');
 object(p.coordinate,['name','unit','meaning']);
 if(typeof p.coordinate.name!=='string'||!p.coordinate.name.trim()||p.coordinate.name.length>64||p.coordinate.unit!=='1'||p.coordinate.meaning!=='path_order')throw Error('Coordinate must express dimensionless path order.');
 vector(p.initial_strain,6);
 if(!Array.isArray(p.controls)||p.controls.length!==6)throw Error('Six fixed control rows required.');
 for(const row of p.controls){object(row,['kind','coefficients']);vector(row.coefficients,6);if(!['strain','stress'].includes(row.kind)||!row.coefficients.some(x=>x!==0))throw Error('Invalid recorded control row.');}
 if(p.controls.every(c=>c.kind==='strain')&&!rank(p.controls.map(c=>c.coefficients)))throw Error('Dependent all-strain controls.');
 if(!Array.isArray(p.knots)||p.knots.length<2||p.knots.length>5001)throw Error('Use 2–5001 ordered knots.');
 let previous=-Infinity;
 for(const knot of p.knots){object(knot,['coordinate','targets']);vector(knot.targets,6);if(typeof knot.coordinate!=='number'||!Number.isFinite(knot.coordinate)||knot.coordinate<=previous)throw Error('Coordinates must strictly increase in input order.');previous=knot.coordinate;}
 recordedSettings(s);return s;
}
export function recordedWire(s){
 validateRecordedRun(s);
 return {controls:s.path.controls.flatMap(c=>[Number(c.kind==='stress'),...c.coefficients]),knots:s.path.knots.flatMap(k=>[k.coordinate,...k.targets])};
}
export function verifyRecordedResponse(r,s){
 const {controls,knots}=recordedWire(s),settings=recordedSettings(s);
 if(!r.api_version)throw Error(r.message||'Reload a matching recorded-replay engine.');
 const same=(a,b)=>Array.isArray(a)&&a.length===b.length&&a.every((v,i)=>v===b[i]);
 if(r.api_version!=='experimental-recorded-replay-0.1'||r.model!==s.model||!same(r.controls_wire,controls)||!same(r.knots_wire,knots)||!same(r.initial_strain,s.path.initial_strain)||Object.keys(settings.control).some(k=>r.control_settings?.[k]!==settings.control[k]))throw Error('Recorded engine response differs from request.');
 if(settings.restarts){
  if(!r.restart_settings||Object.keys(settings.restarts).some(k=>r.restart_settings[k]!==settings.restarts[k]))throw Error('Recorded restart policy differs from request.');
  const d=r.restart_diagnostics;
  if(!d||Object.keys(d).sort().join(',')!=='accepted,material_trials,searches'||Object.values(d).some(x=>!Number.isInteger(x)||x<0)||!Number.isInteger(r.material_trials)||r.material_trials<0||d.accepted>d.searches||d.material_trials>r.material_trials||(settings.restarts.max_restarts===0&&Object.values(d).some(x=>x!==0)))throw Error('Invalid recorded restart diagnostics.');
 }else if(['restart_settings','restart_diagnostics'].some(k=>Object.hasOwn(r,k)))throw Error('Unexpected recorded restart policy.');
 verifyReturnedSettings(r,settings.material);
 for(const key of ['initial','parameters'])if(s[key]&&!same(r[key],s[key]))throw Error('Recorded engine changed explicit '+key+'.');
 return r;
}
export function runRecorded(engine,s){
 const {controls,knots}=recordedWire(s),settings=recordedSettings(s);
 const args=[s.model,s.parameters?.join(',')??'',s.initial?.join(',')??'',s.path.initial_strain.join(','),controls.join(','),knots.join(','),settingsCsv(settings.material),Object.values(settings.control).join(',')];
 if(settings.restarts)args.push(Object.values(settings.restarts).join(','));
 const r=JSON.parse(engine.ccall(settings.restarts?'atlas_replay_recorded_with_restarts':'atlas_replay_recorded','string',Array(args.length).fill('string'),args));
 return verifyRecordedResponse(r,s);
}
export function recordedSeries(result,component){
 if(!Number.isInteger(component)||component<0||component>5)throw Error('Invalid Mandel component.');
 return {strain:result.points.map(p=>[p.coordinate,p.strain[component]]),stress:result.points.map(p=>[p.coordinate,p.state[component]/1000])};
}
