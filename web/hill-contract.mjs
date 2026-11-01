// Pure request, identity and transaction contract; physics stays in the common engine.
export const MODEL='hill-abaqus2025-perfect-be';
export const MODEL_SHA256='1f98a70a68098d95804639e3abeb69da57e7ceeaf302d621e4738db4340e2621';
export const SETTINGS=Object.freeze([1e-11,1e-6,60,0,1,20]);
export const MAX_ROWS=200;
export const FORMAT='atlas-hill-replay-v1';
const ID_KEYS=['model','model_sha256','catalogue_hash','catalogue_sha256','module_sha256','wasm_sha256','approval_sha256','review_sha256'];
const SETTINGS_KEYS=['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'];
const clone=x=>JSON.parse(JSON.stringify(x));
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const requireThat=(condition,message)=>{if(!condition)throw Error(message);};
const vector=(v,n,label)=>requireThat(Array.isArray(v)&&v.length===n&&v.every(x=>typeof x==='number'&&Number.isFinite(x)),`${label}: expected ${n} finite numbers.`);
export function parseNumbers(text,n,label='Values'){
 const parts=text.trim().split(',').map(x=>x.trim());
 requireThat(parts.length===n&&parts.every(x=>x!==''),`${label}: expected ${n} comma-separated numbers.`);
 const values=parts.map(Number);vector(values,n,label);return values;
}
export function parsePath(text){
 const rows=text.trim().split(/\r?\n/);requireThat(rows.length<=MAX_ROWS,`At most ${MAX_ROWS} increment rows are allowed.`);
 return rows.map((row,i)=>parseNumbers(row,6,`Row ${i+1}`));
}
export function preset(){return {model:MODEL,parameters:[1e5,20e6,12e6,60000,.7,.5,.3,1.2,1.7,2],initial:Array(7).fill(0),settings:[...SETTINGS],increments:[[.003,-.0015,-.0015,0,0,0],[-.003,.0015,.0015,0,0,0],[0,0,0,0,0,0]]};}
export function validateRequest(input){
 requireThat(input&&input.model===MODEL,'Unsupported model.');
 requireThat(equal(Object.keys(input).sort(),['increments','initial','model','parameters','settings']),'Unexpected request fields.');
 vector(input.parameters,10,'Parameters');vector(input.initial,7,'Initial state');vector(input.settings,6,'Settings');
 const minimum=[1,1,1,1,...Array(6).fill(1e-6)],maximum=[1e15,1e15,1e15,1e13,...Array(6).fill(100)];
 requireThat(input.parameters.every((x,i)=>x>=minimum[i]&&x<=maximum[i]),'Parameters outside the declared machine envelope.');
 requireThat(equal(input.settings,SETTINGS),'This laboratory requires its frozen no-subdivision solver settings.');
 requireThat(input.initial[6]===0,'Initial temporary gamma must be zero.');
 const [pRef,,,y,F,Gh,Hh,L,M,N]=input.parameters;
 const [xx,yy,zz,xy,yz,xz]=input.initial;
 const q=Math.hypot(Math.sqrt(F)*(yy-zz),Math.sqrt(Gh)*(zz-xx),Math.sqrt(Hh)*(xx-yy),Math.sqrt(N)*xy,Math.sqrt(L)*yz,Math.sqrt(M)*xz);
 requireThat(Number.isFinite(q)&&q<=Math.sqrt(y*y+2*y*pRef*1e-10),'Initial stress must lie inside/on the Hill yield surface.');
 requireThat(Array.isArray(input.increments)&&input.increments.length>=1&&input.increments.length<=MAX_ROWS,`Supply 1–${MAX_ROWS} strain-increment rows.`);
 let sum=Array(6).fill(0);
 for(const [i,row]of input.increments.entries()){vector(row,6,`Row ${i+1}`);sum=sum.map((x,j)=>x+row[j]);requireThat(sum.every(Number.isFinite),'Cumulative strain overflow.');}
 return clone(input);
}
export function validateIdentity(identity){
 requireThat(identity&&equal(Object.keys(identity).sort(),[...ID_KEYS].sort()),'Incomplete package identity.');
 requireThat(identity.model===MODEL&&identity.model_sha256===MODEL_SHA256,'Unexpected exact model identity.');
 requireThat(ID_KEYS.slice(1).every(k=>typeof identity[k]==='string'&&/^[0-9a-f]{64}$/.test(identity[k])),'Invalid package digest.');
 return clone(identity);
}
export function wire(request,state,row){return {function:'atlas_integrate_with_settings',types:Array(5).fill('string'),args:[MODEL,request.parameters.join(','),state.join(','),row.join(','),request.settings.join(',')]};}
export function validateResponse(response,request,state,row,identity){
 requireThat(response&&typeof response.ok==='boolean','Invalid engine response.');
 // Even a failure must bind the attempted row and return the complete incoming state.
 requireThat(response.catalogue_hash===identity.catalogue_hash&&response.model===MODEL,'Engine catalogue/model mismatch.');
 for(const [k,v]of [['parameters',request.parameters],['initial',state],['strain',row]])requireThat(equal(response[k],v),`Engine ${k} echo mismatch.`);
 vector(response.state,7,'Returned full state');
 requireThat(response.integration_settings?.version==='incremental-settings-0.1'&&response.integration_settings.norm==='scaled_component_max'&&SETTINGS_KEYS.every((k,i)=>response.integration_settings[k]===request.settings[i]),'Engine settings mismatch.');
 requireThat(typeof response.message==='string','Missing engine message.');
 if(response.ok){requireThat(equal(response.diagnostics?.increment_fractions,[1])&&response.diagnostics.substeps===1,'Unexpected internal subdivision.');}
 else requireThat(equal(response.state,state),'Failed row did not roll back the full incoming state.');
 return clone(response);
}
export async function runPath(call,input,packageIdentity,{beforeStep=async()=>{}}={}){
 const request=validateRequest(input),identity=validateIdentity(packageIdentity);let state=[...request.initial],strain=Array(6).fill(0);
 const points=[{step:0,strain:[...strain],state:[...state]}],records=[];
 for(let i=0;i<request.increments.length;i++){
  await beforeStep(i);const row=request.increments[i],w=wire(request,state,row);
  let response;
  try{response=validateResponse(await call(clone(w)),request,state,row,identity);}
  catch(error){records.push({row:i+1,wire:w,response:null,error:String(error.message)});return {format:FORMAT,provenance:identity,request,ok:false,failedRow:i+1,message:'Engine response rejected: '+error.message,points,records};}
  records.push({row:i+1,wire:w,response});
  if(!response.ok)return {format:FORMAT,provenance:identity,request,ok:false,failedRow:i+1,message:response.message,points,records};
  state=[...response.state];strain=strain.map((x,j)=>x+row[j]);points.push({step:i+1,strain:[...strain],state:[...state]});
 }
 return {format:FORMAT,provenance:identity,request,ok:true,failedRow:null,message:'',points,records};
}
export function replayRequest(document,identity){
 validateIdentity(identity);requireThat(document?.format===FORMAT,'Unsupported replay format.');
 requireThat(document.provenance&&equal(Object.keys(document.provenance).sort(),Object.keys(identity).sort())&&Object.keys(identity).every(k=>document.provenance[k]===identity[k]),'Replay identity does not match this exact package.');
 // Saved results are never trusted: reconstruct the complete immutable starting request.
 return validateRequest(document.request);
}
