// Kelvin–Voigt atlas transport/validation only; constitutive equations remain in common Wasm.
export const modelId='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';
export const modelSha256='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da';
export const defaults=Object.freeze({mode:'creep',duration:8,samples:8,start:0,parameters:[20e6,12e6,2],initial:[0,0,0,0,0,0],initialRates:[.001,-.0005,-.0005,.0004,-.0002,.0003],rates:[.001,-.0005,-.0005,.0004,-.0002,.0003]});
export const solver=Object.freeze({method:'backward-euler-step-doubling',relative_tolerance:3e-11,absolute_scale_fraction:3e-14,minimum_step:1e-12,maximum_step:1e6,maximum_substeps:1000000,nonlinear_tolerance:1e-10,maximum_iterations:40,maximum_depth:40});
export const types=Object.freeze([...Array(7).fill('string'),...Array(8).fill('number')]);
const vector=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(x=>typeof x==='number'&&Number.isFinite(x));
export function parseRunJSON(text){
 // Strict token checks follow the general atlas recorded-JSON policy without a UI dependency.
 if(typeof text!=='string')throw Error('Expected JSON text.');const data=JSON.parse(text),stack=[];
 for(const token of text.matchAll(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}[\],:]/g)){
  const value=token[0],frame=stack.at(-1);
  if(value==='{')stack.push({names:new Set(),key:true});else if(value==='[')stack.push(null);else if(value==='}'||value===']')stack.pop();else if(value===','){if(frame)frame.key=true;}else if(value===':'){if(frame)frame.key=false;}
  else if(value[0]==='"'){if(frame?.key){const name=JSON.parse(value);if(frame.names.has(name))throw Error('Duplicate JSON key: '+name);frame.names.add(name);}}
  else{const number=Number(value);if(!Number.isFinite(number))throw Error('JSON number outside finite binary64 range.');if(!/[.eE]/.test(value)&&BigInt(value)!==BigInt(number))throw Error('Integer is not exactly representable in binary64.');}
 }return data;
}
export function validateControls(c){
 if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).length!==Object.keys(defaults).length||Object.keys(c).some(k=>!Object.hasOwn(defaults,k))||!['hold','creep','rate'].includes(c.mode))throw Error('Choose strain hold, creep or strain-rate loading with explicit controls.');
 if(!Number.isFinite(c.duration)||c.duration<1e-6||c.duration>10000||!Number.isInteger(c.samples)||c.samples<1||c.samples>200||!Number.isFinite(c.start)||c.start<0||!Number.isFinite(c.start+c.duration)||c.start+c.duration<=c.start)throw Error('Use finite nonnegative start time, duration1e-6–10000s and1–200 intervals.');
 for(const [key,n]of [['parameters',3],['initial',6],['initialRates',6],['rates',6]])if(!vector(c[key],n))throw Error(key+' requires '+n+' finite explicit components.');
 if(c.parameters.some(x=>x<1e-12||x>1e30))throw Error('Positive coefficients must lie within declared machine bounds1e-12–1e30; this is not a qualified material range.');
 return structuredClone(c);
}
export function request(c,identity){
 c=validateControls(c);if(identity?.model!==modelId||identity.model_sha256!==modelSha256)throw Error('Wrong Kelvin–Voigt model identity.');
 return [modelId,c.parameters.join(','),c.initial.join(','),c.initial.slice(0,6).join(','),c.initialRates.join(','),[c.duration,c.samples,...c.rates.flatMap(v=>[+(c.mode==='creep'),+(c.mode==='rate'),c.mode==='rate'?v:0])].join(','),c.mode==='hold'?'relaxation':c.mode,c.start,solver.relative_tolerance,solver.absolute_scale_fraction,solver.minimum_step,solver.maximum_step,solver.maximum_substeps,solver.nonlinear_tolerance,solver.maximum_iterations];
}
export function verifyResult(r,identity,c){
 c=validateControls(c);
 if(r?.catalogue_hash!==identity.catalogue_hash||r.model!==modelId)throw Error('Engine/model catalogue mismatch.');if(!r.ok)throw Error(r.message||'Engine rejected history.');
 if(r.units!=='SI'||r.schema_version!=='0.2'||r.start_time!==c.start||JSON.stringify(r.parameters)!==JSON.stringify(c.parameters)||JSON.stringify(r.initial)!==JSON.stringify(c.initial)||JSON.stringify(r.initial_strain)!==JSON.stringify(c.initial.slice(0,6))||JSON.stringify(r.initial_strain_rate)!==JSON.stringify(c.initialRates))throw Error('Returned model/state contract mismatch.');
 if(!r.solver||Object.keys(r.solver).length!==Object.keys(solver).length||Object.entries(solver).some(([k,v])=>r.solver[k]!==v))throw Error('Returned solver settings mismatch.');
 if(!Array.isArray(r.points)||r.points.length!==c.samples+2)throw Error('Incomplete Kelvin–Voigt history.');
 for(const [i,p]of r.points.entries()){
  const time=i<2?c.start:c.start+c.duration*(i-1)/c.samples;
  if(!Number.isFinite(p.time)||Math.abs(p.time-time)>1e-12*Math.max(1,Math.abs(time))||p.side!==(i===1?'right':'left')||p.segment!==(i===0?-1:0))throw Error('Invalid Kelvin–Voigt sample/event time.');
  const unresolved=i===1&&c.mode==='creep'&&Array.isArray(p.strain_rate)&&p.strain_rate.length===6&&p.strain_rate.every(x=>x===null);
  for(const [key,n]of [['state',6],['strain',6],['strain_rate',6],['observables',6]])if(!(key==='strain_rate'&&unresolved)&&!vector(p[key],n))throw Error('Invalid returned '+key+'.');
  if(p.strain.some((v,j)=>Math.abs(v-p.state[j])>64*Number.EPSILON*Math.max(1,Math.abs(v),Math.abs(p.state[j]))))throw Error('Stored strain/state mismatch.');
 }
 if(JSON.stringify(r.points[0].strain_rate)!==JSON.stringify(c.initialRates))throw Error('Incoming initial rate changed.');
 if(JSON.stringify(r.points[0].state)!==JSON.stringify(c.initial)||JSON.stringify(r.points[1].state)!==JSON.stringify(c.initial))throw Error('Initial complete state changed at event.');
 return r;
}
export function verifyReplay(actual,expected){
 const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,canonical(value[key])])):value;
 if(JSON.stringify(canonical(actual))!==JSON.stringify(canonical(expected)))throw Error('Replayed complete result differs from saved output.');return actual;
}
export function importRun(text,identity,{withResult=false}={}){
 const data=parseRunJSON(text);if(data?.kind!=='atlas-kelvin-voigt-laboratory-v1')throw Error('Expected an exported Kelvin–Voigt main-atlas run.');
 for(const key of Object.keys(identity))if(JSON.stringify(data.provenance?.[key])!==JSON.stringify(identity[key]))throw Error('Imported '+key+' differs from this exact package.');
 const c=validateControls(data.controls),args=request(c,identity);
 if(data.request?.function!=='atlas_run_schedule'||JSON.stringify(data.request.args)!==JSON.stringify(args))throw Error('Imported request differs from explicit controls/settings.');
 verifyResult(data.result,identity,c);return withResult?{controls:c,result:structuredClone(data.result)}:c;
}
