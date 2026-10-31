import {parseRecordedJSON,validateRecordedRun,verifyRecordedResponse,recordedSeries} from './recorded.mjs';
export function setupRecordedView({models,catalogueHash,chart,sourceLinks,definitionLink}){
 const $=id=>document.getElementById(id);
 let spec=null,result=null,worker=null,timer=null,generation=0;
 const message=text=>{$('recorded-status').textContent=text;};
 const exports=enabled=>{$('recorded-export').disabled=$('recorded-csv').disabled=!enabled;};
 const stop=()=>{++generation;clearTimeout(timer);worker?.terminate();worker=null;$('recorded-cancel').hidden=true;};
 function plot(){
  const component=Number($('recorded-component').value),label=$('recorded-component').selectedOptions[0].textContent;
  const data=result?recordedSeries(result,component):{strain:[],stress:[]};
  const axis=spec?spec.path.coordinate.name+' [1]':'Record order [1]';
  chart('recorded-strain-chart',axis,label+' strain [1]',data.strain,[]);
  chart('recorded-stress-chart',axis,label+' stress [kPa]',data.stress,[]);
 }
 function download(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
 function replay(){
  if(!spec)return;stop();const id=generation;result=null;exports(false);plot();
  message('Replaying ordered records…');$('recorded-cancel').hidden=false;
  worker=new Worker('./worker.js',{type:'module'});
  worker.onmessage=({data})=>{
   if(data.id!==id||id!==generation)return;clearTimeout(timer);worker.terminate();worker=null;$('recorded-cancel').hidden=true;
   try{
    if(data.error)throw Error(data.error);const r=verifyRecordedResponse(data.result,spec);
    if(r.catalogue_hash!==catalogueHash)throw Error('Engine and catalogue differ. Reload a matching build.');
    result=r;plot();exports(Boolean(r.points.length));
    message(r.ok?`Replay complete · ${r.points.length} ordered observations · ${r.material_trials} material trials.`:r.failed_knot<0?`Replay rejected before integration. ${r.message}`:`Stopped at record ${r.failed_knot} · ${r.points.length} committed observations retained. ${r.message}`);
    $('recorded-resolved').textContent=JSON.stringify({parameters:r.parameters,initial:r.initial,integration_settings:r.integration_settings,control_settings:r.control_settings,...(r.restart_settings?{restart_settings:r.restart_settings,restart_diagnostics:r.restart_diagnostics}:{})},null,2);
   }catch(error){message('Replay error: '+error.message);}
  };
  worker.onerror=event=>{if(id!==generation)return;stop();message('Replay error: '+event.message);};
  timer=setTimeout(()=>{if(id!==generation)return;stop();message('Replay stopped after 60 seconds. Use fewer records or check the material domain.');},60000);
  worker.postMessage({id,kind:'recorded',specification:spec});
 }
 function load(doc){
  stop();spec=result=null;exports(false);$('recorded-replay').disabled=true;$('recorded-resolved').textContent='';plot();
  if(doc?.catalogue_hash&&doc.catalogue_hash!==catalogueHash)throw Error('Recorded run uses a different catalogue. Use its matching release.');
  const candidate=doc?.specification??doc;validateRecordedRun(candidate);
  const model=models.find(m=>m.id===candidate.model);if(!model)throw Error('This model is not in the public executable catalogue.');
  spec=structuredClone(candidate);$('recorded-model').textContent=model.name;
  $('recorded-summary').textContent=`${spec.path.knots.length} records · ${spec.path.controls.map((c,i)=>`${i+1}: ${c.kind}`).join(' · ')}. Initial state and parameters: ${spec.initial?'supplied':'model defaults'} / ${spec.parameters?'supplied':'model defaults'}.`;
  const sources=$('recorded-sources');sources.replaceChildren();sourceLinks(sources,model.sources);sources.append(definitionLink(model.id));
  $('recorded-replay').disabled=false;replay();
 }
 async function importRecorded(read){
  // Invalidate both running work and pending reads before awaiting a new source.
  stop();const id=generation;spec=result=null;exports(false);
  $('recorded-replay').disabled=true;$('recorded-resolved').textContent='';plot();
  message('Reading recorded path…');$('recorded-cancel').hidden=false;
  let doc;
  try{doc=await read();}
  catch(error){if(id===generation){$('recorded-cancel').hidden=true;message('Import rejected: '+error.message);}return;}
  if(id!==generation)return;
  try{load(doc);}catch(error){$('recorded-cancel').hidden=true;message('Import rejected: '+error.message);}
 }
 $('recorded-file').onchange=event=>{
  const file=event.target.files[0];if(!file)return;event.target.value='';
  return importRecorded(async()=>{
   if(file.size>10*1024*1024)throw Error('File exceeds 10 MB.');
   return parseRecordedJSON(await file.text());
  });
 };
 $('recorded-example').onclick=()=>importRecorded(async()=>{
  const response=await fetch('./recorded-example.json');if(!response.ok)throw Error('Example unavailable.');
  return parseRecordedJSON(await response.text());
 });
 $('recorded-replay').onclick=replay;$('recorded-component').onchange=plot;
 $('recorded-cancel').onclick=()=>{stop();message(spec?'Replay cancelled. Run again to restart from the supplied initial state.':'Import cancelled. Load a recorded path to start again.');};
 $('recorded-export').onclick=()=>download(spec.model+'-recorded.json',JSON.stringify({schema_version:'experimental-recorded-replay-export-0.1',catalogue_hash:catalogueHash,specification:spec,result},null,2),'application/json');
 $('recorded-csv').onclick=()=>{
  const labels=['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz'];
  const header=['coordinate_1',...labels.map(c=>'strain_'+c+'_1'),...labels.map(c=>'effective_stress_'+c+'_Pa'),'control_error','iterations','substeps'];
  const rows=result.points.map(p=>[p.coordinate,...p.strain,...p.state.slice(0,6),p.control_error,p.diagnostics.iterations,p.diagnostics.substeps].join(','));
  download(spec.model+'-recorded.csv',[header.join(','),...rows].join('\n'),'text/csv');
 };
 plot();
}
