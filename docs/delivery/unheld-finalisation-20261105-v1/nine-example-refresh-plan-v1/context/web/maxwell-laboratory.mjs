import {modelId,preset,solver,validateControls,parseRunJSON,importRun} from './maxwell-atlas-contract.mjs';
import {createMaxwellRunner} from './maxwell-atlas-runner.mjs';
export function setupMaxwellLaboratory({chart,cancelOrdinary=()=>{},createWorker}={}) {
  const $=id=>document.getElementById(id),ordinary=document.querySelector('#laboratory > .lab-layout'),links=document.querySelector('#laboratory > .workspace-links');
  if(!ordinary||!$('model'))throw Error('Maxwell requires the main atlas laboratory.');
  if($('maxwell-laboratory'))throw Error('Maxwell laboratory already initialized.');
  const panel=document.createElement('section');panel.id='maxwell-laboratory';panel.hidden=true;
  panel.innerHTML=`<div class="lab-layout"><form id="maxwell-controls" class="controls"><h2>Maxwell continuum</h2>
  <p class="control-hint">Elastic volume · viscous deviatoric response · dry total Cauchy stress · small strain · fixed spatial axes, zero spin.</p>
  <label>Illustrative history<select id="maxwell-preset"><option value="relaxation">Relaxation · hold strains</option><option value="creep">Creep · hold stresses</option><option value="oedometer">Oedometer · axial stress, lateral strain holds</option><option value="load-hold-reverse">Load–hold–reverse · complete strain rates</option></select></label>
  <label>Start time (s)<input id="maxwell-start" type="number" min="0" step="any" required></label>
  <label>Parameters [K (Pa), G (Pa), η (Pa·s)]<textarea id="maxwell-parameters" rows="2"></textarea></label>
  <details class="control-section"><summary>Complete initial state &amp; loading history</summary>
  <p class="control-hint">Compression positive. Six Mandel components: xx, yy, zz, √2xy, √2yz, √2xz. Initial stress and accumulated strain are independent history inputs; changing coefficients starts a new run. The oedometer preset includes its elastic preparation.</p>
  <label>Initial total Cauchy stress (six, Pa)<textarea id="maxwell-initial" rows="3"></textarea></label>
  <label>Initial accumulated strain (six, dimensionless)<textarea id="maxwell-initial-strain" rows="3"></textarea></label>
  <label>Initial strain rate (six, 1/s)<textarea id="maxwell-initial-rate" rows="3"></textarea></label>
  <label>Segments (JSON)<textarea id="maxwell-segments" rows="16" spellcheck="false"></textarea></label>
  <p class="control-hint">Each segment specifies an ID, duration in seconds, output intervals and six controls. Each control selects strain or stress and hold or rate; rate values use 1/s or Pa/s. Holds advance physical time. Up to 200 intervals per segment, 1000 total. JSON editing is for custom exploratory histories.</p></details>
  <p class="control-hint">Presets are illustrative, with bounded numerical evidence. Custom coefficients/history are exploratory; positive machine bounds are not a qualified material range. Fixed backward-Euler step-doubling settings. No calibration or experimental validation.</p>
  <div class="run-actions"><button id="maxwell-run">Run physical-time history</button><button type="button" id="maxwell-reset" class="secondary">Reset selected preset</button><button type="button" id="maxwell-import" class="secondary">Import &amp; replay</button><input id="maxwell-file" type="file" accept=".json,application/json" hidden><button type="button" id="maxwell-export" class="secondary" disabled>Export complete run</button><p id="maxwell-status" role="status">Select Maxwell to run a history.</p></div></form>
  <div class="results-column"><section class="experiment-card"><h2>Physical-time response</h2><p id="maxwell-summary">No current result.</p>
  <label>Plot component · Mandel<select id="maxwell-component"><option>xx</option><option>yy</option><option>zz</option><option>√2xy</option><option>√2yz</option><option>√2xz</option></select></label>
  <svg id="maxwell-stress" viewBox="0 0 480 290" role="img" aria-label="Selected total stress against physical time"></svg><svg id="maxwell-strain" viewBox="0 0 480 290" role="img" aria-label="Selected accumulated strain against physical time"></svg><svg id="maxwell-rate" viewBox="0 0 480 290" role="img" aria-label="Selected strain-rate samples against physical time"></svg>
  <p class="control-hint">Plots connect output samples. Unresolved strain rates at stress-control entry are omitted from the rate plot and identified in the table.</p>
  <details><summary>Complete stress, strain and rate history</summary><p>SI units. Initial and right-side entry events share a time; each segment endpoint is retained before the next entry. Unresolved rates are not zeros.</p><div style="overflow:auto;max-width:100%"><table id="maxwell-state" style="font-size:11px;white-space:nowrap"></table></div></details>
  <details><summary>Fetched model, review &amp; engine identities</summary><pre id="maxwell-identities" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
  <p>Measurement overlay unavailable: no compatible calibrated material or source experiment is supplied for these illustrative Maxwell histories. Curves do not imply agreement with Wichtmann data.</p></section>
  <details class="experiment-card" id="maxwell-equations"><summary>Equations, sources &amp; approved scope</summary><p>σ̇ = K tr(D) I + 2G dev(D) − (G/η) dev(σ). Relaxation time τ = η/G. Volume response is elastic; deviatoric stress relaxes.</p><p>Continuous small-strain law derived from Itasca 9.0.182. Atlas uses compression-positive Mandel components and its common physical-time integrator. This is a dry uncoupled total-stress specialization. Vendor central-difference updates, finite rotations, saturation, FE behavior and a broad parameter envelope are outside the approved scope. Continuous dissipation does not guarantee numerical energy decay for arbitrary loose settings. Source printed adjacent trace indices are interpreted as the trace projector; no published erratum is claimed.</p>
  <p><a href="https://docs.itascacg.com/itasca900/common/models/viscous/doc/modelviscous.html" target="_blank" rel="noopener">Itasca Maxwell equations</a> · <a href="https://docs.itascacg.com/itasca900/common/docproject/source/manual/program_guide/modelformulation/signconventions.html" target="_blank" rel="noopener">Source sign convention</a> · <a href="https://docs.itascacg.com/itasca900/flac3d/zone/test3d/Creep/OedometerMaxwell/oedometermaxwell.html" target="_blank" rel="noopener">Oedometer source</a></p>
  <p><a href="./engine-maxwell/review.html">Independent agent review &amp; exact scope</a> · <a href="./engine-maxwell/review.json">Nine-item checklist</a> · <a href="./engine-maxwell/approval.json">Approval and limitations</a> · <a href="./engine-maxwell/${modelId}.json">Exact model schema and source links</a></p>
  <p>Existing approval covers the frozen bounded CLI/ABI evidence. Website functional qualification is a separate delivery gate; custom requests retain their exploratory status.</p></details></div></div>`;
  ordinary.after(panel);
  if(![...$('model').options].some(o=>o.value===modelId))$('model').append(new Option('Maxwell · physical-time relaxation / creep',modelId));
  let active=false,last=null;
  const fields={parameters:'maxwell-parameters',initial:'maxwell-initial',initial_strain:'maxwell-initial-strain',initial_strain_rate:'maxwell-initial-rate',segments:'maxwell-segments'};
  const set=c=>{for(const [key,id]of Object.entries(fields))$(id).value=JSON.stringify(c[key],null,2);$('maxwell-start').value=c.start_time;};
  const read=()=>{
    if($('maxwell-start').value.trim()==='')throw Error('Start time is required.');
    return validateControls({schema_version:'0.2',units:'SI',model:modelId,...Object.fromEntries(Object.entries(fields).map(([key,id])=>[key,parseRunJSON($(id).value)])),start_time:Number($('maxwell-start').value),solver:{...solver}});
  };
  function render() {
    if(!last)return;const i=$('maxwell-component').selectedIndex,{result}=last,end=result.points.at(-1);
    chart('maxwell-stress','Physical time (s)','Total Cauchy stress (kPa)',result.points.map(p=>[p.time,p.state[i]/1000]));
    chart('maxwell-strain','Physical time (s)','Accumulated strain (%)',result.points.map(p=>[p.time,p.strain[i]*100]));
    chart('maxwell-rate','Physical time (s)','Strain rate (1/s)',result.points.filter(p=>p.strain_rate[i]!==null).map(p=>[p.time,p.strain_rate[i]]));
    $('maxwell-summary').textContent=`${result.segments.length} segments; ${result.start_time}–${end.time} s; final σxx=${end.state[0].toPrecision(7)} Pa, εxx=${end.strain[0].toPrecision(7)}.`;
    const names=['xx','yy','zz','√2xy','√2yz','√2xz'],table=$('maxwell-state');table.replaceChildren();const heading=document.createElement('tr');
    for(const label of ['t(s)','segment','side',...names.map(n=>'σ '+n+' (Pa)'),...names.map(n=>'ε '+n),...names.map(n=>'D '+n+' (1/s)')]){const th=document.createElement('th');th.textContent=label;heading.append(th);}table.append(heading);
    for(const p of result.points){const tr=document.createElement('tr');for(const value of [p.time,p.segment<0?'initial':result.segments[p.segment].id,p.side,...p.state,...p.strain,...p.strain_rate]){const td=document.createElement('td');td.textContent=value===null?'unresolved':typeof value==='number'?Number(value.toPrecision(8)):value;tr.append(td);}table.append(tr);}
    $('maxwell-identities').textContent=JSON.stringify(last.provenance,null,2);
  }
  const runner=createMaxwellRunner({createWorker,notify:event=>{
    last=event.run||null;$('maxwell-status').textContent=event.message;$('maxwell-run').disabled=event.state==='running';$('maxwell-export').disabled=event.state!=='complete';
    if(last)render();else{for(const id of ['maxwell-stress','maxwell-strain','maxwell-rate','maxwell-state'])$(id).replaceChildren();$('maxwell-identities').textContent='';$('maxwell-summary').textContent='No current result.';}
  }});
  function run(event,expected=null){event?.preventDefault();if(!active)return;let c;try{c=read();}catch(error){runner.cancel('Invalid input: '+error.message);return;}runner.run(c,{expected});}
  set(preset('relaxation'));
  $('maxwell-controls').onsubmit=run;
  $('maxwell-controls').addEventListener('input',e=>{if(!['maxwell-file','maxwell-preset'].includes(e.target.id))runner.cancel();});
  $('maxwell-preset').onchange=()=>{runner.cancel();set(preset($('maxwell-preset').value));};
  $('maxwell-component').onchange=render;
  $('maxwell-reset').onclick=()=>{runner.cancel();set(preset($('maxwell-preset').value));run();};
  $('maxwell-import').onclick=()=>$('maxwell-file').click();
  $('maxwell-file').onchange=async()=>{
    runner.cancel('Reading imported Maxwell history…');const id=runner.generation;
    try{
      const file=$('maxwell-file').files[0];$('maxwell-file').value='';if(!file)return;if(file.size>10*1024*1024)throw Error('Import exceeds 10 MB.');
      const text=await file.text(),response=await fetch(new URL('./engine-maxwell/identity.json',import.meta.url),{cache:'no-store'});
      if(!response.ok)throw Error('Maxwell package identity unavailable.');const identity=parseRunJSON(await response.text());
      if(id!==runner.generation||!active)return;
      const imported=importRun(text,identity);set(imported.controls);run(undefined,parseRunJSON(text));
    }catch(error){if(id===runner.generation)runner.cancel('Import rejected: '+error.message);}
    finally{if(id===runner.generation)$('maxwell-file').value='';}
  };
  $('maxwell-export').onclick=()=>{
    if(!last)return;const url=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='maxwell-atlas-run.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  function select(id,{auto=true}={}){
    const next=id===modelId,changed=next!==active;
    if(!next){if(changed){active=false;runner.cancel('Maxwell inactive.');panel.hidden=true;ordinary.hidden=false;if(links)links.hidden=false;if($('import-run'))$('import-run').hidden=false;}return false;}
    active=true;ordinary.hidden=true;if(links)links.hidden=true;panel.hidden=false;if($('import-run'))$('import-run').hidden=true;cancelOrdinary();$('model').value=modelId;
    $('model-description').textContent='Maxwell continuum: elastic volume and relaxing deviatoric stress. Complete physical-time stress/strain/rate history.';$('model-family').textContent='Linear viscoelasticity';$('model-status').textContent='Approved bounded CLI/ABI scope';$('model-sources').replaceChildren();
    const a=document.createElement('a');a.href='./engine-maxwell/review.html';a.textContent='Independent agent review and exact scope';$('model-sources').append(a);
    if(changed&&auto)run();return true;
  }
  return {modelId,select,get active(){return active;},run,showEquations(){if(!active)return false;$('maxwell-equations').open=true;$('maxwell-equations').scrollIntoView({behavior:'smooth'});return true;}};
}
