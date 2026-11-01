import {defaultConfigurations,makeStudy,exportStudy,importStudy,resultSeries,modelIds,sweepParameters,validateExperiment} from './ensemble.mjs';
import {EnsembleQueue} from './ensemble-queue.mjs';
import {createRecordedDocument} from './recorded-document.mjs';
const root=document.getElementById('ensemble');
const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
const colors=['#256d64','#a55635','#6258a4'];
const names={'linear-elastic':'Linear elasticity','drucker-prager':'Drucker–Prager','modified-cam-clay':'Modified Cam Clay'};
const $=id=>document.getElementById(id);
function download(name,value){const a=node('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
async function loadExperiment(){
 const manifestResponse=await fetch('./ensemble-index.json');if(!manifestResponse.ok)throw Error('Ensemble experiment manifest is unavailable.');
 const manifest=await manifestResponse.json();
 if(manifest.version!=='atlas-ensemble-asset-0.1'||manifest.path!=='ensemble-experiment.json'||!Number.isSafeInteger(manifest.size_bytes)||manifest.size_bytes<1||manifest.size_bytes>2*1024*1024||!/^[a-f0-9]{64}$/.test(manifest.sha256))throw Error('Invalid ensemble experiment manifest.');
 const response=await fetch('./'+manifest.path);if(!response.ok)throw Error('Ensemble experiment is unavailable.');
 const bytes=await response.arrayBuffer(),digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 if(bytes.byteLength!==manifest.size_bytes||digest!==manifest.sha256)throw Error('Ensemble experiment checksum differs. Reload a consistent package.');
 return validateExperiment(JSON.parse(new TextDecoder().decode(bytes)));
}
function workerExecutor(catalogue){
 let worker=null,nextId=0;
 const close=()=>{worker?.terminate();worker=null;};
 const execute=(job,signal)=>new Promise((resolve,reject)=>{
  if(signal.aborted){reject(Error('Cancelled.'));return;}
  const id=++nextId;worker??=new Worker(new URL('./ensemble-worker.mjs',import.meta.url),{type:'module'});
  const abort=()=>{close();reject(Error('Cancelled.'));};signal.addEventListener('abort',abort,{once:true});
  const finish=(error,result)=>{signal.removeEventListener('abort',abort);if(error){close();reject(error);}else resolve(result);};
  worker.onmessage=({data})=>{if(data.id!==id)return;try{if(data.error)throw Error(data.error);createRecordedDocument(job.specification,data.result,catalogue);finish(null,data.result);}catch(e){finish(e);}};
  worker.onerror=event=>finish(Error(event.message||'Worker failed.'));
  worker.postMessage({id,specification:job.specification,catalogue});
 });
 return {execute,close};
}
function plot(svg,record,jobs,channel,selected){
 svg.replaceChildren();const ns='http://www.w3.org/2000/svg';
 const add=(tag,attrs,text)=>{const el=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;svg.append(el);return el;};
 const measured=record.rows.map(r=>[r.axial_strain*100,channel==='stress'?r.q/1000:r.volumetric_strain*100]);
 const series=jobs.map(job=>({job,points:resultSeries(job,channel)}));
 const all=[...measured,...series.flatMap(s=>s.points)],xs=all.map(p=>p[0]),ys=all.map(p=>p[1]);
 let lo=Math.min(...ys),hi=Math.max(...ys);const pad=Math.max((hi-lo)*.08,.01);lo-=pad;hi+=pad;
 const maxX=Math.max(...xs,.01),x=v=>62+v/maxX*460,y=v=>260-(v-lo)/(hi-lo)*220;
 add('title',{},(channel==='stress'?'Deviator stress':'Volumetric strain')+' versus axial strain');
 for(let i=0;i<=4;i++){
  const yy=40+i*55;add('line',{x1:62,y1:yy,x2:522,y2:yy,stroke:'#e2e6dc'});add('text',{x:53,y:yy+4,'text-anchor':'end'},Number((hi-(hi-lo)*i/4).toPrecision(3)));
  add('text',{x:62+i*115,y:281,'text-anchor':'middle'},Number((maxX*i/4).toPrecision(3)));
 }
 add('text',{x:62,y:22},channel==='stress'?'Deviator stress q (kPa)':'Volumetric strain (%) · compression positive');
 add('text',{x:292,y:310,'text-anchor':'middle'},'Axial strain (%)');
 add('polyline',{points:measured.map(([a,b])=>x(a)+','+y(b)).join(' '),fill:'none',stroke:'#59605c','stroke-width':2,'stroke-dasharray':'3 3'});
 series.sort((a,b)=>Number(a.job.id===selected)-Number(b.job.id===selected));
 for(const {job,points} of series){if(!points.length)continue;const active=job.id===selected;
  add('polyline',{points:points.map(([a,b])=>x(a)+','+y(b)).join(' '),fill:'none',stroke:colors[modelIds.indexOf(job.model)],'stroke-width':active?3:job.change?1.3:2,opacity:active?1:job.change?.45:.8,'stroke-dasharray':job.change?'5 2':'none'});
 }
}
async function setup(){
 const [record,catalogue]=await Promise.all([loadExperiment(),fetch('./models.json').then(r=>{if(!r.ok)throw Error('Model catalogue unavailable.');return r.json();})]);
 let study=null,selected=null,stale=false,revision=0,pendingRun=null,activeRun=null;
 const hidden=new Set(),editors=new Map();
 root.replaceChildren();
 const intro=node('div',undefined,'intro');intro.append(node('div'));intro.firstChild.append(node('span','ONE EXPERIMENT · MULTIPLE MODELS','eyebrow'),node('h1','Explore models together.'));root.append(intro);
 const experiment=node('section',undefined,'model-card');experiment.append(node('span','FIXED EXPERIMENT','eyebrow'),node('h2','OPARA · drained triaxial · 100 kPa'),node('p','Clayey-silty sand · measured starting effective stress 103.72 kPa · e₀ = 0.416. Replay: all 1,438 acquired observations, ending at 15.99% axial strain.'));
 const source=node('a','Ullmann et al. · source experiment ↗');source.href='https://doi.org/10.25532/OPARA-1072';source.target='_blank';source.rel='noopener noreferrer';experiment.append(source);
 const disclosure=node('details');disclosure.append(node('summary','Loading, preparation and comparison assumptions'),node('p','Axial strain and author membrane-corrected radial effective stress are imposed at acquired endpoints. The membrane correction uses measured volume change: these are conditional comparisons. Recorded order is preserved; elapsed time and consolidation history are not simulated.'));
 disclosure.append(node('p','All baselines are illustrative and uncalibrated for this specimen. Passing software checks does not establish model–material suitability. Modified Cam Clay uses an explicit assumed preconsolidation pressure, initially 200 kPa (OCR ≈ 1.93). Numerical scale and solver settings stay fixed.'));
 for(const warning of record.warnings)disclosure.append(node('p',warning));disclosure.append(node('p',record.provenance.attribution));experiment.append(disclosure);root.append(experiment);
 const layout=node('div',undefined,'ensemble-layout'),controls=node('form',undefined,'controls ensemble-controls'),results=node('div',undefined,'results-column');controls.id='ensemble-controls';controls.append(node('h2','Models & parameter variations'),node('p','SI units throughout. Each model runs its baseline, then changes one parameter at a time. Blank variation lists run only the baseline for that parameter.','control-hint'));
 const fields=node('div');controls.append(fields);
 function numeric(label,value,readonly=false){const wrapper=node('label',label),input=node('input');input.type='number';input.step='any';input.required=true;input.value=value;input.readOnly=readonly;wrapper.append(input);return {wrapper,input};}
 function populate(configurations){
  fields.replaceChildren();editors.clear();
  for(const config of configurations){
   const model=catalogue.models.find(m=>m.id===config.model),box=node('details',undefined,'ensemble-model');box.open=config.model==='linear-elastic';
   const heading=node('summary',names[config.model]);heading.style.borderLeftColor=colors[modelIds.indexOf(config.model)];box.append(heading);
   const enabledLabel=node('label',undefined,'ensemble-check'),enabled=node('input');enabled.type='checkbox';enabled.checked=config.enabled;enabled.disabled=!model;enabledLabel.append(enabled,node('span',model?'Include this model':'Unavailable in this engine'));box.append(enabledLabel);
   const parameters={},variations={},history={};
   if(model){
    const grid=node('div',undefined,'ensemble-fields');
    for(const [key,f]of Object.entries(model.parameters)){const item=numeric(key+' ('+f.unit+')',config.parameters[key],key==='p_ref');item.input.min=f.min;item.input.max=f.max;item.input.dataset.parameter=key;parameters[key]=item.input;grid.append(item.wrapper);}box.append(grid);
    if(config.model==='modified-cam-clay'){const item=numeric('Assumed initial pc (Pa) · not measured',config.history.pc);history.pc=item.input;box.append(item.wrapper);}
    for(const key of sweepParameters[config.model]){const label=node('label',key+' variation values · comma separated'),input=node('input');input.type='text';input.value=config.variations[key].join(', ');input.dataset.variation=key;variations[key]=input;label.append(input);box.append(label);}
    const definition=node('a','Exact model definition ↗');definition.href='./models/'+config.model+'.json';definition.target='_blank';definition.rel='noopener';box.append(definition);
   }
   fields.append(box);editors.set(config.model,{enabled,parameters,variations,history,original:config});
  }
 }
 const count=node('p','15 runs · three illustrative models');count.id='ensemble-count';const actions=node('div',undefined,'ensemble-actions'),cancel=node('button','Cancel'),save=node('button','Export ensemble'),importButton=node('button','Import & replay'),file=node('input');
 cancel.type=save.type=importButton.type='button';cancel.hidden=true;cancel.id='ensemble-cancel';save.disabled=true;save.id='ensemble-export';file.type='file';file.accept='.json,application/json';file.hidden=true;file.id='ensemble-file';importButton.id='ensemble-import';actions.append(cancel,save,importButton,file);
 const status=node('p','Parameters update the ensemble automatically.');status.id='ensemble-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');controls.append(count,actions,status);controls.insertBefore(count,fields);controls.insertBefore(actions,fields);controls.insertBefore(status,fields);
 const legend=node('div',undefined,'ensemble-legend');legend.append(node('span','··· Measurements'));
 for(const id of modelIds){const label=node('label',undefined,'ensemble-check'),input=node('input');input.type='checkbox';input.checked=true;label.style.color=colors[modelIds.indexOf(id)];label.append(input,node('span',names[id]));input.onchange=()=>{input.checked?hidden.delete(id):hidden.add(id);render();};legend.append(label);}
 results.append(legend,node('p','Solid: baseline · dashed: parameter variation · thicker: selected run.','control-hint'));
 const charts={};for(const channel of ['stress','volume']){const panel=node('section',undefined,'chart-panel'),svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.id='ensemble-'+channel;svg.setAttribute('viewBox','0 0 560 330');svg.setAttribute('role','img');svg.setAttribute('aria-label',channel==='stress'?'Ensemble deviator stress versus axial strain':'Ensemble volumetric strain versus axial strain');panel.append(svg);charts[channel]=svg;results.append(panel);}
 const outcomes=node('section',undefined,'experiment-card');outcomes.append(node('h2','Runs & outcomes'));const list=node('div');list.id='ensemble-runs';outcomes.append(list);const detail=node('section',undefined,'experiment-card');detail.append(node('h2','Selected run'));const detailText=node('p','Select a run to inspect its inputs.'),raw=node('pre'),rawDetails=node('details');raw.id='ensemble-selected';rawDetails.append(node('summary','Exact request, outcome and retained response'),raw);const single=node('button','Export selected recorded replay');single.type='button';single.disabled=true;single.id='ensemble-single-export';detail.append(detailText,single,rawDetails);results.append(outcomes,detail);layout.append(controls,results);root.append(layout);
 const executor=workerExecutor(catalogue),queue=new EnsembleQueue(executor.execute,()=>render());
 function read(){return modelIds.map(id=>{const e=editors.get(id);if(!e.parameters.p_ref||!e.enabled.checked)return {...e.original,enabled:false};return {model:id,enabled:e.enabled.checked,parameters:Object.fromEntries(Object.entries(e.parameters).map(([k,v])=>[k,v.value.trim()===''?NaN:Number(v.value)])),history:Object.fromEntries(Object.entries(e.history).map(([k,v])=>[k,v.value.trim()===''?NaN:Number(v.value)])),variations:Object.fromEntries(Object.entries(e.variations).map(([k,v])=>[k,v.value.trim()===''?[]:v.value.split(',').map(x=>x.trim()===''?NaN:Number(x.trim()))]))};});}
 function refreshCount(){for(const e of editors.values())for(const input of [...Object.values(e.parameters),...Object.values(e.history),...Object.values(e.variations)])input.disabled=!e.enabled.checked;try{const preview=makeStudy(record,catalogue,read());count.textContent=preview.jobs.length+' runs · '+preview.jobs.filter(j=>j.status==='rejected').length+' rejected by input checks';}catch(e){count.textContent=e.message;}}
 function render(){
  cancel.hidden=!queue.running&&pendingRun===null;save.disabled=!study||stale||queue.running;importButton.disabled=queue.running;
  const jobs=study?.jobs||[];
  for(const channel of ['stress','volume'])plot(charts[channel],record,jobs.filter(j=>!hidden.has(j.model)),channel,selected);
  if(study){const counts={};for(const job of jobs)counts[job.status]=(counts[job.status]||0)+1;
   status.textContent=(pendingRun!==null?'Updating after parameter changes · ':stale?'Inputs changed · displayed results are stale. ':'')+(queue.running?'Running · ':'')+Object.entries(counts).map(([k,v])=>v+' '+k).join(' · ');
  }
  list.replaceChildren();for(const job of jobs){const row=node('button',undefined,'ensemble-run-row');row.type='button';row.dataset.status=job.status;row.setAttribute('aria-pressed',String(job.id===selected));row.style.borderLeftColor=colors[modelIds.indexOf(job.model)];row.append(node('span',names[job.model]+' · '+job.label),node('span',job.status));row.onclick=()=>{selected=job.id;render();};list.append(row);}
  const job=jobs.find(j=>j.id===selected);single.disabled=!job?.result||stale||queue.running;
  if(job){detailText.textContent=names[job.model]+' · '+job.label+' · '+job.status+(job.message?' · '+job.message:'');raw.textContent=JSON.stringify({parameters:job.parameters,initial_history_assumptions:job.history,specification:job.specification,status:job.status,message:job.message,result:job.result},null,2);}
 }
 function clearPending(){clearTimeout(pendingRun);pendingRun=null;}
 async function start(prepared){
  const id=++revision;
  clearPending();
  if(queue.running)queue.cancel();
  await activeRun;
  if(id!==revision)return;
  let failure=null;
  try{
   const next=prepared||makeStudy(record,catalogue,read());
   study=next;stale=false;selected=study.jobs.some(job=>job.id===selected)?selected:study.jobs[0].id;
   activeRun=queue.run(study);await activeRun;
  }catch(e){failure='Cannot update: '+e.message;}
  finally{activeRun=null;executor.close();render();if(failure&&id===revision)status.textContent=failure;}
 }
 function schedule(delay=350){
  ++revision;clearPending();stale=!!study;
  if(queue.running)queue.cancel();
  pendingRun=setTimeout(()=>{pendingRun=null;void start();},delay);
  refreshCount();render();
 }
 controls.onsubmit=event=>{event.preventDefault();schedule(0);};
 controls.addEventListener('input',event=>{if(event.target!==file)schedule();});
 cancel.onclick=()=>{++revision;clearPending();queue.cancel();render();};
 save.onclick=()=>{try{download('opara-txcd100-ensemble.json',exportStudy(study,catalogue,record));}catch(e){status.textContent=e.message;}};
 single.onclick=()=>{const job=study.jobs.find(j=>j.id===selected);try{download(job.model+'-opara-recorded.json',createRecordedDocument(job.specification,job.result,catalogue));}catch(e){status.textContent=e.message;}};
 importButton.onclick=()=>file.click();file.onchange=async()=>{clearPending();const id=++revision;try{const item=file.files[0];if(!item)return;if(item.size>100*1024*1024)throw Error('Import exceeds 100 MB.');const text=await item.text();if(id!==revision)return;const prepared=importStudy(text,catalogue,record);populate(prepared.configurations);refreshCount();await start(prepared);}catch(e){status.textContent='Import rejected: '+e.message;}finally{file.value='';}};
 window.addEventListener('pagehide',()=>{++revision;clearPending();queue.cancel();executor.close();});
 populate(defaultConfigurations(catalogue));refreshCount();render();root.dataset.ready='true';
 const initialRun=()=>{if(location.hash==='#ensemble'&&!study&&pendingRun===null&&!activeRun)schedule(0);};
 window.addEventListener('hashchange',initialRun);initialRun();
}
// Keep this independent of other laboratories' loading/engine qualification.
function route(){if(location.hash==='#ensemble'){document.querySelectorAll('.page').forEach(el=>el.hidden=el!==root);document.querySelectorAll('.rail nav a').forEach(el=>{const active=el.hash==='#ensemble';el.classList.toggle('active',active);if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});}}
window.addEventListener('hashchange',route);route();
setup().catch(error=>{root.replaceChildren(node('h1','Ensemble explorer'),node('p','Unable to load: '+error.message));});
