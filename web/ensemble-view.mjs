import {defaultConfigurations,makeStudy,exportStudy,importStudy,availableModels,modelExclusion,variedParameters,historyFields,validateExperiment} from './ensemble.mjs';
import {loadEnsembleCatalogue,fetchEnsembleTest,filterTests,replayGap} from './ensemble-experiments.mjs';
import {createEnsemblePlot} from './ensemble-plots.mjs';
import {EnsembleQueue,ensembleConcurrency} from './ensemble-queue.mjs';
import {createRecordedDocument} from './recorded-document.mjs';
const root=document.getElementById('ensemble');
const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
const outcomeIcons={completed:['✓','Completed'],stopped:['!','Stopped early'],rejected:['×','Input rejected'],error:['×','Run failed'],timeout:['×','Timed out'],cancelled:['–','Cancelled'],queued:['·','Waiting'],running:['·','In progress']};
const palette=['#256d64','#a55635','#6258a4','#ac7822','#286fa8','#a23f72','#62752a','#795c40','#447b85','#72517b','#b04b47','#6d6f38','#375595'];
const compactNames={'linear-elastic':'Linear elasticity','drucker-prager':'Drucker–Prager','modified-cam-clay':'Modified Cam Clay','barodesy-clay-2017':'Barodesy clay (2017)','barodesy-sand':'Barodesy sand (2015)','duncan-chang-1970-endpoint-average':'Duncan–Chang (1970)','hypoplastic-clay-2005':'Hypoplastic clay (2005)','hypoplastic-clay-2013':'Hypoplastic clay (2013)','hypoplastic-sand-igs97':'Hypoplastic sand + IGS (1997)','hypoplastic-sand-vw96':'Hypoplastic sand (1996)','mohr-coulomb':'Mohr–Coulomb','original-cam-clay-sw-electronic-log-recovery-v1':'Original Cam Clay','research-hp-extracted-asbs-gis-2024-v03':'ASBS + GIS (2024)'};
let modelIds=[],names={},colors=[];
const $=id=>document.getElementById(id);
function download(name,value){const a=node('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
function workerExecutor(catalogue){
 const slots=new Set();let nextId=0;
 const remove=slot=>{slot.worker.terminate();slots.delete(slot);};
 const close=()=>{for(const slot of slots)remove(slot);};
 const execute=(job,signal)=>new Promise((resolve,reject)=>{
  if(signal.aborted){reject(Error('Cancelled.'));return;}
  let slot=[...slots].find(s=>!s.busy);
  if(!slot){slot={worker:new Worker(new URL('./ensemble-worker.mjs',import.meta.url),{type:'module'}),busy:false};slots.add(slot);}
  slot.busy=true;const {worker}=slot,id=++nextId;let settled=false;
  const finish=(error,result)=>{
   if(settled)return;settled=true;signal.removeEventListener('abort',abort);worker.onmessage=worker.onerror=null;
   if(error){remove(slot);reject(error);}else{slot.busy=false;resolve(result);}
  };
  const abort=()=>finish(Error('Cancelled.'));signal.addEventListener('abort',abort,{once:true});
  worker.onmessage=({data})=>{if(data.id!==id)return;try{if(data.error)throw Error(data.error);createRecordedDocument(job.specification,data.result,catalogue);finish(null,data.result);}catch(e){finish(e);}};
  worker.onerror=event=>finish(Error(event.message||'Worker failed.'));
  try{worker.postMessage({id,specification:job.specification,catalogue});}catch(error){finish(error);}
 });
 return {execute,close};
}
async function setup(){
 const [entries,catalogue]=await Promise.all([loadEnsembleCatalogue(),fetch('./models.json').then(r=>{if(!r.ok)throw Error('Model catalogue unavailable.');return r.json();})]);
 let entry=entries.find(e=>e.id==='OPARA-TXCD-100')||entries[0];
 if(!entry)throw Error('No tests available.');
 let record=await fetchEnsembleTest(entry),testGap='',loading=false,testSequence=0,importSequence=0;
 if(entry.replay)validateExperiment(record);else testGap=replayGap(record)||'No verified replay loading asset is available for this record.';
 modelIds=availableModels(catalogue).map(m=>m.id);names=Object.fromEntries(catalogue.models.map(m=>[m.id,m.name]));colors=modelIds.map((_,i)=>palette[i%palette.length]);
 const styles=Object.fromEntries(modelIds.map((id,i)=>[id,{name:names[id],color:colors[i]}]));
 let viewRevision=0;
 let study=null,selected=null,stale=false,revision=0,pendingRun=null,activeRun=null;
 const hidden=new Set(),editors=new Map();
 root.replaceChildren();
 const title=node('h1','Ensemble explorer','ensemble-sr-only');root.append(title);
 const testControls=node('section',undefined,'model-card ensemble-test-controls');
 const searchLabel=node('label','Find a test'),search=node('input');search.type='search';search.id='ensemble-test-search';search.placeholder='Material or test ID';searchLabel.append(search);
 const protocolLabel=node('label','Test type'),protocol=node('select');protocol.id='ensemble-test-protocol';protocol.append(new Option('All test types',''));for(const value of [...new Set(entries.map(e=>e.protocol))].sort())protocol.append(new Option(value.replaceAll('-',' '),value));protocolLabel.append(protocol);
 const availabilityLabel=node('label','Availability'),availability=node('select');availability.id='ensemble-test-availability';for(const [text,value]of [['All records',''],['Ensemble replay','replay'],['Measurements only','source']])availability.append(new Option(text,value));availabilityLabel.append(availability);
 const testLabel=node('label','Experimental test'),testSelect=node('select');testSelect.id='ensemble-test';testLabel.append(testSelect);const testCount=node('p',undefined,'control-hint');testCount.id='ensemble-test-count';testControls.append(searchLabel,protocolLabel,availabilityLabel,testLabel);root.append(testControls);
 const help=node('button','?','ensemble-help');help.type='button';help.id='ensemble-test-help';help.setAttribute('aria-label','Test information and assumptions');help.setAttribute('aria-haspopup','dialog');help.setAttribute('aria-controls','ensemble-test-info');
 const info=node('dialog',undefined,'ensemble-test-info');info.id='ensemble-test-info';info.setAttribute('aria-labelledby','ensemble-test-info-title');const infoTitle=node('h2','Test information');infoTitle.id='ensemble-test-info-title';const closeInfo=node('button','Close','ensemble-info-close');closeInfo.type='button';const infoHeader=node('div',undefined,'ensemble-info-header');infoHeader.append(infoTitle,closeInfo);info.append(infoHeader,testCount);root.append(info);help.onclick=()=>info.showModal();closeInfo.onclick=()=>info.close();info.addEventListener('click',event=>{if(event.target===info){const box=info.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)info.close();}});
 function filterOptions(){const filtered=filterTests(entries,{search:search.value,protocol:protocol.value,availability:availability.value});testSelect.replaceChildren();if(!filtered.some(e=>e.id===entry.id))testSelect.append(new Option('Current: '+entry.id,entry.id));for(const e of filtered)testSelect.append(new Option(e.id+' · '+e.material+' · '+(e.replay?'ensemble':'measurements'),e.id));testSelect.value=entry.id;testCount.textContent=filtered.length+' matching / '+entries.length+' records · '+entries.filter(e=>e.replay).length+' ready for ensemble replay';}
 search.oninput=protocol.onchange=availability.onchange=filterOptions;
 const experiment=node('section'),testHeading=node('h2'),testDescription=node('p'),source=node('a','Source experiment ↗'),gapNote=node('p',undefined,'ensemble-gap');gapNote.id='ensemble-test-gap';gapNote.setAttribute('role','status');source.target='_blank';source.rel='noopener noreferrer';experiment.append(testHeading,testDescription,source,gapNote);
 const loadingNote=node('p'),warnings=node('div');
 const disclosure=node('details');disclosure.append(node('summary','Loading, preparation and comparison assumptions'),loadingNote,node('p','All baselines are illustrative and uncalibrated for the selected specimen. Measured effective stress and void ratio initialize replay; other history uses the displayed unmeasured model assumptions. No consolidation history or physical-time evolution is inferred. Unsupported source channels are available for inspection without inventing a loading contract.'),warnings);experiment.append(disclosure);info.append(experiment);
 const sourceControls=node('div',undefined,'ensemble-source-controls'),sourceX=node('select'),sourceY=node('select');sourceX.id='ensemble-source-x';sourceY.id='ensemble-source-y';for(const [text,input]of [['X channel',sourceX],['Y channel',sourceY]]){const label=node('label',text);label.append(input);sourceControls.append(label);}experiment.append(sourceControls);
 const exclusions=node('details');exclusions.append(node('summary','Model availability for this test'));exclusions.append(node('p',modelIds.length+' compiled models support effective-stress strain-path replay. Other dedicated timed, total-stress and restricted-path engines require different loading or execution contracts.'));for(const model of catalogue.models){const reason=modelExclusion(model);if(reason)exclusions.append(node('p',model.name+': '+reason));}experiment.append(exclusions);
 const layout=node('div',undefined,'ensemble-layout'),controls=node('form',undefined,'controls ensemble-controls'),results=node('div',undefined,'results-column');controls.id='ensemble-controls';controls.append(node('h2','Models & parameter variations'),node('p','SI units throughout. Each model runs its baseline, then changes one parameter at a time. Blank variation lists run only the baseline for that parameter.','control-hint'));
 const fields=node('div');controls.append(fields);
 let controlId=0;
 function numeric(label,value,readonly=false,bounds={}){
  const wrapper=node('div',undefined,'ensemble-numeric'),caption=node('label',label),input=node('input'),display=node('button',String(value),'ensemble-value');
  input.type='number';input.step='any';input.required=true;input.value=value;input.readOnly=readonly;input.id='ensemble-value-'+(++controlId);caption.htmlFor=input.id;
  if(bounds.min!==undefined)input.min=bounds.min;if(bounds.max!==undefined)input.max=bounds.max;
  display.type='button';display.title='Enter an exact value';display.setAttribute('aria-label',label+': enter exact value');display.setAttribute('aria-expanded','false');display.setAttribute('aria-controls',input.id);input.hidden=true;
  const min=bounds.min??Math.min(0,value*3),max=bounds.max??Math.max(1,Math.abs(value)*3);
  const slider=node('input');slider.type='range';slider.min=0;slider.max=1000;slider.step=1;slider.setAttribute('aria-label',label+' slider');
  const logarithmic=min>0&&max/min>=1000;
  function sync(){const v=Number(input.value);display.textContent=input.value||'Enter value';slider.value=1000*(logarithmic?Math.log(Math.max(min,v)/min)/Math.log(max/min):(v-min)/(max-min));slider.setAttribute('aria-valuetext',input.value);}
  slider.oninput=()=>{const t=Number(slider.value)/1000;input.value=Number((logarithmic?min*Math.pow(max/min,t):min+(max-min)*t).toPrecision(6));sync();};
  input.oninput=sync;
  function collapse(){input.hidden=true;display.hidden=false;display.setAttribute('aria-expanded','false');sync();}
  display.onclick=()=>{display.hidden=true;input.hidden=false;display.setAttribute('aria-expanded','true');input.focus();input.select();};
  input.onblur=collapse;input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();collapse();display.focus();}};
  wrapper.append(caption,display,input);if(!readonly&&max>min)wrapper.append(slider);else display.disabled=true;
  input.setEnabled=enabled=>{input.disabled=slider.disabled=display.disabled=!enabled||readonly;};sync();
  return {wrapper,input};
 }
 function outcomeSlot(className){return {element:node('div',undefined,'ensemble-outcome-slot '+className),badges:new Map()};}
 function updateOutcomes(slot,jobs){
  const ids=new Set(jobs.map(job=>job.id));
  for(const [id,badge]of slot.badges)if(!ids.has(id)){badge.wrapper.remove();slot.badges.delete(id);}
  for(const [index,job]of jobs.entries()){
   let badge=slot.badges.get(job.id);
   if(!badge){
    const wrapper=node('span',undefined,'ensemble-outcome'),button=node('button'),tooltip=node('span',undefined,'ensemble-outcome-tip');
    tooltip.id='ensemble-outcome-'+(++controlId);tooltip.setAttribute('role','tooltip');
    button.type='button';button.setAttribute('aria-label',names[job.model]+' · '+job.label);button.setAttribute('aria-describedby',tooltip.id);button.setAttribute('aria-controls','ensemble-run-detail');
    button.onclick=()=>{selected=job.id;render();};
    wrapper.onkeydown=event=>{if(event.key==='Escape'&&!wrapper.hasAttribute('data-dismissed')){event.stopPropagation();wrapper.setAttribute('data-dismissed','');}};
    const restore=()=>wrapper.removeAttribute('data-dismissed');button.onblur=restore;wrapper.onpointerleave=restore;
    wrapper.append(button,tooltip);badge={wrapper,button,tooltip};slot.badges.set(job.id,badge);
   }
   const [symbol,label]=outcomeIcons[job.status];
   if(badge.button.textContent!==symbol)badge.button.textContent=symbol;
   const tip=job.label+' · '+(stale?'Previous result: ':'')+label;
   if(badge.tooltip.textContent!==tip)badge.tooltip.textContent=tip;
   badge.button.dataset.status=job.status;badge.button.setAttribute('aria-pressed',String(job.id===selected));
   if(slot.element.children[index]!==badge.wrapper)slot.element.insertBefore(badge.wrapper,slot.element.children[index]||null);
  }
 }
 function populate(configurations){
  fields.replaceChildren();editors.clear();
  for(const config of configurations){
   const model=catalogue.models.find(m=>m.id===config.model),box=node('details',undefined,'ensemble-model'),row=node('div',undefined,'ensemble-model-row'),baseline=outcomeSlot('ensemble-baseline-outcome');box.open=config.model==='linear-elastic';
   const heading=node('summary',names[config.model]);heading.style.borderLeftColor=colors[modelIds.indexOf(config.model)];box.append(heading);
   const enabledLabel=node('label',undefined,'ensemble-check'),enabled=node('input');enabled.type='checkbox';enabled.checked=config.enabled;enabled.disabled=!model;enabledLabel.append(enabled,node('span',model?'Include this model':'Unavailable in this engine'));box.append(enabledLabel);
   const parameters={},variations={},history={},variationOutcomes={};
   if(model){
    const grid=node('div',undefined,'ensemble-fields');
    for(const [key,f]of Object.entries(model.parameters)){const item=numeric(key+' ('+f.unit+')',config.parameters[key],key==='p_ref',f);item.input.dataset.parameter=key;parameters[key]=item.input;grid.append(item.wrapper);}box.append(grid);
    for(const field of historyFields(model)){const item=numeric('Assumed initial '+field.key+' ('+field.unit+') · not measured',config.history[field.key]);history[field.key]=item.input;box.append(item.wrapper);}
    for(const key of variedParameters(model)){
     const field=node('div',undefined,'ensemble-variation'),header=node('div',undefined,'ensemble-variation-heading'),label=node('label',key+' variation values · comma separated'),input=node('input');
     input.type='text';input.id='ensemble-variation-'+(++controlId);input.value=config.variations[key].join(', ');input.dataset.variation=key;label.htmlFor=input.id;variations[key]=input;
     const slot=variationOutcomes[key]=outcomeSlot('ensemble-variation-outcomes');header.append(label,slot.element);field.append(header,input);box.append(field);
    }
    const definition=node('a','Exact model definition ↗');definition.href='./models/'+config.model+'.json';definition.target='_blank';definition.rel='noopener';box.append(definition);
   }
   row.append(box,baseline.element);fields.append(row);editors.set(config.model,{enabled,parameters,variations,history,baseline,variationOutcomes,original:config});
  }
 }
 const count=node('p','');count.id='ensemble-count';const actions=node('div',undefined,'ensemble-actions'),cancel=node('button','Cancel'),save=node('button','Export ensemble'),importButton=node('button','Import & replay'),file=node('input');
 cancel.type=save.type=importButton.type='button';cancel.hidden=true;cancel.id='ensemble-cancel';save.disabled=true;save.id='ensemble-export';file.type='file';file.accept='.json,application/json';file.hidden=true;file.id='ensemble-file';importButton.id='ensemble-import';const reset=node('button','Reset all models');reset.type='button';reset.id='ensemble-reset';actions.append(cancel,save,importButton,reset,file);
 const loadSaved=node('button','Import');loadSaved.type='button';loadSaved.id='ensemble-load-saved';loadSaved.onclick=()=>file.click();loadSaved.title='Import saved ensemble';testControls.append(loadSaved,help);
 const progress=node('progress');progress.id='ensemble-progress';progress.hidden=true;progress.setAttribute('aria-label','Case progress');controls.append(progress);
 const status=node('p','Parameters update automatically.');status.id='ensemble-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');controls.append(count,actions,status);controls.insertBefore(count,fields);controls.insertBefore(actions,fields);controls.insertBefore(status,fields);controls.insertBefore(progress,fields);
 const legend=node('div',undefined,'ensemble-legend');legend.setAttribute('role','group');legend.setAttribute('aria-label','Visible model curves');legend.append(node('span','··· Measurements','ensemble-measurements'));
 for(const id of modelIds){const label=node('label',undefined,'ensemble-check'),input=node('input');input.type='checkbox';input.checked=true;label.style.color=colors[modelIds.indexOf(id)];input.setAttribute('aria-label',names[id]);label.title=names[id];label.append(input,node('span',compactNames[id]||names[id].split(' — ')[0]));input.onchange=()=>{input.checked?hidden.delete(id):hidden.add(id);render();};legend.append(label);}
 const comparisonContext=node('aside',undefined,'ensemble-comparison-context'),comparisonText=node('p'),stopKey=node('p','× marks where a model run stopped. No model response is shown beyond that point.');
 comparisonContext.append(node('strong','How to read this comparison'),comparisonText,stopKey);
 const plotHelp=node('p',undefined,'control-hint');results.append(comparisonContext,legend,plotHelp);
 const charts={},panels={};for(const channel of ['stress','volume','path','pore','source']){
  const panel=node('section',undefined,'chart-panel'),heading=node('h2',({stress:'Deviator stress',volume:'Volumetric strain · compression positive',path:'Effective stress path',pore:'Pore-pressure change',source:'Source measurements'})[channel]),chart=node('div',undefined,'ensemble-plot'),error=node('p',undefined,'control-hint');
  heading.id='ensemble-'+channel+'-title';chart.id='ensemble-'+channel;chart.setAttribute('role','region');chart.setAttribute('aria-labelledby',heading.id);error.setAttribute('role','status');
  panel.append(heading,chart,error);results.append(panel);panels[channel]=panel;
  charts[channel]=createEnsemblePlot(chart,{channel,onSelect:id=>{selected=id;render();},onError:failure=>{error.textContent=failure.message;}});
 }
 const detail=node('section',undefined,'experiment-card');detail.id='ensemble-run-detail';detail.append(node('h2','Selected run'));const detailText=node('p','Select a run to inspect its inputs.'),raw=node('pre'),rawDetails=node('details');raw.id='ensemble-selected';rawDetails.append(node('summary','Exact request, outcome and retained response'),raw);const single=node('button','Export selected recorded replay');single.type='button';single.disabled=true;single.id='ensemble-single-export';detail.append(detailText,single,rawDetails);results.append(detail);layout.append(controls,results);root.append(layout);
 const executor=workerExecutor(catalogue),queue=new EnsembleQueue(executor.execute,()=>render(),30000,ensembleConcurrency(navigator.hardwareConcurrency));
 function read(){return [...editors].map(([id,e])=>{if(!e.enabled.checked)return {...e.original,enabled:false};return {model:id,enabled:e.enabled.checked,parameters:Object.fromEntries(Object.entries(e.parameters).map(([k,v])=>[k,v.value.trim()===''?NaN:Number(v.value)])),history:Object.fromEntries(Object.entries(e.history).map(([k,v])=>[k,v.value.trim()===''?NaN:Number(v.value)])),variations:Object.fromEntries(Object.entries(e.variations).map(([k,v])=>[k,v.value.trim()===''?[]:v.value.split(',').map(x=>x.trim()===''?NaN:Number(x.trim()))]))};});}
 function updateTestInfo(){
  disclosure.hidden=false;testHeading.textContent=entry.id+' · '+entry.protocol.replaceAll('-',' ');
  testDescription.textContent=record.material+' · '+record.rows.length.toLocaleString()+' observations'+(record.initial?.effective_stress?' · initial radial effective stress '+(record.initial.effective_stress[1]/1000).toFixed(2)+' kPa · e₀ = '+record.initial.void_ratio:'');
  source.href=record.provenance?.source_url||record.provenance?.license_url||'#';source.hidden=!record.provenance?.source_url;
  gapNote.textContent=testGap?'Measurements only. '+testGap:'Ensemble replay · all observations retained in acquisition order.';
  warnings.replaceChildren(...(record.warnings||[]).map(w=>node('p',w)),node('p',record.provenance?.attribution||''));
  const native=record.kind&&record.kind!=='experiment';sourceControls.hidden=!native;
  if(native)for(const [input,key]of [[sourceX,'x'],[sourceY,'y']]){input.replaceChildren();for(const c of record.columns)input.append(new Option(c.name+' ('+c.unit+')',c.key));input.value=record.source_plot[key];}
  plotHelp.textContent=testGap?'Hover for source values. Use the toolbar to zoom, pan, reset axes or download an image.':'Solid: baseline · dashed: parameter variation · thicker: selected run. Hover for values or click a model curve to select its run. Use the toolbar to zoom, pan, reset axes or download an image.';
  exclusions.hidden=!!testGap;controls.hidden=!!testGap;legend.hidden=!!testGap;detail.hidden=!!testGap;
  for(const [channel,panel]of Object.entries(panels))panel.hidden=native?channel!=='source':channel==='source'||channel==='pore'&&record.protocol!=='undrained-triaxial'||channel==='path'&&!record.rows.some(r=>Number.isFinite(r.p)||Number.isFinite(r.radial_effective_stress))||channel==='volume'&&!record.rows.some(r=>Number.isFinite(r.volumetric_strain));
 }
 function describeLoading(){loadingNote.textContent=testGap?testGap:record.protocol==='undrained-triaxial'?'Idealized undrained replay: impose acquired axial strain, zero volumetric strain and equal lateral effective stresses. Measured effective radial stress is an output comparison, not imposed loading. Pore-pressure change is inferred from measured cell-pressure change minus predicted lateral effective-stress change; saturated incompressible response is assumed.':'Acquired axial strain and measured membrane-corrected radial effective stress are imposed. This is a conditional comparison: the membrane correction uses measured specimen volume.';}
 function refreshCount(){if(loading||testGap)return;for(const e of editors.values())for(const input of [...Object.values(e.parameters),...Object.values(e.history),...Object.values(e.variations)])input.setEnabled?input.setEnabled(e.enabled.checked):input.disabled=!e.enabled.checked;try{const preview=makeStudy(record,catalogue,read());count.textContent=preview.model_definitions.length+' models · '+preview.jobs.length+' runs · '+preview.jobs.filter(j=>j.status==='rejected').length+' rejected by input checks';}catch(e){count.textContent=e.message;}}
 function render(){
  if(loading)return;
  describeLoading();
  cancel.hidden=!queue.running&&pendingRun===null;save.disabled=!study||stale||queue.running;importButton.disabled=queue.running;
  if(!study)status.textContent=testGap?'Measurements only · no simulation requested.':'Ready to run the selected test.';
  const jobs=study?.jobs||[];
  comparisonContext.hidden=!!testGap;
  if(!testGap){
   const applied=record.protocol==='undrained-triaxial'?'Models follow the measured axial strain at fixed specimen volume. Pore-pressure change is inferred using measured cell pressure.':'Models follow the measured axial strain and recorded radial effective stress.';
   comparisonText.textContent='The dotted line is measured; coloured lines are model responses. '+applied+' Starting stress and void ratio come from the test. Atlas starts with example parameters and assumed specimen history; it does not fit parameters to this test.';
   stopKey.hidden=!jobs.some(job=>job.status==='stopped'&&job.result?.points?.length&&!hidden.has(job.model));
  }
  if(location.hash==='#ensemble')for(const [channel,chart]of Object.entries(charts))if(!panels[channel].hidden)chart.update(record,jobs.filter(j=>!hidden.has(j.model)),selected,styles,viewRevision);
  progress.hidden=!study&&pendingRun===null;
  if(pendingRun!==null){progress.removeAttribute('value');status.textContent='Updating cases…';}
  else if(study){
   const finished=jobs.filter(job=>!['queued','running'].includes(job.status)).length,attention=jobs.filter(job=>['rejected','error','timeout','stopped'].includes(job.status)).length;
   progress.max=jobs.length;progress.value=finished;
   status.textContent=stale?'Inputs changed · displayed results are stale.':queue.running?'Updating cases · '+finished+' of '+jobs.length:finished+' cases finished'+(attention?' · '+attention+' need attention':'');
  }
  const byModel=new Map();
  for(const job of jobs){if(!byModel.has(job.model))byModel.set(job.model,[]);byModel.get(job.model).push(job);}
  for(const [model,editor]of editors){
   const cases=editor.enabled.checked?byModel.get(model)||[]:[];
   updateOutcomes(editor.baseline,cases.filter(job=>!job.change));
   for(const [key,slot]of Object.entries(editor.variationOutcomes)){
    const byValue=new Map(cases.filter(job=>job.change?.parameter===key).map(job=>[job.change.value,job]));
    const values=new Set(editor.variations[key].value.split(',').filter(value=>value.trim()!=='').map(Number));
    updateOutcomes(slot,[...values].map(value=>byValue.get(value)).filter(Boolean));
   }
  }
  const job=jobs.find(j=>j.id===selected);single.disabled=!job?.result||stale||queue.running;
  if(job){detailText.textContent=names[job.model]+' · '+job.label+' · '+job.status+(job.message?' · '+job.message:'');raw.textContent=JSON.stringify({parameters:job.parameters,initial_history_assumptions:job.history,specification:job.specification,status:job.status,message:job.message,result:job.result},null,2);}
 }
 function clearPending(){clearTimeout(pendingRun);pendingRun=null;}
 async function start(prepared){
  if(loading||testGap)return;
  const id=++revision;
  clearPending();
  let failure=null;
  try{
   const next=prepared||makeStudy(record,catalogue,read());
   ++viewRevision;study=prepared?next:queue.reconcile(next);stale=false;selected=study.jobs.some(job=>job.id===selected)?selected:study.jobs[0].id;
   if(queue.running){render();return;}
   activeRun=queue.run(study);await activeRun;
  }catch(e){failure='Cannot update: '+e.message;}
  finally{if(!queue.running){activeRun=null;executor.close();}render();if(failure&&id===revision)status.textContent=failure;}
 }
 function schedule(delay=350){
  if(loading||testGap)return;
  ++revision;clearPending();stale=!!study;
  pendingRun=setTimeout(()=>{pendingRun=null;void start();},delay);
  refreshCount();render();
 }
 controls.onsubmit=event=>{event.preventDefault();schedule(0);};
 controls.addEventListener('input',event=>{if(event.target!==file)schedule();});
 reset.onclick=()=>{populate(defaultConfigurations(catalogue));schedule(0);};
 cancel.onclick=()=>{++revision;clearPending();queue.cancel();render();};
 save.onclick=()=>{try{download(record.id+'-ensemble.json',exportStudy(study,catalogue,record));}catch(e){status.textContent=e.message;}};
 single.onclick=()=>{const job=study.jobs.find(j=>j.id===selected);try{download(job.model+'-'+record.id+'-recorded.json',createRecordedDocument(job.specification,job.result,catalogue));}catch(e){status.textContent=e.message;}};
 async function selectTest(id,{run=true}={}){
  const requested=++testSequence;const next=entries.find(e=>e.id===id);if(!next)throw Error('Test is absent from this catalogue.');
  ++revision;clearPending();queue.cancel();loading=true;study=null;selected=null;stale=false;save.disabled=true;single.disabled=true;raw.textContent='';detailText.textContent='Select a run to inspect its inputs.';testHeading.textContent=id;testDescription.textContent='';source.hidden=true;disclosure.hidden=true;gapNote.textContent='Loading '+id+'…';controls.hidden=true;detail.hidden=legend.hidden=comparisonContext.hidden=true;sourceControls.hidden=true;for(const panel of Object.values(panels))panel.hidden=true;
  try{
   const loaded=await fetchEnsembleTest(next);if(requested!==testSequence)return false;
   if(next.replay)validateExperiment(loaded);
   await activeRun;if(requested!==testSequence)return false;
   entry=next;record=loaded;testGap=entry.replay?'':replayGap(record)||'No verified replay loading asset is available for this record.';loading=false;++viewRevision;
   filterOptions();updateTestInfo();refreshCount();render();if(run&&!testGap)schedule(0);return true;
  }catch(error){if(requested===testSequence){loading=true;gapNote.textContent='Unable to load '+id+': '+error.message;testSelect.value=id;}return false;}
 }
 testSelect.onchange=()=>{void selectTest(testSelect.value);};
 sourceX.onchange=sourceY.onchange=()=>{record={...record,source_plot:{x:sourceX.value,y:sourceY.value}};++viewRevision;render();};
 importButton.onclick=()=>file.click();file.onchange=async()=>{const importId=++importSequence;try{
  const item=file.files[0];if(!item)return;if(item.size>100*1024*1024)throw Error('Import exceeds 100 MB.');
  const readingSelection=testSequence,text=await item.text();if(importId!==importSequence||readingSelection!==testSequence)return;const doc=JSON.parse(text),id=doc.study?.experiment?.id;
  const selectedTest=await selectTest(id,{run:false});if(!selectedTest)return;const selection=testSequence;
  const prepared=importStudy(text,catalogue,record);if(selection!==testSequence)return;
  populate(prepared.configurations);refreshCount();await start(prepared);
 }catch(error){status.textContent='Import rejected: '+error.message;}finally{file.value='';}};
 window.addEventListener('pagehide',()=>{++revision;clearPending();queue.cancel();executor.close();for(const chart of Object.values(charts))chart.dispose();});
 populate(defaultConfigurations(catalogue));filterOptions();updateTestInfo();refreshCount();render();root.dataset.ready='true';
 const initialRun=()=>{if(location.hash==='#ensemble'){render();if(!loading&&!testGap&&!study&&pendingRun===null&&!activeRun)schedule(0);}};
 window.addEventListener('hashchange',initialRun);initialRun();
}
// Keep this independent of other laboratories' loading/engine qualification.
function route(){if(location.hash==='#ensemble'){document.querySelectorAll('.page').forEach(el=>el.hidden=el!==root);document.querySelectorAll('.rail nav a').forEach(el=>{const active=el.hash==='#ensemble';el.classList.toggle('active',active);if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});}}
window.addEventListener('hashchange',route);route();
setup().catch(error=>{root.replaceChildren(node('h1','Ensemble explorer'),node('p','Unable to load: '+error.message));});
