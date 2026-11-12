import {parseRecordedDocument,createRecordedDocument,recordedDocumentCSV} from './recorded-document.mjs';
import {persistentState} from './state-contract.mjs';

export const recordedLaboratoryId='__recorded_path__';
// All six Mandel stress/strain components remain in the request and saved result.
export function recordedCurves(result){
 const curves={stress:[],path:[],volume:[],strain:[]};
 for(const point of result?.points??[]){
  const sigma=point.state.slice(0,6),p=(sigma[0]+sigma[1]+sigma[2])/3;
  const q=Math.sqrt(1.5*sigma.reduce((sum,value,i)=>sum+(i<3?value-p:value)**2,0));
  curves.stress.push([point.strain[0]*100,q/1000]);curves.path.push([p/1000,q/1000]);
  curves.volume.push([point.strain[0]*100,point.strain.slice(0,3).reduce((a,b)=>a+b,0)*100]);
  curves.strain.push([point.coordinate,point.strain[0]*100]);
 }
 return curves;
}
export function setupRecordedLaboratory({catalogue,chart,cancelOrdinary,onLeave}){
 const $=id=>document.getElementById('recorded-lab-'+id),root=document.createElement('section');
 root.id='recorded-laboratory';root.hidden=true;
 root.innerHTML=`<div class="lab-layout"><form class="controls" id="recorded-lab-controls">
 <h2>Full recorded loading path</h2><p id="recorded-lab-summary"></p>
 <p class="control-hint" id="recorded-lab-hint">Every acquired control point is retained. Parameter and starting-state edits rerun the same path.</p>
 <button type="button" id="recorded-lab-leave" class="secondary">Use standard loading controls</button>
 <details class="control-section"><summary>Material parameters</summary><div id="recorded-lab-parameters"></div></details>
 <details class="control-section"><summary>Complete starting state</summary><div id="recorded-lab-initial"></div></details>
 <details class="control-section"><summary>Exact loading path and solver settings</summary><pre id="recorded-lab-path"></pre></details>
 <p id="recorded-lab-status" role="status" aria-live="polite"></p>
 <button id="recorded-lab-run" type="submit">Replay full path</button>
 <button id="recorded-lab-stop" type="button" hidden>Stop calculation</button>
 <button id="recorded-lab-export" type="button" disabled>Reproducible run</button>
 <button id="recorded-lab-csv" type="button" disabled>Results CSV</button>
 <details id="recorded-lab-equations"><summary>Model equations and sources</summary><div id="recorded-lab-sources"></div><pre id="recorded-lab-law"></pre></details>
 </form><div class="results-column">
 <section class="chart-panel"><h2>Stress–strain response</h2><svg id="recorded-lab-stress" viewBox="0 0 480 290" role="img" aria-label="Recorded deviator stress versus axial strain"></svg></section>
 <section class="chart-panel"><h2>Stress path</h2><svg id="recorded-lab-stress-path" viewBox="0 0 480 290" role="img" aria-label="Recorded deviator stress versus mean stress"></svg></section>
 <section class="chart-panel"><h2>Volumetric response</h2><svg id="recorded-lab-volume" viewBox="0 0 480 290" role="img" aria-label="Recorded volumetric versus axial strain"></svg></section>
 <section class="chart-panel"><h2>Full axial strain history</h2><svg id="recorded-lab-strain" viewBox="0 0 480 290" role="img" aria-label="Recorded axial strain versus acquisition order"></svg></section>
 </div></div>`;
 document.getElementById('laboratory').append(root);
 const ordinaryCatalogue=catalogue;
 let workerPath='./worker.js',fixed=false;
 let active=false,spec=null,result=null,worker=null,generation=0,timer=null,debounce=null;
 const inputs={parameters:[],initial:[]};
 const exports=enabled=>{$('export').disabled=$('csv').disabled=!enabled;};
 function stop(){++generation;clearTimeout(timer);clearTimeout(debounce);worker?.terminate();worker=null;$('stop').hidden=true;}
 function select(id){
  stop();active=id===recordedLaboratoryId;root.hidden=!active;
  document.querySelector('#laboratory > .lab-layout').hidden=active;
  document.querySelector('#laboratory > .workspace-links').hidden=active;
  document.getElementById('import-run').hidden=active;
  if(active)cancelOrdinary();return active;
 }
 function plot(){
  const c=recordedCurves(result),scope=spec?.stress_scope??'effective';
  chart('recorded-lab-stress','Axial strain (%)','Deviator stress q (kPa)',c.stress);
  chart('recorded-lab-stress-path','Mean '+scope+' stress (kPa)','Deviator stress q (kPa)',c.path);
  chart('recorded-lab-volume','Axial strain (%)','Volumetric strain (%)',c.volume);
  chart('recorded-lab-strain',spec?.path.coordinate.name??'Acquisition order','Axial strain (%)',c.strain);
 }
 function read(){
  const next=structuredClone(spec);
  for(const key of ['parameters','initial'])for(const {input,offset,size} of inputs[key]){
   const tokens=input.value.split(',');if(tokens.length!==size||tokens.some(v=>!v.trim()||!Number.isFinite(Number(v))))throw Error('Use '+size+' finite value(s) for '+input.name+'.');
   tokens.forEach((v,i)=>next[key][offset+i]=Number(v));
  }
  return parseRecordedDocument(JSON.stringify(next),catalogue).specification;
 }
 function run(){
  if(!active||!spec)return;stop();exports(false);const id=generation;
  try{
   spec=read();result=null;plot();$('status').textContent='Replaying full recorded path…';$('stop').hidden=false;
   worker=new Worker(workerPath,{type:'module'});
   worker.onmessage=({data})=>{
    if(id!==generation||data.id!==id||!active)return;
    clearTimeout(timer);worker?.terminate();worker=null;$('stop').hidden=true;
    try{
     if(data.error)throw Error(data.error);
     result=createRecordedDocument(spec,data.result,catalogue).result;plot();exports(result.points.length>0);
     $('status').textContent=result.ok?'Response up to date · '+result.points.length+' ordered observations.':'Stopped · '+result.points.length+' committed observations retained. '+result.message;
    }catch(e){result=null;exports(false);$('status').textContent='Replay failed: '+e.message;}
   };
   worker.onerror=event=>{if(id!==generation)return;stop();$('status').textContent='Replay failed: '+event.message;};
   timer=setTimeout(()=>{if(id!==generation)return;stop();$('status').textContent='Replay exceeded 60 seconds. Check the material inputs.';},60000);
   worker.postMessage({id,kind:'recorded',specification:spec,catalogue});
  }catch(e){stop();result=null;plot();$('status').textContent='Cannot replay: '+e.message;}
 }
 function field(container,label,value,offset,size,key,readonly=false){
  const wrapper=document.createElement('label'),input=document.createElement('input');wrapper.textContent=label;input.name=label;input.value=value.join(', ');input.required=true;input.readOnly=readonly;
  if(size===1){input.type='number';input.step='any';}else input.type='text';
  wrapper.append(input);$(container).append(wrapper);if(!readonly)inputs[key].push({input,offset,size});
 }
 function load(saved,{partition=ordinaryCatalogue,worker='./worker.js',readOnly=false,title=null,hint=null}={}){
  catalogue=partition;workerPath=worker;fixed=readOnly;
  $('hint').textContent=fixed?(hint??'Replay the verified six-component example with its original inputs. The repeated target records the same state without another material update.'):'Every acquired control point is retained. Parameter and starting-state edits rerun the same path.';
  $('leave').textContent=fixed?'Return to standard laboratory':'Use standard loading controls';
  const parsed=parseRecordedDocument(JSON.stringify(saved),catalogue),model=catalogue.models.find(m=>m.id===parsed.specification.model);
  stop();spec=structuredClone(parsed.specification);result=null;
  spec.parameters??=Object.values(model.parameters).map(p=>p.default);spec.initial??=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]);
  $('sources').replaceChildren();for(const source of model.sources??[]){if(!/^https?:\/\//i.test(source.url))continue;const p=document.createElement('p'),a=document.createElement('a');a.textContent=source.locator??source.role??'Source';a.href=source.url;a.target='_blank';a.rel='noopener';p.append(a);$('sources').append(p);}$('law').textContent=JSON.stringify({derived:model.derived,state:model.state},null,2);
  $('parameters').replaceChildren();$('initial').replaceChildren();inputs.parameters=[];inputs.initial=[];
  Object.entries(model.parameters).forEach(([name,p],offset)=>field('parameters',name+' ('+p.unit+')',[spec.parameters[offset]],offset,1,'parameters',fixed));
  let offset=0;for(const f of model.state){const size=f.shape==='sym'?6:1;field('initial',f.name+' ('+f.unit+')'+(size===6?' · Mandel xx, yy, zz, √2xy, √2yz, √2xz':''),spec.initial.slice(offset,offset+size),offset,size,'initial',fixed||!persistentState(f));offset+=size;}
  const axial=spec.path.controls[0],axialControl=axial.kind==='strain'&&axial.coefficients.every((v,i)=>v===Number(i===0));
  $('summary').textContent=(title??model.name)+' · '+spec.path.knots.length+' ordered control points'+(axialControl?' · ending at '+Number((spec.path.knots.at(-1).targets[0]*100).toPrecision(6))+'% axial strain.':'.');
  $('path').textContent=JSON.stringify({path:spec.path,integration_settings:spec.integration_settings,control_settings:spec.control_settings},null,2);
  select(recordedLaboratoryId);run();return spec.model;
 }
 function download(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
 $('controls').onsubmit=e=>{e.preventDefault();run();};
 $('controls').addEventListener('input',()=>{stop();exports(false);$('status').textContent='Inputs changed · updating full path…';debounce=setTimeout(run,350);});
 $('stop').onclick=()=>{stop();exports(false);$('status').textContent='Calculation stopped. Replay full path to restart.';};
 $('leave').onclick=()=>onLeave(fixed?'hypoplastic-sand-vw96':spec.model);
 $('export').onclick=()=>download(spec.model+'-recorded.json',JSON.stringify(createRecordedDocument(spec,result,catalogue),null,2),'application/json');
 $('csv').onclick=()=>download(spec.model+'-recorded.csv',recordedDocumentCSV(spec,result,catalogue),'text/csv');
 return {modelId:recordedLaboratoryId,select,load,run,get active(){return active;},showEquations(){if(!active)return false;$('equations').open=true;$('equations').scrollIntoView({behavior:'smooth'});return true;}};
}
