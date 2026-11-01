// Pure request, identity and transaction contract; physics stays in the common engine.
export const MODEL='orthotropic-linear-elastic-ogs';
export const MODEL_SHA256='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14';
export const SETTINGS=Object.freeze([1e-11,1e-6,60,0,1,20]);
export const MAX_ROWS=200;
export const FORMAT='atlas-orthotropic-replay-v1';
const ID_KEYS=['model','model_sha256','catalogue_hash','catalogue_sha256','module_sha256','wasm_sha256','approval_sha256','review_sha256','review_html_sha256'];
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
export function preset(){return {model:MODEL,parameters:[30e6,45e6,60e6,12e6,18e6,15e6,.2,.25,.15],initial:Array(6).fill(0),settings:[...SETTINGS],increments:[[.001,-.0002,.0003,.0004,-.0005,.0006],[-.001,.0002,-.0003,-.0004,.0005,-.0006],[0,0,0,0,0,0]]};}
export function validateRequest(input){
 requireThat(input&&input.model===MODEL,'Unsupported model.');
 requireThat(equal(Object.keys(input).sort(),['increments','initial','model','parameters','settings']),'Unexpected request fields.');
 vector(input.parameters,9,'Parameters');vector(input.initial,6,'Initial stress');vector(input.settings,6,'Settings');
 const [E1,E2,E3,G12,G23,G13,a,b,c]=input.parameters;
 requireThat([E1,E2,E3,G12,G23,G13].every(x=>x>=1&&x<=1e12)&&[a,b,c].every(x=>x>=-10&&x<=10),'Parameters outside the declared machine envelope; this is not a physically qualified range.');
 const r21=E2/E1,r31=E3/E1,r32=E3/E2,det=1-a*a*r21-c*c*r31-b*b*r32-2*a*b*c*r31;
 requireThat(1-a*a*r21>0&&1-c*c*r31>0&&1-b*b*r32>0&&det>0,'Compliance must be positive definite: check all coupled Poisson ratios and moduli.');
 requireThat(equal(input.settings,SETTINGS),'This laboratory requires its frozen no-subdivision solver settings.');
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
 vector(response.state,6,'Returned full state');
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

// Strict exported-JSON decoding rejects duplicate object keys and lossy/nonfinite tokens.
export function parseRunJSON(text){
 if(typeof text!=='string')throw Error('Expected JSON text.');const data=JSON.parse(text),stack=[];
 for(const token of text.matchAll(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}[\],:]/g)){
  const value=token[0],frame=stack.at(-1);
  if(value==='{')stack.push({names:new Set(),key:true});else if(value==='[')stack.push(null);else if(value==='}'||value===']')stack.pop();else if(value===','){if(frame)frame.key=true;}else if(value===':'){if(frame)frame.key=false;}
  else if(value[0]==='"'){if(frame?.key){const name=JSON.parse(value);if(frame.names.has(name))throw Error('Duplicate JSON key: '+name);frame.names.add(name);}}
  else{const number=Number(value);if(!Number.isFinite(number))throw Error('JSON number outside finite binary64 range.');if(!/[.eE]/.test(value)&&BigInt(value)!==BigInt(number))throw Error('Integer is not exactly representable in binary64.');}
 }return data;
}
export function verifyReplay(actual,saved){
 const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
 requireThat(JSON.stringify(canonical(actual))===JSON.stringify(canonical(saved)),'Replayed complete document differs from saved output.');return actual;
}
