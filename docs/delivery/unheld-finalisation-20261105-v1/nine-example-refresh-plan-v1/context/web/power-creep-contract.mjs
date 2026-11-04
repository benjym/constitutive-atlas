// Bounded public UI request/replay contract. No constitutive equation evaluation.
import {parseRecordedJSON} from './recorded.mjs';
export const defaults=Object.freeze({mode:'relaxation',duration:10,samples:20,pressure:1,initialQ:.3,bulk:20,shear:12,pref:1,b1:.002,n1:1,b2:.001,n2:3});
const limits={duration:[.001,10000],samples:[1,200],pressure:[-1000,1000],initialQ:[-1000,1000],bulk:[.000001,1e8],shear:[.000001,1e8],pref:[.000001,1e6],b1:[0,1000],n1:[1,10],b2:[0,1000],n2:[1,10]};
export function validateControls(c){
 if(!c||typeof c!=='object'||!['creep','relaxation'].includes(c.mode))throw Error('Choose creep or relaxation.');
 for(const [key,[lo,hi]] of Object.entries(limits))if(typeof c[key]!=='number'||!Number.isFinite(c[key])||c[key]<lo||c[key]>hi)throw Error(key+' is outside the supported control bounds.');
 if(!Number.isInteger(c.samples))throw Error('Output intervals must be an integer.');
 return {...c};
}
export function request(c,identity){
 c=validateControls(c);const p=c.pressure*1e6,q=c.initialQ*1e6,stress=+(c.mode==='creep');
 return [identity.model,[c.bulk*1e6,c.shear*1e6,c.pref*1e6,c.b1,c.n1,c.b2,c.n2,1].join(','),[p+2*q/3,p-q/3,p-q/3,0,0,0].join(','),'0,0,0,0,0,0','0,0,0,0,0,0',[c.duration,c.samples,...Array.from({length:6},()=>[stress,0,0]).flat()].join(','),c.mode,0,1e-9,1e-12,1e-12,.1,200000,1e-10,40];
}
const vector=(s,n)=>{if(typeof s!=='string'||s.split(',').some(v=>!v.trim()))throw Error('Invalid imported numeric wire.');const a=s.split(',').map(Number);if(a.length!==n||a.some(v=>!Number.isFinite(v)))throw Error('Invalid imported numeric components.');return a;};
export function importRun(text,identity){
 const data=parseRecordedJSON(text),a=data?.request?.args;
 if(data?.request?.function!=='atlas_run_schedule'||!Array.isArray(a)||a.length!==15)throw Error('Expected an exported power-creep schedule.');
 for(const key of ['model','model_sha256','catalogue_hash','module_sha256','wasm_sha256'])if(data.provenance?.[key]!==identity[key])throw Error('Imported '+key+' differs from this engine.');
 const p=vector(a[1],8),s=vector(a[2],6),wire=vector(a[5],20);
 const c=validateControls({mode:a[6],duration:wire[0],samples:wire[1],pressure:(s[0]+s[1]+s[2])/3e6,initialQ:(s[0]-s[1])/1e6,bulk:p[0]/1e6,shear:p[1]/1e6,pref:p[2]/1e6,b1:p[3],n1:p[4],b2:p[5],n2:p[6]});
 const expected=request(c,identity);
 for(let i=0;i<a.length;i++){
  if([1,2,3,4,5].includes(i)){
   const x=vector(a[i],expected[i].split(',').length),y=vector(expected[i],x.length);
   if(x.some((v,j)=>Math.abs(v-y[j])>1e-9+1e-14*Math.abs(y[j])))throw Error('Imported request is outside the supported two-experiment interface.');
  }else if(a[i]!==expected[i])throw Error('Imported settings differ from the qualified public interface.');
 }
 return c;
}
export function verifyResult(result,identity){
 if(result.catalogue_hash!==identity.catalogue_hash)throw Error('Engine catalogue identity mismatch.');
 if(!result.ok)throw Error(result.message||'Solver rejected this history.');
 if(!Array.isArray(result.points)||result.points.length<2)throw Error('Incomplete solver history.');
 for(const p of result.points)for(const [key,n] of [['state',6],['strain',6],['observables',9]])if(!Array.isArray(p[key])||p[key].length!==n||p[key].some(v=>typeof v!=='number'||!Number.isFinite(v)))throw Error('Invalid returned '+key+'.');
 return result;
}
