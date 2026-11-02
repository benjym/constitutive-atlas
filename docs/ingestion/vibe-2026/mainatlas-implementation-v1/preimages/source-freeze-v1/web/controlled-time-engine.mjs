// Generic typed physical-time transport. Constitutive equations live in generated Wasm.
export const PROFILE='controlled-time-ode-v1';
export const canonical=x=>JSON.stringify(x,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
export const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
export function strictJSON(text){
 if(typeof text!=='string')throw Error('Expected JSON text.');
 const data=JSON.parse(text),stack=[];
 for(const token of text.matchAll(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}[\],:]/g)){
  const value=token[0],frame=stack.at(-1);
  if(value==='{')stack.push({names:new Set(),key:true});else if(value==='[')stack.push(null);else if(value==='}'||value===']')stack.pop();else if(value===','){if(frame)frame.key=true;}else if(value===':'){if(frame)frame.key=false;}
  else if(value[0]==='"'){if(frame?.key){const name=JSON.parse(value);if(frame.names.has(name))throw Error('Duplicate JSON key: '+name);frame.names.add(name);}}
  else{const number=Number(value);if(!Number.isFinite(number))throw Error('Nonfinite JSON number.');if(!/[.eE]/.test(value)&&BigInt(value)!==BigInt(number))throw Error('Integer not exactly representable.');}
 }return data;
}
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const keys=(x,expected,label)=>{if(!x||typeof x!=='object'||Array.isArray(x)||canonical(Object.keys(x).sort())!==canonical([...expected].sort()))throw Error('Complete '+label+' fields required.');};
const same=(a,b)=>canonical(a)===canonical(b);
const size=f=>f.size??(f.shape==='sym'?6:1);
export function flatten(values,fields,label='typed data'){
 keys(values,fields.map(f=>f.name),label);const result=[];
 for(const f of fields){const x=values[f.name];if(size(f)===1){if(!finite(x))throw Error('Finite '+f.name+' required.');result.push(x);}else{if(!Array.isArray(x)||x.length!==size(f)||!x.every(finite))throw Error('Complete finite '+f.name+' components required.');result.push(...x);}}
 return result;
}
export function unpack(values,fields){let offset=0;return Object.fromEntries(fields.map(f=>{const n=size(f),v=n===1?values[offset]:values.slice(offset,offset+n);offset+=n;return [f.name,v];}));}
function controlCheck(values,descriptor,rates=false){
 const a=flatten(values,descriptor.controls,'control'+(rates?' rates':' values'));
 if(!rates)for(const f of descriptor.controls){const v=size(f)===1?[values[f.name]]:values[f.name];if(f.constraint==='positive_finite'&&v.some(x=>x<=0)||f.constraint==='nonnegative_finite'&&v.some(x=>x<0))throw Error('Control domain: '+f.name);}
 return a;
}
const settingNames=['absolute_scale_fraction','relative_tolerance','minimum_step_seconds','maximum_step_seconds','maximum_depth','maximum_trials'];
export function validateSettings(s){keys(s,settingNames,'solver settings');const v=settingNames.map(n=>s[n]);if(!v.every(finite)||v.slice(0,4).some(x=>x<=0)||v[2]>v[3]||!Number.isInteger(v[4])||v[4]<1||v[4]>60||!Number.isInteger(v[5])||v[5]<1||v[5]>1000000)throw Error('Invalid physical-time solver settings.');return v;}
export function validateContext(context,descriptor,definition){
 keys(context,['state','time','controls','control_rates','parameters','model_sha256','profile'],'restart context');
 if(context.profile!==PROFILE||context.model_sha256!==descriptor.model_sha256||!finite(context.time))throw Error('Restart model/profile/physical time mismatch.');
 flatten(context.state,descriptor.state,'persistent state');controlCheck(context.controls,descriptor);controlCheck(context.control_rates,descriptor,true);
 keys(context.parameters,descriptor.parameters,'parameters');for(const n of descriptor.parameters){const v=context.parameters[n],p=definition.parameters[n];if(!finite(v)||v<p.min||v>p.max)throw Error('Parameter outside supported bounds: '+n);}
 return structuredClone(context);
}
export function interpolate(start,end,duration,fraction,descriptor){
 if(!finite(duration)||duration<=0||!finite(fraction)||fraction<0||fraction>1)throw Error('Positive seconds and valid stage fraction required.');
 const a=controlCheck(start,descriptor),b=controlCheck(end,descriptor),v=[],r=[];
 for(let i=0;i<a.length;i++){const delta=b[i]-a[i],rate=delta/duration,value=fraction===0?a[i]:fraction===1?b[i]:a[i]+fraction*delta;if(![delta,rate,value].every(finite))throw Error('Unrepresentable field interpolation.');v.push(value);r.push(rate);}
 return [unpack(v,descriptor.controls),unpack(r,descriptor.controls)];
}
export function validateRequest(request,descriptor,definition){
 keys(request,['profile','model','context','settings','segments'],'request');if(request.profile!==PROFILE||request.model!==descriptor.id)throw Error('Wrong physical-time model/profile.');
 const context=validateContext(request.context,descriptor,definition);validateSettings(request.settings);
 if(!Array.isArray(request.segments)||request.segments.length<1||request.segments.length>100)throw Error('Use1–100 explicit segments.');
 let t=context.time,current=context.controls,total=0;const ids=new Set();
 for(const s of request.segments){keys(s,['id','duration','samples','controls_end'],'segment');if(typeof s.id!=='string'||!/^[A-Za-z0-9_-]{1,80}$/.test(s.id)||ids.has(s.id))throw Error('Unique valid segment IDs required.');ids.add(s.id);
  if(!finite(s.duration)||s.duration<=0||!finite(t+s.duration)||t+s.duration<=t||!Number.isInteger(s.samples)||s.samples<1||s.samples>200)throw Error('Positive representable seconds and1–200 output intervals required.');
  interpolate(current,s.controls_end,s.duration,1,descriptor);let previous=t;
  for(let i=1;i<=s.samples;i++){const next=i===s.samples?t+s.duration:t+s.duration*i/s.samples;if(!finite(next)||next<=previous)throw Error('Unrepresentable sample interval.');previous=next;}
  total+=s.samples;t+=s.duration;current=s.controls_end;
 }
 if(total>10000)throw Error('At most10000 output intervals.');return structuredClone(request);
}
export class ControlledTimeEngine{
 constructor(module,catalogue,definition){
  if(catalogue.profile!==PROFILE)throw Error('Dedicated physical-time catalogue required.');this.module=module;this.catalogue=catalogue;this.definition=definition;
  const matches=catalogue.models.map((d,i)=>[d,i]).filter(([d])=>d.id===definition.id);if(matches.length!==1)throw Error('Model missing/duplicated in catalogue.');
  [this.descriptor,this.index]=matches[0];const d=this.descriptor;
  if(module.UTF8ToString(module._controlled_time_model_hash(this.index))!==d.model_sha256||module.UTF8ToString(module._controlled_time_catalogue_hash())!==catalogue.catalogue_sha256)throw Error('Compiled model/catalogue identity mismatch.');
  this.shapes=[d.state.reduce((a,f)=>a+size(f),0),d.parameters.length,d.controls.reduce((a,f)=>a+size(f),0),d.observables.reduce((a,f)=>a+size(f),0),6,4];if(this.shapes.some((n,i)=>module._controlled_time_size(this.index,i)!==n))throw Error('Compiled ABI shape mismatch.');
 }
 call(inputs,lengths,invoke){
  const m=this.module,allocations=[];
  try{const ins=inputs.map(a=>{const p=m._malloc(Math.max(8,a.length*8));if(!p)throw Error('Allocation failed.');allocations.push(p);m.HEAPF64.set(a,p/8);return p;});
   const outs=lengths.map(n=>{const p=m._malloc(Math.max(8,n*8));if(!p)throw Error('Allocation failed.');allocations.push(p);m.HEAPF64.fill(-1234567,p/8,p/8+n);return p;});const status=invoke(ins,outs);
   if(ins.some((p,i)=>!same(Array.from(m.HEAPF64.subarray(p/8,p/8+inputs[i].length)),inputs[i])))throw Error('Compiled call mutated inputs.');
   const result=outs.map((p,i)=>Array.from(m.HEAPF64.subarray(p/8,p/8+lengths[i])));
   if(status!==1){if(result.some(a=>a.some(x=>x!==-1234567)))throw Error('Failed ABI call mutated output.');throw Error('Constitutive domain/refinement rejected; committed history preserved.');}
   if(result.some(a=>!a.every(finite)))throw Error('Nonfinite compiled output.');return result;
  }finally{for(const p of allocations.reverse())m._free(p);}
 }
 evaluate(context,initial=false){
  validateContext(context,this.descriptor,this.definition);const d=this.descriptor,[ns,np,nc,no]=this.shapes,inputs=[flatten(context.state,d.state),d.parameters.map(n=>context.parameters[n]),controlCheck(context.controls,d),controlCheck(context.control_rates,d,true)];
  const [rate,obs,scales]=this.call(inputs,[ns,no,ns],(a,o)=>this.module._controlled_time_evaluate(this.index,a[0],ns,a[1],np,context.time,a[2],nc,a[3],nc,+initial,o[0],ns,o[1],no,o[2],ns));
  return {rate:unpack(rate,d.state),observables:unpack(obs,d.observables),scales};
 }
 advance(parent,duration,end,settings){
  validateContext(parent,this.descriptor,this.definition);const d=this.descriptor,[ns,np,nc,no]=this.shapes,sv=validateSettings(settings);
  if(!finite(parent.time+duration)||parent.time+duration<=parent.time)throw Error('Positive representable time advance required.');
  const [values,rates]=interpolate(parent.controls,end,duration,1,d),left=this.evaluate(parent).observables,right=this.evaluate({...parent,control_rates:rates}).observables;
  const inputs=[flatten(parent.state,d.state),d.parameters.map(n=>parent.parameters[n]),controlCheck(parent.controls,d),controlCheck(parent.control_rates,d,true),controlCheck(parent.controls,d),controlCheck(end,d),sv];
  const [state,time,controls,controlRates,obs,diag]=this.call(inputs,[ns,1,nc,nc,no,4],(a,o)=>this.module._controlled_time_advance(this.index,a[0],ns,a[1],np,parent.time,duration,a[2],nc,a[3],nc,a[4],nc,a[5],nc,a[6],6,o[0],ns,o[1],1,o[2],nc,o[3],nc,o[4],no,o[5],4));
  if(time[0]!==parent.time+duration||!same(controls,flatten(values,d.controls))||!same(controlRates,flatten(rates,d.controls)))throw Error('Compiled time/control endpoint mismatch.');
  const context={...structuredClone(parent),state:unpack(state,d.state),time:time[0],controls:unpack(controls,d.controls),control_rates:unpack(controlRates,d.controls)};validateContext(context,d,this.definition);
  return {context,observables:unpack(obs,d.observables),left_observables:left,right_observables:right,diagnostics:Object.fromEntries(['trials','accepted_half_steps','rejected_trials','final_error'].map((n,i)=>[n,diag[i]]))};
 }
 run(request){
  const spec=validateRequest(request,this.descriptor,this.definition),points=[];let current=structuredClone(spec.context);this.evaluate(current);
  for(const segment of spec.segments){const start=structuredClone(current);
   for(let i=1;i<=segment.samples;i++){const [end]=interpolate(start.controls,segment.controls_end,segment.duration,i/segment.samples,this.descriptor),time=i===segment.samples?start.time+segment.duration:start.time+segment.duration*i/segment.samples;
    const result=this.advance(current,time-current.time,end,spec.settings);
    if(i===1){points.push({segment:segment.id,side:'left',context:structuredClone(current),observables:result.left_observables});points.push({segment:segment.id,side:'right',context:{...structuredClone(current),control_rates:structuredClone(result.context.control_rates)},observables:result.right_observables});}
    points.push({segment:segment.id,side:'end',context:structuredClone(result.context),observables:result.observables,diagnostics:result.diagnostics});current=result.context;
   }
  }return {profile:PROFILE,model:this.descriptor.id,model_sha256:this.descriptor.model_sha256,request:spec,context:current,points};
 }
}
