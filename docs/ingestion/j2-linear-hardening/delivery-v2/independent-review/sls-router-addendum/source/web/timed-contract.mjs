// Generic physical-time hold interface. Constitutive equations remain in Wasm.
import {parseRecordedJSON} from './recorded.mjs';
export const modelId='burgers-itasca900-dry-zero-spin-ode';
export const defaults=Object.freeze({mode:'relaxation',duration:2,samples:8,start:4,parameters:[11000000,6000000,2000000,3000000,4000000],initial:[140000,80000,80000,12000,-8000,4000,.002,-.001,-.001,.0003,-.0002,.0001],strain:[0,0,0,0,0,0],rate:[0,0,0,0,0,0]});
const vector=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(v=>typeof v==='number'&&Number.isFinite(v));
export function validateControls(c){
 if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).length!==Object.keys(defaults).length||Object.keys(c).some(k=>!Object.hasOwn(defaults,k))||!['creep','relaxation'].includes(c.mode))throw Error('Choose creep or relaxation.');
 if(!Number.isFinite(c.duration)||c.duration<=0||c.duration>100||!Number.isInteger(c.samples)||c.samples<1||c.samples>200||!Number.isFinite(c.start)||c.start<0)throw Error('Use positive duration up to100s,1–200 intervals and nonnegative start time.');
 for(const [key,n]of [['parameters',5],['initial',12],['strain',6],['rate',6]])if(!vector(c[key],n))throw Error(key+' requires '+n+' finite explicit components.');
 if(c.parameters.some(v=>v<=0))throw Error('Moduli and viscosities must be positive.');
 if(Math.abs(c.initial[6]+c.initial[7]+c.initial[8])>1e-12)throw Error('Kelvin strain must be deviatoric: sum of normal components <=1e-12.');
 return structuredClone(c);
}
export function request(c,identity){
 c=validateControls(c);if(identity.model!==modelId)throw Error('Wrong physical-time model.');
 return [identity.model,c.parameters.join(','),c.initial.join(','),c.strain.join(','),c.rate.join(','),[c.duration,c.samples,...Array.from({length:6},()=>[+(c.mode==='creep'),0,0]).flat()].join(','),c.mode==='creep'?'creep':'hold',c.start,2e-7,2e-10,1e-12,.125,200000,1e-11,40];
}
export function importRun(text,identity){
 const data=parseRecordedJSON(text);
 if(data?.kind!=='atlas-timed-hold-v1')throw Error('Expected an exported physical-time hold run.');
 for(const key of ['model','model_sha256','catalogue_hash','module_sha256','wasm_sha256','approval_sha256','review_sha256'])if(data.provenance?.[key]!==identity[key])throw Error('Imported '+key+' differs from this package.');
 const c=validateControls(data.controls),args=request(c,identity);
 if(data.request?.function!=='atlas_run_schedule'||JSON.stringify(data.request.args)!==JSON.stringify(args))throw Error('Imported request differs from the supported controls/settings.');
 return c;
}
export function verifyResult(r,identity,c){
 if(r.catalogue_hash!==identity.catalogue_hash)throw Error('Engine catalogue mismatch.');
 if(!r.ok)throw Error(r.message||'Engine rejected history.');
 const expectedSolver={method:'backward-euler-step-doubling',relative_tolerance:2e-7,absolute_scale_fraction:2e-10,minimum_step:1e-12,maximum_step:.125,maximum_substeps:200000,nonlinear_tolerance:1e-11,maximum_iterations:40,maximum_depth:40};
 if(JSON.stringify(r.solver)!==JSON.stringify(expectedSolver)||r.units!=='SI'||r.schema_version!=='0.2'||r.start_time!==c.start||JSON.stringify(r.parameters)!==JSON.stringify(c.parameters))throw Error('Returned timed contract/settings mismatch.');
 if(r.model!==undefined&&r.model!==identity.model)throw Error('Wrong returned model.');
 if(!Array.isArray(r.points)||r.points.length!==c.samples+2)throw Error('Incomplete timed history.');
 let previous=-Infinity;
 for(const [i,p] of r.points.entries()){
  const expectedTime=i<2?c.start:c.start+c.duration*(i-1)/c.samples;
  if(Math.abs(p.time-expectedTime)>1e-12*Math.max(1,Math.abs(expectedTime))||p.side!==(i===1?'right':'left')||p.segment!==(i===0?-1:0))throw Error('Unexpected schedule sample/event.');
  const initialEvent=i===1&&p.time===c.start&&p.side==='right'&&r.points[0].side==='left';
  if(!Number.isFinite(p.time)||(!initialEvent&&p.time<=previous))throw Error('Invalid physical time.');previous=p.time;
  const unresolvedRate=initialEvent&&c.mode==='creep'&&Array.isArray(p.strain_rate)&&p.strain_rate.length===6&&p.strain_rate.every(v=>v===null);
  for(const [key,n]of [['state',12],['strain',6],['strain_rate',6],['observables',6]])if(!(key==='strain_rate'&&unresolvedRate)&&!vector(p[key],n))throw Error('Invalid returned '+key+'.');
  if(p.observables.some((v,i)=>v!==p.state[i]))throw Error('Stress observable mismatch.');
  if(Math.abs(p.state[6]+p.state[7]+p.state[8])>1e-12)throw Error('Returned Kelvin trace invalid.');
 }
 if(r.points[1].time!==c.start||JSON.stringify(r.points[0].state)!==JSON.stringify(c.initial)||JSON.stringify(r.points[1].state)!==JSON.stringify(c.initial)||JSON.stringify(r.points[0].strain)!==JSON.stringify(c.strain)||JSON.stringify(r.points[1].strain)!==JSON.stringify(c.strain))throw Error('Invalid initial event state.');
 if(r.points[0].time!==c.start||Math.abs(r.points.at(-1).time-(c.start+c.duration))>1e-12)throw Error('Wrong returned time range.');
 return r;
}
