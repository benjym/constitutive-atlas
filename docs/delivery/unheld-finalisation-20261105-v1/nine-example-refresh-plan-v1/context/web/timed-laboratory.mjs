import {defaults,modelId,validateControls,request,importRun} from './timed-contract.mjs';
export function setupTimedLaboratory({chart,onOrdinary,cancelOrdinary}){
 const $=id=>document.getElementById(id),panel=document.createElement('section');panel.id='timed-laboratory';panel.hidden=true;
 panel.innerHTML=`<div class="lab-layout"><form id="timed-controls" class="controls"><h2>Physical-time controls</h2>
 <p class="control-hint">Continuous Burgers law · dry total stress · small strain · zero spin. All six components are held. Other strain-path protocols are unavailable for this interface.</p>
 <label>Experiment<select id="timed-mode"><option value="relaxation">Relaxation · hold all strains</option><option value="creep">Creep · hold all stresses</option></select></label>
 <label>Duration (s)<input id="timed-duration" type="number" step="any" required></label><label>Output intervals<input id="timed-samples" type="number" step="1" required></label>
 <label>Start time (s)<input id="timed-start" type="number" step="any" required></label>
 <details><summary>Material parameters · SI units</summary><p>K, Gm, Gk (Pa); ηm, ηk (Pa s). Positive finite values.</p><label>Five parameters<textarea id="timed-parameters" rows="3" style="width:100%"></textarea></label></details>
 <details><summary>Complete initial state &amp; preparation</summary><p>Mandel order: xx, yy, zz, √2xy, √2yz, √2xz. Compression positive. Twelve explicit components: six stresses (Pa), then six Kelvin strains. Kelvin normal components sum to zero within1e-12. This is an illustrative prepared state, not a calibrated specimen.</p>
 <label>Stress and Kelvin strain<textarea id="timed-initial" rows="5" style="width:100%"></textarea></label><label>Accumulated strain (six)<textarea id="timed-strain" style="width:100%"></textarea></label><label>Initial strain rate (1/s, six)<textarea id="timed-rate" style="width:100%"></textarea></label></details>
 <p class="control-hint">Implicit backward Euler with step doubling; fixed qualified example solver settings. Changed coefficients/time/state are exploratory, without a general accuracy guarantee. Parameters are uncalibrated.</p>
 <button id="timed-run">Run physical-time history</button><button type="button" id="timed-reset" class="secondary">Reset example</button><button type="button" id="timed-import" class="secondary">Import &amp; replay</button><input id="timed-file" type="file" accept=".json,application/json" hidden><button type="button" id="timed-export" class="secondary" disabled>Export full result</button><p id="timed-status" role="status"></p></form>
 <div class="results-column"><section class="experiment-card"><h2>Physical-time response</h2><p id="timed-summary">Run a history.</p><svg id="timed-stress" viewBox="0 0 480 290" role="img" aria-label="Axial total stress against physical time"></svg><svg id="timed-strain-chart" viewBox="0 0 480 290" role="img" aria-label="Axial strain against physical time"></svg><svg id="timed-kelvin" viewBox="0 0 480 290" role="img" aria-label="Axial Kelvin strain against physical time"></svg>
 <details><summary>All state, rates and fetched identities</summary><pre id="timed-state" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
 <p>Measurement comparison is unavailable: these illustrative parameters have no matched calibrated material or approved compatible experiment. No experimental validation is implied.</p></section>
 <details class="experiment-card" id="timed-equations"><summary>Equations, sources &amp; reviewed scope</summary><p>σ̇ = K tr(D) I + 2Gm [dev(D) − ε̇k − dev(σ)/(2ηm)]; ε̇k = [dev(σ) − 2Gk dev(εk)]/(2ηk).</p><p>Elastic volume and Burgers deviatoric response. Physical seconds, infinitesimal strain, fixed spatial zero-spin frame; dry uncoupled total stress. Vendor centered update, finite rotations, plasticity and host coupling excluded. Independent approval supports the exact bounded frozen native/Wasm cases; new browser delivery qualification is recorded separately.</p><p><a href="https://docs.itascasoftware.com/itasca900/common/models/burgers/doc/modelburgers.html" target="_blank" rel="noopener">Itasca Burgers model source</a> · <a href="engine-burgers/review.json">Nine-item independent review</a> · <a href="engine-burgers/approval.json">Approved scope</a> · <a href="engine-burgers/${modelId}.json">Exact definition</a> · <a href="docs/models/burgers-main-laboratory-v1.md.html">Source/numerical dossier</a></p></details></div></div>`;
 const ordinary=document.querySelector('#laboratory > .lab-layout'),links=document.querySelector('#laboratory > .workspace-links');ordinary.after(panel);
 $('model').append(new Option('Burgers · physical-time creep / relaxation',modelId));
 let active=false,worker=null,generation=0,last=null,timer=null;
 const set=c=>{for(const k of Object.keys(defaults))$('timed-'+k).value=Array.isArray(c[k])?JSON.stringify(c[k]):c[k];};
 const read=()=>Object.fromEntries(Object.entries(defaults).map(([k,v])=>[k,Array.isArray(v)?JSON.parse($('timed-'+k).value):k==='mode'?$('timed-'+k).value:Number($('timed-'+k).value)]));
 function invalidate(message='Inputs changed. Run to update results.'){
  generation++;worker?.terminate();worker=null;clearTimeout(timer);last=null;$('timed-export').disabled=true;
  for(const id of ['timed-stress','timed-strain-chart','timed-kelvin'])$(id).replaceChildren();
  $('timed-state').textContent='';$('timed-summary').textContent='No current result.';$('timed-status').textContent=message;$('timed-run').disabled=false;
 }
 function run(event){
  event?.preventDefault();invalidate();let controls;
  try{controls=validateControls(read());}catch(e){$('timed-status').textContent='Invalid input: '+e.message;return;}
  const id=generation;worker=new Worker(new URL('./timed-worker.mjs',import.meta.url),{type:'module'});$('timed-status').textContent='Running physical-time history…';$('timed-run').disabled=true;
  const failure=message=>{if(id!==generation)return;invalidate('Run failed: '+message);};
  timer=setTimeout(()=>failure('Time limit exceeded; reduce duration/output or check parameters.'),30000);
  worker.onerror=e=>failure(e.message);
  worker.onmessage=({data})=>{
   if(id!==generation||data.id!==id)return;
   if(data.error){failure(data.error);return;}
   clearTimeout(timer);worker.terminate();worker=null;
   const {result,identity,args}=data,end=result.points.at(-1);
   last={kind:'atlas-timed-hold-v1',controls,provenance:identity,request:{function:'atlas_run_schedule',args},result};
   chart('timed-stress','Physical time (s)','Axial total stress (kPa)',result.points.map(p=>[p.time,p.state[0]/1000]));
   chart('timed-strain-chart','Physical time (s)','Accumulated axial strain (%)',result.points.map(p=>[p.time,p.strain[0]*100]));
   chart('timed-kelvin','Physical time (s)','Axial Kelvin strain (%)',result.points.map(p=>[p.time,p.state[6]*100]));
   $('timed-summary').textContent=`${controls.mode}: ${controls.duration} s; final axial strain ${end.strain[0].toPrecision(7)}, total axial stress ${end.state[0].toPrecision(7)} Pa.`;
   $('timed-state').textContent=JSON.stringify({basis:'Mandel; compression positive',time_s:end.time,stress_Pa:end.state.slice(0,6),Kelvin_strain:end.state.slice(6),accumulated_strain:end.strain,strain_rate_per_s:end.strain_rate,identity},null,2);
   $('timed-status').textContent=`Completed ${controls.samples} output intervals.`;$('timed-run').disabled=false;$('timed-export').disabled=false;
  };
  worker.postMessage({id,controls});
 }
 set(defaults);$('timed-controls').onsubmit=run;$('timed-controls').addEventListener('input',e=>{if(e.target.id!=='timed-file')invalidate();});
 $('timed-reset').onclick=()=>{set(defaults);run();};$('timed-import').onclick=()=>$('timed-file').click();
 $('timed-file').onchange=async()=>{
  invalidate('Reading imported history…');const id=generation;
  try{const file=$('timed-file').files[0];if(!file)return;if(file.size>10*1024*1024)throw Error('Import exceeds10MB.');const text=await file.text();const r=await fetch('./engine-burgers/identity.json');if(!r.ok)throw Error('Package identity unavailable.');const identity=await r.json();if(id!==generation)return;set(importRun(text,identity));$('timed-file').value='';run();}
  catch(e){if(id===generation)$('timed-status').textContent='Import rejected: '+e.message;}
  finally{if(id===generation)$('timed-file').value='';}
 };
 $('timed-export').onclick=()=>{if(!last)return;const url=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='burgers-'+last.controls.mode+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 function select(id,{auto=true}={}){
  const next=id===modelId,changed=next!==active;active=next;ordinary.hidden=next;links.hidden=next;panel.hidden=!next;$('import-run').hidden=next;
  if(!next){if(changed)invalidate();return false;}
  cancelOrdinary();$('model').value=modelId;$('model-description').textContent='Continuous Burgers viscoelasticity. Explore physical-time creep and relaxation; full stress and Kelvin history retained.';$('model-family').textContent='Viscoelasticity';$('model-status').textContent='Approved bounded scope';
  $('model-sources').replaceChildren();const a=document.createElement('a');a.href='engine-burgers/review.json';a.textContent='Independent review and exact scope';$('model-sources').append(a);
  if(changed&&auto)run();return true;
 }
 return {modelId,select,get active(){return active;},run,showEquations(){if(active){$('timed-equations').open=true;$('timed-equations').scrollIntoView();return true;}return false;}};
}
