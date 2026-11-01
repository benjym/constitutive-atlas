import {MODEL,MODEL_SHA256,preset,parseNumbers,parsePath,validateRequest,validateIdentity,runPath,replayRequest,parseRunJSON,verifyReplay} from './orthotropic-contract.mjs';
// Dedicated material-point interface mounted in the main laboratory. No global control IDs.
export function setupOrthotropicLaboratory({cancelOrdinary=()=>{}}={}){
 const ordinary=document.querySelector('#laboratory > .lab-layout');
 if(!ordinary)throw Error('Main laboratory layout is unavailable.');
 if(document.getElementById('orthotropic-material-laboratory'))throw Error('Orthotropic laboratory is already mounted.');
 const panel=document.createElement('section');panel.id='orthotropic-material-laboratory';panel.hidden=true;panel.setAttribute('aria-label','Orthotropic strain-increment laboratory');
 const root=panel.attachShadow({mode:'open'});
 root.innerHTML=`<style>
  :host{font:16px/1.5 system-ui,sans-serif;color:#19312c;background:#f3f5f1}
  *{box-sizing:border-box}
  header{display:flex;gap:24px;justify-content:space-between;align-items:start;margin-bottom:28px}
  h1{font-size:34px;letter-spacing:-1px;margin:3px 0 8px}h2{font-size:16px;margin:0 0 14px}
  p{margin:6px 0}a{color:#17644b}.eyebrow{font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#547168}
  .badge{display:inline-block;border:1px solid #d4c58b;color:#745c1c;background:#fff8df;padding:5px 12px;border-radius:20px;font-size:12px;white-space:nowrap}
  .layout{display:grid;grid-template-columns:315px 1fr;gap:22px}.card{background:#fff;border:1px solid #dce4dd;border-radius:14px;padding:23px}
  label{display:block;font-size:13px;color:#466057;margin:12px 0 5px}input,select,button{width:100%;font:inherit;padding:9px 10px;border:1px solid #c9d6cc;border-radius:6px;background:white;color:inherit}
  input:focus,select:focus,button:focus{outline:3px solid #b4dcc9;outline-offset:1px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  button{background:#18563f;color:white;border:0;font-weight:600;cursor:pointer;margin-top:18px}button:disabled{opacity:.45;cursor:wait}
  button.secondary{background:#eef4ef;color:#18563f;margin-top:10px}.subtle{color:#64766f;font-size:13px}.error{color:#943228}
  .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:22px}.stat{background:#edf4ef;border-radius:8px;padding:13px}.stat strong{font-size:23px;display:block;letter-spacing:-.5px}.stat span{font-size:12px;color:#557064}
  svg{width:100%;height:auto;display:block}.chart{margin-top:14px}.chart+h2{margin-top:24px}.plot-note{display:flex;justify-content:space-between;gap:12px;font-size:12px;color:#63776e}
  details{margin-top:16px;border-top:1px solid #e3e9e4;padding-top:14px}summary{font-size:13px;cursor:pointer}footer{margin:22px 0;font-size:12px;color:#67766e}
  @media(max-width:800px){.layout{grid-template-columns:1fr}header{flex-direction:column;gap:8px}.stats{gap:6px}.stat{padding:10px}.stat strong{font-size:19px}}

textarea{width:100%;font:13px/1.6 ui-monospace,monospace;padding:9px;border:1px solid #c9d6cc;border-radius:6px;color:inherit;resize:vertical} .layout{grid-template-columns:340px minmax(0,1fr)}.card{min-width:0} code{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font:12px/1.6 ui-monospace,monospace}th,td{padding:6px;text-align:right;border-bottom:1px solid #e3e9e4;white-space:nowrap}.scroll{overflow:auto} .legend{font-size:12px;color:#557064} .stats{grid-template-columns:1fr 1fr} .scope{margin:20px 0;padding:14px 18px;border-left:3px solid #b7a55a;background:#faf7eb;font-size:13px} @media(max-width:800px){.layout{grid-template-columns:1fr}}

.parameter-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}.scope{line-height:1.6}.stats{grid-template-columns:1fr 1fr}.stat strong{font-size:21px}.actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}.full{grid-column:1/-1}pre{white-space:pre-wrap;overflow-wrap:anywhere}button{min-height:44px}summary{min-height:32px}.danger{color:#943228}.table-note{font-size:12px}.layout{grid-template-columns:370px minmax(0,1fr)}@media(max-width:850px){.layout{grid-template-columns:1fr}}

:host{display:block}:host([hidden]){display:none}footer{padding-bottom:1rem}.scope{margin-top:0}.card{min-width:0}h3{font-size:17px}.equation{padding:18px;background:#fff;border:1px solid #dce4dd;border-radius:10px;margin-top:18px}
</style><div class="scope"><b>Scope of evidence.</b> Complete nine-constant orthotropic linear elasticity, constant material parameters and infinitesimal strain, dry total Cauchy stress. Material axes 1,2,3 remain aligned with Cartesian x,y,z; rotating or evolving material axes are unsupported. Compression-positive stress and strain, Mandel shear components. The named preset is illustrative; custom parameters and starting stresses are exploratory. No physical clock, stress control, thermal strain, pore pressure, damage or plastic history. No experimental calibration or validation.</div>
<div class="layout"><form id="controls" class="card"><h2>All six strain increments</h2><p class="subtle">Mandel order: xx, yy, zz, √2xy, √2yz, √2xz. Compression positive; SI units. Each run starts from the complete initial state below.</p>
<div class="parameter-grid"><div><label for="E1">E1 (Pa)</label><input id="E1" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="E2">E2 (Pa)</label><input id="E2" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="E3">E3 (Pa)</label><input id="E3" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="G12">G12 (Pa)</label><input id="G12" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="G23">G23 (Pa)</label><input id="G23" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="G13">G13 (Pa)</label><input id="G13" type="number" min="1" max="1000000000000.0" step="any" required></div><div><label for="nu12">nu12 (dimensionless)</label><input id="nu12" type="number" min="-10" max="10" step="any" required></div><div><label for="nu23">nu23 (dimensionless)</label><input id="nu23" type="number" min="-10" max="10" step="any" required></div><div><label for="nu13">nu13 (dimensionless)</label><input id="nu13" type="number" min="-10" max="10" step="any" required></div></div>
<p class="subtle">E1,E2,E3 are axial Young moduli; G12,G23,G13 are shear moduli. νij is minus transverse j strain divided by axial i strain under uniaxial stress in i. Reciprocal ratios are determined by symmetry. Coupled compliance must be positive definite. Machine bounds do not establish physical calibration or numerical qualification across that range. E1 also scales numerical residuals.</p>
<label for="initial">Explicit initial full stress state · six numbers</label><textarea id="initial" rows="3" spellcheck="false" required aria-describedby="stateHelp"></textarea><p class="subtle" id="stateHelp">σxx, σyy, σzz, √2σxy, √2σyz, √2σxz (Pa). All six entries are persistent total Cauchy stress; no additional history variables are required. Starting stress need not be zero.</p>
<label for="increments">Strain increment path · six numbers per row</label><textarea id="increments" rows="7" spellcheck="false" required></textarea><p class="subtle">1–200 rows. The preset loads, reverses, then holds. All six components are prescribed; a zero row is a strain hold without elapsed time. Rows commit sequentially. A failed row preserves the accepted prefix.</p>
<details><summary>Frozen numerical settings</summary><p class="subtle">Residual tolerance 10⁻¹¹; rate tolerance 10⁻⁶; 60 iterations; depth 0; one substep; 20 backtracks. No internal subdivision. The elastic law is path independent at fixed constants; these settings are numerical choices.</p></details>
<button id="run">Run increment path</button><div class="actions"><button id="resetPreset" type="button" class="secondary">Reset named preset</button><button id="download" type="button" class="secondary" disabled>Export request &amp; result</button></div>
<label for="import">Import exported JSON &amp; replay</label><input id="import" type="file" accept=".json,application/json"><p id="status" role="status" class="subtle">Checking exact packaged identities…</p></form>
<section class="card" aria-label="Simulation results"><div class="stats"><div class="stat"><span>Committed increment rows</span><strong id="stepValue">—</strong></div><div class="stat"><span>Final σxx · total stress</span><strong id="stressValue">—</strong></div></div>
<label for="component">Plot component · Mandel</label><select id="component"><option>xx</option><option>yy</option><option>zz</option><option>√2xy</option><option>√2yz</option><option>√2xz</option></select>
<h2>Total Cauchy stress</h2><div class="plot-note"><span>Compression positive (kPa)</span><span>Committed row →</span></div><svg id="stressChart" viewBox="0 0 720 230" role="img" aria-label="Selected total stress against committed row"></svg>
<h2>Cumulative applied strain</h2><div class="plot-note"><span>Increment sum (%)</span><span>Committed row →</span></div><svg id="strainChart" viewBox="0 0 720 230" role="img" aria-label="Selected cumulative strain increment against row"></svg>
<p id="description" class="subtle">Run the named preset or supply an exploratory loading path.</p><p class="subtle">Cumulative strain is the sum applied from the supplied starting stress; it is a relative strain, not a reconstruction of the starting deformation. Experimental overlays unavailable: no compatible calibration or source experiment is supplied. Curves are model responses.</p>
<details id="stateDetails" open><summary>Complete state at every accepted row</summary><p class="table-note subtle">All six persistent stress state entries are shown and exported in Pa. The complete strain-increment history is included in every export.</p><div class="scroll"><table id="stateTable"></table></div></details>
<details><summary>Exact model, engine and approval identities</summary><pre id="identity" style="font-size:11px"></pre><p class="subtle">Model, module, Wasm, catalogue, approval and review file hashes are verified before use. Every result must echo its exact request, catalogue and numerical settings.</p></details>
</section></div>
<details id="equations" class="equation"><summary>Orthotropic equations, source conventions and integration</summary><p>σₙ₊₁ = σₙ + C Δε, C = S⁻¹. The normal compliance block has diagonal (1/E1, 1/E2, 1/E3) and symmetric off-diagonals S12 = −ν12/E1, S13 = −ν13/E1, S23 = −ν23/E2. Mandel shear compliance is diagonal (1/(2G12), 1/(2G23), 1/(2G13)). All remaining entries vanish. Positive-definite compliance is required.</p><p>The source uses tension-positive Kelvin components. Simultaneously reversing stress and strain yields this compression-positive convention without changing C. The fixed material axes are aligned with x,y,z. The strain-increment map uses the common declarative engine; all six stress components commit on a successful row, while a failed row rolls back to the incoming state. Zero increment holds stress. There is no physical time or finite-rotation transport.</p></details><footer>Source: <a href="https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.cpp" target="_blank" rel="noreferrer">Pinned OpenGeoSys constitutive implementation</a> · <a href="https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.h" target="_blank" rel="noreferrer">Parameter definitions and reciprocity</a> · <a href="material-point-orthotropic/review.html">Independent review &amp; limitations</a> · <a href="material-point-orthotropic/approval.json">Approval record</a> · <a href="material-point-orthotropic/review.json">Review checklist</a> · <a href="material-point-orthotropic/model.json">Exact approved model</a> · <a href="#catalogue">Atlas catalogue</a></footer>`;
 ordinary.after(panel);
 document.getElementById('model').append(new Option('Orthotropic elasticity · nine constants',MODEL));
const $=id=>root.getElementById(id),form=$('controls'),PARAMS=['E1','E2','E3','G12','G23','G13','nu12','nu23','nu13'];
let identity,lastResult,token=0,active=false,worker=null,cancelWorker=null;
function fill(r){PARAMS.forEach((name,i)=>$(name).value=r.parameters[i]);$('initial').value=r.initial.join(',');$('increments').value=r.increments.map(row=>row.join(',')).join('\n');}
function request(){return validateRequest({model:MODEL,parameters:PARAMS.map(name=>{if($(name).value.trim()==='')throw Error('Every parameter is required.');return Number($(name).value);}),initial:parseNumbers($('initial').value,6,'Initial stress'),settings:preset().settings,increments:parsePath($('increments').value)});}
function invalidate(){token++;if(cancelWorker){cancelWorker(Error('Superseded inputs.'));cancelWorker=null;}if(worker){worker.terminate();worker=null;}lastResult=null;$('download').disabled=true;for(const id of ['stepValue','stressValue'])$(id).textContent='—';for(const id of ['stressChart','strainChart','stateTable'])$(id).replaceChildren();$('description').textContent='Run the current inputs to inspect their response.';}
function fail(error){$('status').className='subtle error';$('status').textContent=error.message;}
function plot(id,points,value,color){
 const svg=$(id),ns='http://www.w3.org/2000/svg',w=720,h=230,left=75,right=15,top=18,bottom=32;svg.replaceChildren();
 const ys=points.map(value),end=Math.max(1,points.at(-1).step);let lo=Math.min(...ys),hi=Math.max(...ys),pad=Math.max((hi-lo)*.12,Math.abs(hi)*.05,1e-7);lo-=pad;hi+=pad;
 const x=t=>left+t/end*(w-left-right),y=v=>h-bottom-(v-lo)/(hi-lo)*(h-top-bottom);
 const add=(tag,attrs,text)=>{const el=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;svg.append(el);};
 for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4;add('line',{x1:left,x2:w-right,y1:y(v),y2:y(v),stroke:'#e4eae5'});add('text',{x:left-8,y:y(v)+4,'text-anchor':'end','font-size':11,fill:'#6b7a71'},Number(v.toPrecision(3)));add('text',{x:x(end*i/4),y:h-10,'text-anchor':'middle','font-size':11,fill:'#6b7a71'},Number((end*i/4).toPrecision(3)));}
 add('polyline',{points:points.map((p,i)=>`${x(p.step)},${y(ys[i])}`).join(' '),fill:'none',stroke:color,'stroke-width':2.5,'stroke-linejoin':'round'});
}
function render(){if(!lastResult)return;const end=lastResult.points.at(-1),i=$('component').selectedIndex;
 $('stepValue').textContent=`${end.step} / ${lastResult.request.increments.length}`;$('stressValue').textContent=`${(end.state[0]/1000).toPrecision(5)} kPa`;
 plot('stressChart',lastResult.points,p=>p.state[i]/1000,'#246647');plot('strainChart',lastResult.points,p=>p.strain[i]*100,'#b07839');
 const table=$('stateTable');table.replaceChildren();const header=document.createElement('tr');for(const label of ['row','σxx','σyy','σzz','√2σxy','√2σyz','√2σxz']){const th=document.createElement('th');th.textContent=label;header.append(th);}table.append(header);
 for(const point of lastResult.points){const tr=document.createElement('tr');for(const value of [point.step,...point.state]){const td=document.createElement('td');td.textContent=Number(value.toPrecision(8));tr.append(td);}table.append(tr);}
 $('description').textContent=lastResult.ok?'All rows committed. Every plotted point is a complete elastic stress update.':`Stopped at row ${lastResult.failedRow}; displaying only the ${end.step} accepted rows. The failed row did not commit. ${lastResult.message}`;
}
// A dedicated worker per run can be terminated even while the solver is busy.
function workerMain(base){
 self.onmessage=async({data:{id,input,saved}})=>{
  try{
   const contract=await import(new URL('orthotropic-contract.mjs',base));
   const sha=async b=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
   const fetchBytes=async p=>{const r=await fetch(new URL(p,base));if(!r.ok)throw Error('Asset unavailable: '+p);return r.arrayBuffer();};
   const decode=b=>contract.parseRunJSON(new TextDecoder().decode(b)),prefix='material-point-orthotropic/';
   const manifest=decode(await fetchBytes(prefix+'package-manifest.json'));
   if(!manifest||Array.isArray(manifest)||typeof manifest!=='object')throw Error('Package manifest unavailable.');
   const entries=new Map();
   for(const [p,h]of Object.entries(manifest)){
    if(!/^[a-zA-Z0-9._/-]+$/.test(p)||p.startsWith('/')||p.split('/').some(v=>v==='..'||v==='.')||!/^([a-f0-9]{64})$/.test(h))throw Error('Invalid package asset path or digest.');
    const b=await fetchBytes(p);if(await sha(b)!==h)throw Error('Package asset identity mismatch: '+p);entries.set(p,b);
   }
   for(const p of ['orthotropic-contract.mjs','orthotropic-laboratory.mjs',...['orthotropic.js','orthotropic.wasm','models.json','model.json','identity.json','approval.json','review.json','review.html'].map(v=>prefix+v)])if(!entries.has(p))throw Error('Package manifest missing '+p);
   const identity=contract.validateIdentity(decode(entries.get(prefix+'identity.json')));
   for(const [p,k]of [['orthotropic.js','module_sha256'],['orthotropic.wasm','wasm_sha256'],['model.json','model_sha256'],['models.json','catalogue_sha256'],['approval.json','approval_sha256'],['review.json','review_sha256'],['review.html','review_html_sha256']])if(await sha(entries.get(prefix+p))!==identity[k])throw Error('Exact identity mismatch: '+p);
   const catalogue=decode(entries.get(prefix+'models.json')),approval=decode(entries.get(prefix+'approval.json')),review=decode(entries.get(prefix+'review.json'));
   if(catalogue.sha256!==identity.catalogue_hash||catalogue.models?.length!==1||catalogue.models[0].id!==contract.MODEL||approval.status!=='approved'||approval.definition?.sha256!==contract.MODEL_SHA256||review.status!=='accepted'||review.model?.sha256!==contract.MODEL_SHA256)throw Error('Catalogue/review/approval binding mismatch.');
   const moduleURL=URL.createObjectURL(new Blob([entries.get(prefix+'orthotropic.js')],{type:'text/javascript'}));let engine;
   try{const {default:create}=await import(moduleURL),compiled=await WebAssembly.compile(entries.get(prefix+'orthotropic.wasm'));engine=await create({instantiateWasm(imports,receive){const instance=new WebAssembly.Instance(compiled,imports);receive(instance);return instance.exports;}});}finally{URL.revokeObjectURL(moduleURL);}
   const descriptor=contract.parseRunJSON(engine.ccall('atlas_describe','string',[],[]));if(descriptor.sha256!==identity.catalogue_hash||JSON.stringify(descriptor.models)!==JSON.stringify(catalogue.models))throw Error('Loaded engine catalogue mismatch.');
   const request=saved?contract.replayRequest(saved,identity):input;
   const result=await contract.runPath(w=>contract.parseRunJSON(engine.ccall(w.function,'string',w.types,w.args)),request,identity);
   if(saved)contract.verifyReplay(result,saved);
   self.postMessage({id,result,identity});
  }catch(error){self.postMessage({id,error:error.message});}
 };
}
function execute(input,saved,id){
 const url=URL.createObjectURL(new Blob(['('+workerMain.toString()+')('+JSON.stringify(new URL('.',import.meta.url).href)+');'],{type:'text/javascript'}));
 worker=new Worker(url,{type:'module'});URL.revokeObjectURL(url);
 return new Promise((resolve,reject)=>{cancelWorker=reject;worker.onmessage=({data})=>{if(data.id!==id)return;data.error?reject(Error(data.error)):resolve(data);};worker.onerror=event=>reject(Error(event.message||'Worker failed.'));worker.postMessage({id,input,saved});});
}
async function run(event,saved=null){event?.preventDefault();if(!active)return;invalidate();const mine=token;try{const r=request();$('status').className='subtle';$('status').textContent='Verifying package and running increment path…';
 const data=await execute(r,saved,mine);if(mine!==token||!active)return;identity=validateIdentity(data.identity);lastResult=data.result;$('identity').textContent=JSON.stringify(identity,null,2);render();$('download').disabled=false;$('status').className=lastResult.ok?'subtle':'subtle error';$('status').textContent=lastResult.ok?`Completed ${lastResult.points.length-1} increment rows.${saved?' Complete saved document matched fresh replay.':''}`:`Row ${lastResult.failedRow} failed: ${lastResult.message}. Accepted prefix retained; edit inputs or reset to recover.`;
 }catch(error){if(mine===token&&active)fail(error);}finally{if(mine===token&&worker){worker.terminate();worker=null;cancelWorker=null;}}}
form.addEventListener('submit',run);form.addEventListener('input',event=>{if(event.target.id==='import')return;invalidate();$('status').className='subtle';$('status').textContent='Inputs changed. Run to update the response.';});$('component').addEventListener('change',render);
$('resetPreset').addEventListener('click',()=>{fill(preset());run();});
$('download').addEventListener('click',()=>{if(!lastResult)return;const url=URL.createObjectURL(new Blob([JSON.stringify(lastResult,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='orthotropic-strain-path.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('import').addEventListener('change',async()=>{invalidate();const mine=token;try{const file=$('import').files[0];if(!file)return;if(file.size>5e6)throw Error('Replay file too large.');const data=parseRunJSON(await file.text());if(mine!==token||!active)return;if(!identity)throw Error('Run this package once before importing.');const r=replayRequest(data,identity);fill(r);$('import').value='';await run(null,data);}catch(error){if(mine===token&&active)fail(error);}finally{$('import').value='';}});
fill(preset());

 function select(id,{auto=true}={}){
  const next=id===MODEL,changed=next!==active;active=next;panel.hidden=!next;
  const links=document.querySelector('#laboratory > .workspace-links'),importButton=document.getElementById('import-run');
  if(!next){if(changed){invalidate();ordinary.hidden=false;if(links)links.hidden=false;if(importButton)importButton.hidden=false;}return false;}
  ordinary.hidden=true;if(links)links.hidden=true;if(importButton)importButton.hidden=true;
  cancelOrdinary();document.getElementById('model').value=MODEL;
  if(changed&&auto)run();return true;
 }
 return {modelId:MODEL,get active(){return active;},select,run,showEquations(){if(!active)return false;$('equations').open=true;$('equations').scrollIntoView({behavior:'smooth',block:'start'});return true;}};
}
