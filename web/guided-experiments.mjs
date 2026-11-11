// Shareable recipes for the ordinary material-point laboratory. Values in
// links use the model definition's units; display conversions are separate.
import {laboratoryExample,persistentState} from './state-contract.mjs';
import {laboratoryStress,verifyScopedLaboratory} from './laboratory-scope.mjs';
import {createLoading} from './loading.mjs';
import {normalizeSettings,settingFields} from './numerics.mjs';
import {laboratoryPresentation,laboratoryPoreView} from './laboratory-view.mjs';
import {modelProfile} from './model-profiles.mjs';

export const guidedPresets={
 clay:{title:'How does compression history change clay response?',link:'Compare clay compression histories',query:'model=modified-cam-clay&protocol=1&target=0.04&steps=200&confinement=100000&ratio=1&state.e=0.7&compare=state.pc&a=100000&b=200000',prompt:'Where do the stress curves begin to separate? Which specimen compresses more at the same axial strain?',explain:'A higher preconsolidation pressure gives Modified Cam Clay a larger initial elastic region. On this path, that delays yielding and changes how much the clay compresses.'},
 elastic:{title:'How does stiffness change the stress response?',link:'Compare two elastic stiffnesses',query:'model=linear-elastic&protocol=1&target=0.01&compare=param.E&a=30000000&b=60000000',prompt:'At the same axial strain, which specimen carries more deviator stress? How does doubling Young’s modulus change the slope?',explain:'With the same Poisson ratio, doubling Young’s modulus doubles the stress change for a given strain on this path.'},
 sand:{title:'How does starting density change sand response?',link:'Compare loose and dense sand',query:'model=hypoplastic-sand-vw96&protocol=1&target=0.04&steps=200&compare=state.e&a=0.8&b=0.6',prompt:'At the same axial strain, which sand carries more deviator stress? Compare the direction and amount of volume change.',explain:'A lower void ratio means a denser packing. The model uses void ratio to change strength and volumetric response during shearing.'},
};
const defaults=normalizeSettings();
const format=value=>Number(value.toPrecision(6)).toString();
const numeric=(s,label)=>{
 if(typeof s!=='string'||!s.trim()||!/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?$/i.test(s.trim())||!Number.isFinite(Number(s)))throw Error(label+' must be a finite number.');
 return Number(s);
};
export function guidedFields(model,protocol){
 const profile=modelProfile(model.id),stress=laboratoryStress(model).scope;
 const fields=new Map([
  ['confinement',{label:'Radial '+stress+' stress',factor:1000,unit:'kPa'}],
  ['ratio',{label:'Axial / radial stress ratio',factor:1,unit:''}],
  ['target',{label:protocol===3?'Deviator stress target':'Axial strain target',factor:protocol===3?1000:.01,unit:protocol===3?'kPa':'%'}],
 ]);
 for(const [key,p] of Object.entries(model.parameters)){
  const guide=profile?.parameters.find(field=>field.name===key);
  const factor=p.unit==='rad'||guide?.unit==='rad'||/\[rad\]/.test(p.label||'')?Math.PI/180:1;
  fields.set('param.'+key,{label:guide?.meaning??key,factor,unit:factor!==1?'°':p.unit==='1'?'':p.unit,min:p.min,max:p.max});
 }
 for(const s of model.state.slice(1).filter(persistentState)){
  fields.set('state.'+s.name,{label:profile?.stateLabels?.[s.name]??s.name,factor:s.unit==='Pa'?1000:1,unit:s.unit==='Pa'?'kPa':s.unit==='1'?'':s.unit,vector:s.shape==='sym'});
 }
 return fields;
}
export function guidedDefaults(model){
 const example=laboratoryExample(model),values=new Map([['confinement',example.initial[1]],['ratio',example.stressRatio],['target',.01]]);
 Object.keys(model.parameters).forEach((name,i)=>values.set('param.'+name,example.parameters[i]));
 let offset=6;
 for(const s of model.state.slice(1)){
  const size=s.shape==='sym'?6:1;
  if(persistentState(s))values.set('state.'+s.name,size===6?example.initial.slice(offset,offset+6):example.initial[offset]);
  offset+=size;
 }
 return values;
}
export function parseGuidedRecipe(hash,catalogue){
 if(hash.length>8000)throw Error('Experiment link is too long.');
 const queryStart=hash.indexOf('?'),q=new URLSearchParams(queryStart<0?'':hash.slice(queryStart+1));
 const seen=new Set();for(const key of q.keys()){if(seen.has(key))throw Error('Duplicate experiment setting: '+key+'.');seen.add(key);}
 if(q.has('v')&&q.get('v')!=='1')throw Error('Unsupported experiment link version.');
 const presetId=hash==='#clay-history'||!q.size?'clay':q.get('preset');
 if(presetId&&(!Object.hasOwn(guidedPresets,presetId)||[...q.keys()].some(k=>k!=='preset'&&k!=='v')))throw Error('Choose a known preset or supply a custom experiment.');
 const preset=presetId?guidedPresets[presetId]:null,params=preset?new URLSearchParams(preset.query):q;
 const model=catalogue.models.find(item=>item.id===params.get('model'));
 if(!model)throw Error('Choose an available Model testing model.');
 const read=(key,fallback)=>params.has(key)?numeric(params.get(key),key):fallback;
 const protocol=read('protocol',1),steps=read('steps',100),cycles=read('cycles',0);
 if(!Number.isInteger(protocol)||protocol<0||protocol>4)throw Error('Protocol must be 0–4.');
 const fields=guidedFields(model,protocol),values=guidedDefaults(model);
 if(protocol===3)values.set('target',20000);
 const compare=params.get('compare'),field=fields.get(compare);
 if(!field||field.vector)throw Error('Choose a scalar input to compare.');
 const settings=normalizeSettings();
 for(const [key,value] of params){
  if(['v','model','protocol','steps','cycles','compare','a','b','title','prompt'].includes(key))continue;
  if(key===compare)throw Error('Set the compared input with a and b only.');
  if(fields.has(key)){
   const parts=value.split(','),vector=fields.get(key).vector;
   if(vector&&parts.length!==6)throw Error(key+' needs six Mandel components.');
   values.set(key,vector?parts.map(p=>numeric(p,key)):numeric(value,key));
  }else if(settingFields.some(f=>'solver.'+f.key===key))settings[key.slice(7)]=numeric(value,key);
  else throw Error('Unknown experiment setting: '+key+'.');
 }
 const a=numeric(params.get('a'),'Reference value (a)'),b=numeric(params.get('b'),'Comparison value (b)');
 const title=params.get('title')?.trim()||'',prompt=params.get('prompt')?.trim()||'';
 if(title.length>100||prompt.length>250)throw Error('Use at most 100 characters for a title and 250 for a prompt.');
 return {model,preset,presetId,title,prompt,protocol,steps,cycles,fields,values,settings:normalizeSettings(settings),compare,field,a,b};
}
export function guidedSpecification(recipe,value){
 const {model,compare,values,protocol,steps,cycles,settings}=recipe;
 const get=key=>key===compare?value:values.get(key),p=get('confinement'),ratio=get('ratio');
 if(p<1||p>1e9||ratio<.01||ratio>10)throw Error('Use radial stress from 0.001 to 1,000,000 kPa and an axial / radial stress ratio from 0.01 to 10.');
 const initial=[p*ratio,p,p,0,0,0],example=laboratoryExample(model).initial;
 let offset=6;
 for(const s of model.state.slice(1)){
  const size=s.shape==='sym'?6:1;
  if(persistentState(s))initial.push(...[get('state.'+s.name)].flat());
  else initial.push(...example.slice(offset,offset+size));
  offset+=size;
 }
 const parameters=Object.keys(model.parameters).map(key=>get('param.'+key));
 Object.values(model.parameters).forEach((p,i)=>{if(!Number.isFinite(parameters[i])||parameters[i]<p.min||parameters[i]>p.max)throw Error(Object.keys(model.parameters)[i]+' is outside the model’s parameter bounds.');});
 const spec={response_contract:'stress-scope-0.1',stress_scope:laboratoryStress(model).scope,model:model.id,parameters,initial,protocol,target:get('target'),steps,cycles,integration_settings:settings};
 spec.loading=createLoading(spec);return spec;
}
export function guidedLink(recipe,compare,a,b){
 const q=new URLSearchParams({v:'1',model:recipe.model.id,protocol:recipe.protocol,steps:recipe.steps,cycles:recipe.cycles,compare,a,b});
 if(recipe.title)q.set('title',recipe.title);
 if(recipe.prompt)q.set('prompt',recipe.prompt);
 for(const [key,value] of recipe.values)if(key!==compare)q.set(key,Array.isArray(value)?value.join(','):value);
 for(const {key} of settingFields)if(recipe.settings[key]!==defaults[key])q.set('solver.'+key,recipe.settings[key]);
 return '#experiment?'+q;
}
export function guideFromRun(model,spec,compare,{ratio=spec.initial[0]/spec.initial[1],title='',prompt=''}={}){
 const {protocol,steps,cycles,integration_settings:settings}=spec,fields=guidedFields(model,protocol),values=guidedDefaults(model);
 if(!fields.has(compare)||fields.get(compare).vector)throw Error('Choose a scalar input to compare.');
 values.set('confinement',spec.initial[1]);values.set('ratio',ratio);values.set('target',spec.target);
 Object.keys(model.parameters).forEach((key,i)=>values.set('param.'+key,spec.parameters[i]));
 let offset=6;
 for(const field of model.state.slice(1)){
  const size=field.shape==='sym'?6:1;
  if(persistentState(field))values.set('state.'+field.name,size===6?spec.initial.slice(offset,offset+6):spec.initial[offset]);
  offset+=size;
 }
 return guidedLink({model,protocol,steps,cycles,values,settings,title,prompt},compare,values.get(compare),values.get(compare));
}
export function setupGuidedExperiments({catalogue,chart,validate}){
 const $=id=>document.getElementById(id),input=$('guided-value'),reset=$('guided-reset'),status=$('guided-status'),charts=$('guided-charts');
 let worker,timer,route='',recipe;
 const stop=()=>{clearTimeout(timer);worker?.terminate();worker=null;};
 const show=(id,value)=>{$(id).hidden=!value;};
 for(const [key,preset] of Object.entries(guidedPresets)){
  const a=document.createElement('a');a.href='#experiment?preset='+key;a.textContent=preset.link;$('guided-presets').append(a);
 }
 function report(message){status.textContent=message;charts.setAttribute('aria-busy','false');}
 function fail(message){show('guided-visuals',false);report(message);}
 function run(){
  stop();
  if(!recipe)return;
  $('guided-values').textContent='';$('guided-link-status').textContent='';$('guided-share').removeAttribute('href');
  show('guided-link-fallback',false);show('guided-visuals',false);show('guided-pore-note',false);
  const {a,field,compare,model,protocol}=recipe,unit=field.unit?' '+field.unit:'';
  const visibleNumber=value=>format(value/field.factor)+unit,showField=field.label;
  $('guided-key-a').textContent='Solid: reference · '+showField+' '+visibleNumber(a);
  $('guided-key-b').textContent='Dashed: comparison';
  const presentation=laboratoryPresentation(model);
  const channels=[
   {id:'guided-stress',yLabel:presentation.axes.stress.yLabel,read:p=>[p.strain[0]*100,p.q_signed/1000]},
   {id:'guided-volume',yLabel:'Volumetric strain (%)',read:p=>[p.strain[0]*100,p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100]},
   {id:'guided-pore',yLabel:'Pore-pressure change (kPa)',pore:true},
  ];
  show('guided-pore-panel',false);
  for(const c of channels)chart(c.id,'Axial strain (%)',c.yLabel,[],[],'Waiting for a response…');
  try{
   const b=numeric(input.value,showField)*field.factor;
   const exactB=input.value===String(recipe.b/field.factor)?recipe.b:b;
   $('guided-key-b').textContent='Dashed: comparison · '+showField+' '+visibleNumber(exactB);
   const requests=[a,exactB].map(value=>{const s=guidedSpecification(recipe,value);validate(s);return s;});
   const share=guidedLink(recipe,compare,a,exactB);
   $('guided-share').href=recipe.preset&&exactB===recipe.b?'#experiment?preset='+recipe.presetId:share;
   const current=new Worker('./worker.js',{type:'module'});worker=current;
   const results=[],send=id=>current.postMessage({id,kind:'laboratory',specification:requests[id],catalogue});
   show('guided-visuals',true);charts.setAttribute('aria-busy','true');status.textContent='Calculating both model responses…';
   current.onmessage=({data})=>{
    if(worker!==current||data.id!==results.length)return;
    try{
     if(data.error)throw Error(data.error);
     verifyScopedLaboratory(data.result,requests[data.id],catalogue);
     results.push(data.result);
     if(results.length===1){send(1);return;}
     stop();
     for(const c of channels){
      const [reference,comparison]=results.map(r=>c.pore?laboratoryPoreView(r,model,protocol).points:r.points.map(c.read));
      if(c.pore){
       const available=reference.length||comparison.length;show('guided-pore-panel',available);show('guided-pore-note',available);
       if(!available)continue;
      }
      chart(c.id,'Axial strain (%)',c.yLabel,reference,[],undefined,{comparison,stopped:!results[0].ok,comparisonStopped:!results[1].ok});
     }
     const end=results.map(result=>result.points.at(-1));
     if(end.every(Boolean))$('guided-values').textContent=end.map((p,i)=>(i?'Comparison':'Reference')+' at '+format(p.strain[0]*100)+'% axial strain: '+format(p.q_signed/1000)+' kPa deviator stress, '+format(p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100)+'% volumetric strain.').join(' ');
     const stopped=results.flatMap((result,i)=>result.ok?[]:[(i?'Comparison':'Reference')+' stopped: '+result.message]);
     report(stopped.join(' ')||'Both curves updated.');
    }catch(error){stop();fail(error.message);}
   };
   current.onerror=()=>{if(worker===current){stop();fail('The experiment could not run. Reset to retry.');}};
   timer=setTimeout(()=>{stop();fail('The experiment took too long. Try fewer increments or reset.');},15000);
   send(0);
  }catch(error){stop();fail(error.message);}
 }
 input.onchange=run;
 reset.onclick=()=>{if(recipe){input.value=recipe.b/recipe.field.factor;run();}};
 $('guided-share').onclick=async event=>{
  const link=$('guided-share');if(!link.hasAttribute('href'))return;
  event.preventDefault();const url=link.href;
  try{await navigator.clipboard.writeText(url);if(link.href===url)$('guided-link-status').textContent='Link copied.';}
  catch{
   if(link.href!==url)return;
   const fallback=$('guided-url');fallback.value=url;show('guided-link-fallback',true);fallback.select();
   $('guided-link-status').textContent='Copy the selected URL to share this setup.';
  }
 };
 return {
  route(hash,focus){
   if(route===hash)return;
   route=hash;stop();recipe=null;
   if(!hash)return;
   $('guided-link-status').textContent='';
   try{
    recipe=parseGuidedRecipe(hash,catalogue);
    const {model,preset,protocol,compare,field,values,cycles,steps}=recipe,view=laboratoryPresentation(model);
    const title=modelProfile(model.id)?.title??model.name;
    $('guided-title').textContent=recipe.title||preset?.title||'Compare '+field.label+' in '+title;
    const undrained=protocol===2||protocol===3;
    const prompt=undrained?'Volume stays fixed in this test. Compare deviator stress'+(view.scope==='effective'?' and pore-pressure change':'')+' at the same axial strain.':'Compare the responses at the same axial strain. Look for changes in stress and volume as you vary the chosen input.';
    $('guided-prompt').textContent=(recipe.prompt||preset?.prompt||prompt)+(undrained?'':' Positive volumetric strain means compression.');
    show('guided-explain',!!preset?.explain);$('guided-explanation').textContent=preset?.explain??'';
    $('guided-model').textContent=title;$('guided-model').href='#catalogue/'+encodeURIComponent(model.id);
    $('guided-lab').href='#laboratory?model='+encodeURIComponent(model.id);
    $('guided-setup').textContent=view.protocols[protocol]+' · '+(cycles?cycles+' loading cycle'+(cycles===1?'':'s'):'monotonic loading')+'. Both runs share the same setup except for '+field.label.toLowerCase()+'.';
    const fixed=$('guided-fixed');fixed.replaceChildren();
    for(const [key,value] of values){
     if(key===compare)continue;
     const f=recipe.fields.get(key),item=document.createElement('li');
     item.textContent=f.label+': '+(Array.isArray(value)?value.map(format).join(', '):format(value/f.factor))+(f.unit?' '+f.unit:'');fixed.append(item);
    }
    const increments=document.createElement('li');increments.textContent='Increments: '+steps;fixed.prepend(increments);
    for(const {key,label} of settingFields)if(recipe.settings[key]!==defaults[key]){
     const item=document.createElement('li');item.textContent=label+': '+recipe.settings[key];fixed.append(item);
    }
    $('guided-label').textContent='Comparison '+field.label+(field.unit?' ('+field.unit+')':'');
    input.value=recipe.b/field.factor;input.min=field.min===undefined?'':field.min/field.factor;input.max=field.max===undefined?'':field.max/field.factor;
    show('guided-workspace',true);run();
   }catch(error){$('guided-title').textContent='Guided experiment';$('guided-lab').href='#laboratory';show('guided-workspace',false);fail(error.message);}
   if(focus)$('guided-title').focus({preventScroll:true});
  }
 };
}
