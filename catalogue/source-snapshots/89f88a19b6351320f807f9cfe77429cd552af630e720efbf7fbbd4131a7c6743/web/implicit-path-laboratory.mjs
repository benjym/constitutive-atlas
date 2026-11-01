import {modelId,kind,preset,settings,validateControls,parseRunJSON,importRun,stringifyRun} from './implicit-path-contract.mjs';
import {createImplicitPathRunner} from './implicit-path-runner.mjs';
// Main-atlas view only; all material calculations run in the verified worker.
export function setupImplicitPathLaboratory({chart,cancelOrdinary=()=>{},createWorker}={}){
 const $=id=>document.getElementById(id),ordinary=document.querySelector('#laboratory > .lab-layout'),links=document.querySelector('#laboratory > .workspace-links');
 if(!ordinary||!$('model')||$('implicit-path-laboratory'))throw Error('Implicit-path requires one main atlas laboratory.');
 const panel=document.createElement('section');panel.id='implicit-path-laboratory';panel.hidden=true;
 panel.innerHTML=`<div class="lab-layout"><form id="ip-controls" class="controls"><h2>Lade–Duncan 1975</h2>
 <p class="control-hint">Original elastoplastic cohesionless-soil law. Small strain · compression positive · fixed spatial axes · total mechanical Cauchy stress with zero pore pressure.</p>
 <label>Illustrative source parameters<select id="ip-preset"><option value="dense">Dense sand · Table 1</option><option value="loose">Loose sand · Table 1</option></select></label>
 <label>Loading control<select id="ip-protocol"><option value="1">Triaxial · fixed lateral stress</option><option value="0">Oedometer · zero lateral strain</option><option value="2">Constant volume · prescribed axial strain</option><option value="3">Constant volume · prescribed deviator stress change</option><option value="4">Isotropic strain</option></select></label>
 <label id="ip-target-label">Control amplitude<input id="ip-target" type="number" step="any" required></label><p id="ip-unit" class="control-hint"></p>
 <label>Caller increments<input id="ip-steps" type="number" min="1" max="5000" step="1" required></label>
 <label>Cycles (0 for a monotonic ramp)<input id="ip-cycles" type="number" min="0" max="100" step="1" required></label>
 <details class="control-section"><summary>Parameters &amp; complete initial state</summary>
 <label>Parameters [pₐ (Pa), k₁, fₜ, A, r_f, M, l, K_ur, n, νᵢ]<textarea id="ip-parameters" rows="4"></textarea></label>
 <p class="control-hint">All parameters except pₐ are dimensionless. The two Table 1 sets are source examples; intermediate combinations are exploratory. pₐ=101325 Pa and νᵢ=0 are fixed in this realization.</p>
 <label>Initial state [σxx, σyy, σzz, √2σxy, √2σyz, √2σxz (Pa), history gap (1), plastic work (Pa)]<textarea id="ip-initial" rows="4"></textarea></label>
 <p class="control-hint">Prepare axisymmetric positive-definite stress below failure. Presets start at 60 kPa isotropic stress, H=fₜ and zero plastic work. The signed gap is a numerical history carrier: H=max(fₜ, f+max(gap,0)). It is distinct from deviator stress q.</p></details>
 <details><summary>Numerical settings &amp; limits</summary><pre id="ip-settings" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre>
 <p class="control-hint">Fixed implicit step-doubling settings. Elastic modulus uses midpoint stress; plastic flow/history use the endpoint. Holds preserve state; loading is parameterized by strain path, without a physical clock. Positive-pressure finite-lifetime boundaries can end unloading. Failed increments retain the last committed point. A run has a 120-second worker limit including loading and initialization.</p></details>
 <p class="control-hint">Source-qualified bounded numerical examples; custom paths/initial states remain exploratory. No post-failure continuation, large-strain or experimental-validation claim.</p>
 <div class="run-actions"><button id="ip-run">Run strain path</button><button type="button" id="ip-reset" class="secondary">Reset selected preset</button><button type="button" id="ip-import" class="secondary">Import &amp; replay</button><input id="ip-file" type="file" accept=".json,application/json" hidden><button type="button" id="ip-export" class="secondary" disabled>Export complete run</button><p id="ip-status" role="status">Select Lade–Duncan to run a path.</p></div></form>
 <div class="results-column"><section class="experiment-card"><h2>Strain-path response</h2><p id="ip-summary">No current result.</p>
 <svg id="ip-stress" viewBox="0 0 480 290" role="img" aria-label="Signed deviator stress against axial strain"></svg>
 <svg id="ip-volume" viewBox="0 0 480 290" role="img" aria-label="Volumetric strain against axial strain"></svg>
 <svg id="ip-work" viewBox="0 0 480 290" role="img" aria-label="Plastic work against axial strain"></svg>
 <svg id="ip-history" viewBox="0 0 480 290" role="img" aria-label="Physical history maximum against axial strain"></svg>
 <details><summary>Complete stress, strain &amp; history</summary><p>SI units; Mandel shear order xx, yy, zz, √2xy, √2yz, √2xz. H is decoded from the signed carrier. No pore-pressure law or reconstructed pore-pressure curve is supplied.</p><div style="overflow:auto;max-width:100%"><table id="ip-state" style="font-size:11px;white-space:nowrap"></table></div></details>
 <details><summary>Fetched model, review &amp; engine identities</summary><pre id="ip-identities" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
 <p>Measurement overlay unavailable: no rights-cleared, compatible experiment is approved for these two source examples. Curves do not imply calibration or agreement with Wichtmann data.</p></section>
 <details class="experiment-card" id="ip-equations"><summary>Equations, source &amp; approved scope</summary>
 <p>For s=σ/pₐ: f=I₁³/I₃, k₂=A f+27(1−A), ḡ=I₁³−k₂ I₃. Plastic-flow direction is 3I₁²I−k₂ cof(s), differentiating at fixed k₂. E=K_ur pₐ s_minⁿ; a=M pₐ s_minˡ. On new loading, dWᵖ=a df/[1−r_f(f−fₜ)/(k₁−fₜ)]²; unloading is elastic. Positive principal stresses and f&lt;k₁ delimit this pre-failure law.</p>
 <p>Original 1975 formulation with Atlas midpoint-elastic/local Eq. 19 integration and signed-gap history. The 1977 curved-surface extension is supporting context, a different formulation. Hydrostatic/proportional boundary evidence is not a general three-dimensional event theorem.</p>
 <p><a href="https://doi.org/10.1061/AJGEB6.0000204" target="_blank" rel="noopener">Lade &amp; Duncan (1975), pp. 1037–1053</a> · <a href="./engine-implicit-path/review.html">Independent agent review &amp; scope</a> · <a href="./engine-implicit-path/review.json">Nine-item checklist</a> · <a href="./engine-implicit-path/approval.json">Approval &amp; limitations</a> · <a href="./engine-implicit-path/${modelId}.json" download>Download exact model JSON</a></p>
 <p>Approval describes the exact bounded implementation; website qualification is a separate gate. Custom controls do not expand the approved parameter or physical scope.</p></details></div></div>`;
 ordinary.after(panel);if(![...$('model').options].some(o=>o.value===modelId))$('model').append(new Option('Lade–Duncan 1975 · cohesionless soil',modelId));
 $('ip-settings').textContent=JSON.stringify(settings,null,2);
 let active=false,last=null;
 const unit=()=>$('ip-unit').textContent=$('ip-protocol').value==='3'?'Amplitude is signed deviator stress change, Pa.':'Amplitude is dimensionless strain (0.005 = 0.5%).';
 const set=c=>{for(const key of ['parameters','initial'])$('ip-'+key).value=JSON.stringify(c[key],null,2);for(const key of ['protocol','target','steps','cycles'])$('ip-'+key).value=c[key];unit();};
 const read=()=>{const c={version:kind,units:'SI',model:modelId,settings:{...settings}};for(const key of ['parameters','initial'])c[key]=parseRunJSON($('ip-'+key).value);for(const key of ['protocol','target','steps','cycles']){if(!$('ip-'+key).value.trim())throw Error(key+' is required.');c[key]=Number($('ip-'+key).value);}return validateControls(c);};
 function history(p){const s=p.state,scale=Math.max(...s.slice(0,6).map(Math.abs)),v=s.slice(0,6).map(x=>x/scale),[a,b,c,d,e,f]=v;const det=a*b*c+2*d*e*f/(2*Math.SQRT2)-(a*e*e+b*f*f+c*d*d)/2;return Math.max(Number(parseRunJSON($('ip-parameters').value)[2]),(a+b+c)**3/det+Math.max(s[6],0));}
 function render(result,identity=null,partial=false){
  const points=result.points;if(!points.length){$('ip-summary').textContent='No increment committed.';return;}const end=points.at(-1);
  chart('ip-stress','Axial strain (%)','Signed deviator stress (kPa)',points.map(p=>[p.strain[0]*100,p.q_signed/1000]));
  chart('ip-volume','Axial strain (%)','Volumetric strain (%)',points.map(p=>[p.strain[0]*100,(p.strain[0]+p.strain[1]+p.strain[2])*100]));
  chart('ip-work','Axial strain (%)','Plastic work (Pa)',points.map(p=>[p.strain[0]*100,p.state[7]]));
  chart('ip-history','Axial strain (%)','History maximum H (1)',points.map(p=>[p.strain[0]*100,history(p)]));
  $('ip-summary').textContent=`${partial?'Committed prefix · ':''}${points.length-1} increments; final axial strain ${(end.strain[0]*100).toPrecision(6)}%; signed q ${(end.q_signed/1000).toPrecision(6)} kPa; Wᵖ ${end.state[7].toPrecision(6)} Pa.`;
  const table=$('ip-state');table.replaceChildren();const heading=document.createElement('tr');for(const label of ['control',...['xx','yy','zz','√2xy','√2yz','√2xz'].map(x=>'σ '+x+' (Pa)'),...['xx','yy','zz','√2xy','√2yz','√2xz'].map(x=>'ε '+x),'gap (1)','H (1)','Wᵖ (Pa)']){const cell=document.createElement('th');cell.textContent=label;heading.append(cell);}table.append(heading);
  for(const p of points){const row=document.createElement('tr');for(const x of [p.control,...p.state.slice(0,6),...p.strain,p.state[6],history(p),p.state[7]]){const cell=document.createElement('td');cell.textContent=Number(x.toPrecision(9));row.append(cell);}table.append(row);}
  $('ip-identities').textContent=identity?JSON.stringify(identity,null,2):'Failed run: committed prefix only.';
 }
 const clear=()=>{for(const id of ['ip-stress','ip-volume','ip-work','ip-history','ip-state'])$(id).replaceChildren();$('ip-summary').textContent='No current result.';$('ip-identities').textContent='';};
 const runner=createImplicitPathRunner({createWorker,notify:event=>{last=event.run||null;$('ip-status').textContent=event.message;$('ip-run').disabled=event.state==='running';$('ip-export').disabled=!last;if(last)render(last.result,last.provenance);else if(event.partial)render(event.partial,null,true);else clear();}});
 function run(event,expected=null){event?.preventDefault();if(!active)return;let c;try{c=read();}catch(error){runner.cancel('Invalid input: '+error.message);return;}runner.run(c,{expected});}
 set(preset());$('ip-controls').onsubmit=run;
 $('ip-controls').addEventListener('input',e=>{if(!['ip-file','ip-preset'].includes(e.target.id)){runner.cancel();unit();}});
 $('ip-preset').onchange=()=>{runner.cancel();set(preset($('ip-preset').value));};
 $('ip-reset').onclick=()=>{runner.cancel();set(preset($('ip-preset').value));run();};
 $('ip-import').onclick=()=>$('ip-file').click();
 $('ip-file').onchange=async()=>{runner.cancel('Reading imported path…');const generation=runner.generation;try{const file=$('ip-file').files[0];$('ip-file').value='';if(!file)return;if(file.size>10*1024*1024)throw Error('Import exceeds 10 MB.');const text=await file.text(),response=await fetch(new URL('./engine-implicit-path/identity.json',import.meta.url),{cache:'no-store'});if(!response.ok)throw Error('Package identity unavailable.');const imported=parseRunJSON(text),value=importRun(text,parseRunJSON(await response.text()));if(generation!==runner.generation||!active)return;set(value.controls);run(null,imported);}catch(error){if(generation===runner.generation)runner.cancel('Import rejected: '+error.message);}};
 $('ip-export').onclick=()=>{if(!last)return;const url=URL.createObjectURL(new Blob([stringifyRun(last)+'\n'],{type:'application/json'})),link=document.createElement('a');link.href=url;link.download='lade-duncan-1975-run.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 return {modelId,get active(){return active;},run,select(id,{auto=true}={}){runner.cancel();active=id===modelId;panel.hidden=!active;ordinary.hidden=active;if(links)links.hidden=active;if(active){cancelOrdinary();if(auto)run();}return active;},showEquations(){if(!active)return false;$('ip-equations').open=true;$('ip-equations').scrollIntoView();return true;}};
}
