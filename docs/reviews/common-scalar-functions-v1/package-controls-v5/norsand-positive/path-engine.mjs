// Generic controlled-path flat C ABI bridge; all material equations remain generated.
const finite = x => typeof x === 'number' && Number.isFinite(x);
const equal = (a,b) => a.length===b.length && a.every((x,i)=>Object.is(x,b[i])||x===b[i]);
const count = fields => fields.reduce((n,f)=>n+f.size,0);
function mapping(value,names,label){
 if(!value||Array.isArray(value)||typeof value!=='object'||Object.keys(value).length!==names.length||names.some(n=>!Object.hasOwn(value,n)))throw Error(`Incomplete ${label}.`);
}
function flatten(state,fields){
 mapping(state,fields.map(f=>f.name),'state');
 const values=fields.flatMap(f=>f.size===1?[state[f.name]]:state[f.name]);
 if(fields.some(f=>f.size!==1&&(!Array.isArray(state[f.name])||state[f.name].length!==f.size))||values.length!==count(fields)||!values.every(finite))throw Error('Invalid state components.');
 return values;
}
function unflatten(values,fields){return Object.fromEntries(fields.map(f=>[f.name,f.size===1?values[f.offset]:values.slice(f.offset,f.offset+f.size)]));}
export function validateRequest(request,descriptor){
 if(!request||typeof request!=='object')throw Error('A complete path request is required.');
 const {context,progress,controls_end,samples,settings}=request;
 if(!context||!finite(context.coordinate)||!finite(progress)||progress<0||!finite(context.coordinate+progress)||progress>0&&!(context.coordinate+progress>context.coordinate))throw Error('Invalid path coordinate/progress.');
 if(!Number.isInteger(samples)||samples<1||samples>200)throw Error('Output intervals must be an integer from1 to200.');
 mapping(context.controls,descriptor.controls,'current controls');mapping(controls_end,descriptor.controls,'end controls');
 mapping(context.parameters,descriptor.parameters,'parameters');flatten(context.state,descriptor.state);
 if(![...Object.values(context.controls),...Object.values(controls_end),...Object.values(context.parameters)].every(finite))throw Error('Controls and parameters must be finite numbers.');
 if(progress===0&&descriptor.controls.some(n=>context.controls[n]!==controls_end[n]))throw Error('Zero progress requires unchanged controls.');
 if(!Array.isArray(settings)||settings.length!==6||!settings.every(finite)||settings.slice(0,4).some(x=>x<=0)||settings[2]>settings[3]||!Number.isInteger(settings[4])||settings[4]<1||settings[4]>60||!Number.isInteger(settings[5])||settings[5]<1||settings[5]>1000000)throw Error('Invalid execution settings.');
 return structuredClone(request);
}
export function createPathEngine(module,catalogue){
 if(catalogue.profile!=='controlled-path-ode-v1'||!Array.isArray(catalogue.models))throw Error('Unsupported path catalogue.');
 const shapes=catalogue.models.map((m,index)=>[count(m.state),m.parameters.length,m.controls.length,Object.keys(m.inputs).length,count(m.observables)].map((n,field)=>{
  if(module._path_size(index,field)!==n)throw Error('Wasm/catalogue shape mismatch.');return n;
 }));
 function call(index,context,progress,end,settings){
  const d=catalogue.models[index],shape=shapes[index];if(!d)throw Error('Unknown path model.');
  const [ns,np,nc,,no]=shape,allocations=[];
  const allocate=values=>{const p=module._malloc(Math.max(8,8*values.length));if(!p)throw Error('Wasm allocation failed.');allocations.push(p);module.HEAPF64.set(values,p/8);return p;};
  const read=(p,n)=>Array.from(module.HEAPF64.subarray(p/8,p/8+n));
  try{
   const values=[flatten(context.state,d.state),d.parameters.map(n=>context.parameters[n]),d.controls.map(n=>context.controls[n]),d.controls.map(n=>context.controls[n]),d.controls.map(n=>end[n]),settings];
   const [state,params,current,start,finish,execution]=values.map(allocate),output=allocate(Array(ns).fill(-1234567)),coordinate=allocate([-7654321]),observed=allocate(Array(no).fill(-1234567));
   const status=module._path_advance(index,state,ns,context.coordinate,params,np,current,nc,progress,start,finish,execution,6,output,coordinate,observed,no);
   for(const [i,p]of [state,params,current,start,finish,execution].entries())if(!equal(read(p,values[i].length),values[i]))throw Error('Engine mutated input.');
   const out=read(output,ns),s=read(coordinate,1)[0],obs=read(observed,no);
   if(status!==1){if(!equal(out,Array(ns).fill(-1234567))||s!==-7654321||!equal(obs,Array(no).fill(-1234567)))throw Error('Failed update changed output.');throw Error('Path update rejected; complete initial context preserved.');}
   if(![...out,s,...obs].every(finite)||s!==context.coordinate+progress)throw Error('Invalid engine output.');
   return {context:{state:unflatten(out,d.state),coordinate:s,controls:structuredClone(end),parameters:structuredClone(context.parameters)},observables:unflatten(obs,d.observables)};
  }finally{for(const p of allocations)module._free(p);}
 }
 return {
  run(modelId,request){
   const index=catalogue.models.findIndex(m=>m.id===modelId);if(index<0)throw Error('Unknown path model.');
   const d=catalogue.models[index],input=validateRequest(request,d),points=[];
   let current=structuredClone(input.context);
   const initial=call(index,current,0,current.controls,input.settings);points.push(initial);
   // All trial points remain local; no partial result is returned on failure.
   for(let i=1;i<=input.samples;i++){
    const fraction=i/input.samples,end=Object.fromEntries(d.controls.map(n=>[n,i===input.samples?input.controls_end[n]:input.context.controls[n]+fraction*(input.controls_end[n]-input.context.controls[n])]));
    const endpoint=i===input.samples?input.context.coordinate+input.progress:input.context.coordinate+fraction*input.progress;
    const result=call(index,current,endpoint-current.coordinate,end,input.settings);points.push(result);current=result.context;
   }
   return {model:modelId,request:input,points};
  }
 };
}
