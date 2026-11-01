import {MODEL,MODEL_SHA256,preset,parseNumbers,parsePath,validateRequest,validateIdentity,runPath,replayRequest} from './j2-contract.mjs';
// Dedicated material-point interface mounted in the main laboratory. No global control IDs.
export function setupJ2Laboratory({cancelOrdinary=()=>{}}={}){
 const ordinary=document.querySelector('#laboratory > .lab-layout');
 if(!ordinary)throw Error('Main laboratory layout is unavailable.');
 if(document.getElementById('j2-material-laboratory'))throw Error('J2 laboratory is already mounted.');
 const panel=document.createElement('section');panel.id='j2-material-laboratory';panel.hidden=true;panel.setAttribute('aria-label','J2 strain-increment laboratory');
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
</style><div class="scope"><b>Scope of evidence.</b> Dry total Cauchy stress, infinitesimal strain, fixed spatial components and zero spin. The named preset uses independently checked material-point parameters. Custom parameters, starting histories and loading paths are exploratory. Each row defines one backward-Euler map; adding rows can change a nonproportional response. No physical clock, stress control, pore pressure or finite-rotation transport. No experimental calibration or validation.</div>
<div class="layout"><form id="controls" class="card"><h2>All six strain increments</h2><p class="subtle">Mandel order: xx, yy, zz, √2xy, √2yz, √2xz. Compression positive; SI units. Each run starts from the complete initial state below.</p>
<div class="parameter-grid"><div><label for="p_ref">Reference scale p_ref (Pa)</label><input id="p_ref" type="number" min="1" max="1e15" step="any" required></div><div><label for="K">Bulk modulus K (Pa)</label><input id="K" type="number" min="1" max="1e15" step="any" required></div><div><label for="G">Shear modulus G (Pa)</label><input id="G" type="number" min="1" max="1e15" step="any" required></div><div><label for="sigma_y">Initial yield σy (Pa)</label><input id="sigma_y" type="number" min="1" max="1e13" step="any" required></div><div class="full"><label for="H">Isotropic hardening H (Pa; zero allowed)</label><input id="H" type="number" min="0" max="1e15" step="any" required></div></div>
<p class="subtle">p_ref scales numerical residuals; it is not a material modulus. Machine parameter bounds do not establish physical calibration or numerical qualification across that range.</p>
<label for="initial">Explicit initial full state · eight numbers</label><textarea id="initial" rows="3" spellcheck="false" required aria-describedby="stateHelp"></textarea><p class="subtle" id="stateHelp">σxx, σyy, σzz, √2σxy, √2σyz, √2σxz (Pa), α, γ. α is persistent equivalent plastic strain ≥ 0; initial stress must be yield-admissible. γ is temporary and must start at zero; it resets at each solve.</p>
<label for="increments">Strain increment path · six numbers per row</label><textarea id="increments" rows="7" spellcheck="false" required></textarea><p class="subtle">1–200 rows. The preset loads, reverses, then holds. All six components are prescribed; a zero row is a strain hold without elapsed time. Rows commit sequentially. A failed row preserves the accepted prefix.</p>
<details><summary>Frozen numerical settings</summary><p class="subtle">Residual tolerance 10⁻¹¹; rate tolerance 10⁻⁶; 60 iterations; depth 0; one substep; 20 backtracks. No internal subdivision. These numerical choices do not qualify continuous curved-path accuracy.</p></details>
<button id="run" disabled>Loading engine…</button><div class="actions"><button id="resetPreset" type="button" class="secondary">Reset named preset</button><button id="download" type="button" class="secondary" disabled>Export request &amp; result</button></div>
<label for="import">Import exported JSON &amp; replay</label><input id="import" type="file" accept=".json,application/json"><p id="status" role="status" class="subtle">Checking exact packaged identities…</p></form>
<section class="card" aria-label="Simulation results"><div class="stats"><div class="stat"><span>Committed increment rows</span><strong id="stepValue">—</strong></div><div class="stat"><span>Final σxx · total stress</span><strong id="stressValue">—</strong></div><div class="stat"><span>Equivalent plastic strain α</span><strong id="alphaValue">—</strong></div><div class="stat"><span>Last temporary increment γ</span><strong id="gammaValue">—</strong></div></div>
<label for="component">Plot component · Mandel</label><select id="component"><option>xx</option><option>yy</option><option>zz</option><option>√2xy</option><option>√2yz</option><option>√2xz</option></select>
<h2>Total Cauchy stress</h2><div class="plot-note"><span>Compression positive (kPa)</span><span>Committed row →</span></div><svg id="stressChart" viewBox="0 0 720 230" role="img" aria-label="Selected total stress against committed row"></svg>
<h2>Cumulative applied strain</h2><div class="plot-note"><span>Increment sum (%)</span><span>Committed row →</span></div><svg id="strainChart" viewBox="0 0 720 230" role="img" aria-label="Selected cumulative strain increment against row"></svg>
<p id="description" class="subtle">Run the named preset or supply an exploratory loading path.</p><p class="subtle">Cumulative strain is the sum applied from the supplied starting state. It does not reconstruct that state's total or plastic strain. Experimental overlays unavailable: no compatible calibration or source experiment is supplied. Curves are model responses.</p>
<details id="stateDetails" open><summary>Complete state at every accepted row</summary><p class="table-note subtle">All eight state entries are shown and exported. Stress is Pa; α and γ are dimensionless. γ records only the latest solve and is not accumulated history.</p><div class="scroll"><table id="stateTable"></table></div></details>
<details><summary>Exact model, engine and approval identities</summary><pre id="identity" style="font-size:11px"></pre><p class="subtle">Model, module, Wasm, catalogue, approval and review file hashes are verified before use. Every result must echo its exact request, catalogue and numerical settings.</p></details>
</section></div>
<details id="equations" class="equation"><summary>J2 equations, source conventions and integration</summary><p>s = dev(σ); q = √(3s:s/2); Y = σy + Hα. Trial stress is σtrial = σn + K tr(Δε)I + 2G dev(Δε). For a plastic step, Δα = (qtrial − σy − Hαn)/(3G + H), α = αn + Δα and σ = σtrial − 3G Δα strial/qtrial. Elastic steps have Δα = 0. The residual uses signed trial consistency to exclude reversed radial roots.</p><p>γ stores Δα only for the latest internal solve. All six components use Mandel order and compression-positive signs; this is a fixed-frame infinitesimal-strain total-stress map, without physical time or finite rotations. The exact source specialization uses sigInf=sig0 and η=0. The mathematical return omits the vendor multiplier shrink.</p></details><footer>Source: <a href="https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/J2Plasticity.html" target="_blank" rel="noreferrer">OpenSees J2Plasticity theory</a> · <a href="https://github.com/OpenSees/OpenSees/blob/955ceb0a55f7b5764856ea82fc9a9cc7f07a1eea/SRC/material/nD/J2Plasticity.cpp" target="_blank" rel="noreferrer">Pinned primary implementation equations</a>. Linear specialization sigInf=sig0, η=0; source multiplier converted to equivalent plastic strain. The mathematical return omits the vendor's small multiplier shrink. The rejected v1 remains historical evidence. <a href="material-point-j2/law-review.html">Independent v2 law review &amp; limitations</a> · <a href="material-point-j2/delivery-review.html">Browser delivery evidence &amp; separate interface review</a> · <a href="material-point-j2/approval.json">Approval record</a> · <a href="material-point-j2/review.json">Review checklist</a> · <a href="material-point-j2/j2-linear-isotropic-hardening-be.json">Exact approved model</a> · <a href="#catalogue">Atlas catalogue</a></footer>`;
 ordinary.after(panel);
 document.getElementById('model').append(new Option('J2 · all-six strain increments',MODEL));
const $=id=>root.getElementById(id),form=$('controls'),PARAMS=['p_ref','K','G','sigma_y','H'];
let engine,identity,lastResult,token=0,active=false,initialization=null;
function fill(r){PARAMS.forEach((name,i)=>$(name).value=r.parameters[i]);$('initial').value=r.initial.join(',');$('increments').value=r.increments.map(row=>row.join(',')).join('\n');}
function request(){return validateRequest({model:MODEL,parameters:PARAMS.map(name=>{if($(name).value.trim()==='')throw Error('Every parameter is required.');return Number($(name).value);}),initial:parseNumbers($('initial').value,8,'Initial state'),settings:preset().settings,increments:parsePath($('increments').value)});}
function invalidate(){token++;lastResult=null;$('download').disabled=true;for(const id of ['stepValue','stressValue','alphaValue','gammaValue'])$(id).textContent='—';for(const id of ['stressChart','strainChart','stateTable'])$(id).replaceChildren();$('description').textContent='Run the current inputs to inspect their response.';}
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
 $('stepValue').textContent=`${end.step} / ${lastResult.request.increments.length}`;$('stressValue').textContent=`${(end.state[0]/1000).toPrecision(5)} kPa`;$('alphaValue').textContent=end.state[6].toPrecision(5);$('gammaValue').textContent=end.state[7].toPrecision(5);
 plot('stressChart',lastResult.points,p=>p.state[i]/1000,'#246647');plot('strainChart',lastResult.points,p=>p.strain[i]*100,'#b07839');
 const table=$('stateTable');table.replaceChildren();const header=document.createElement('tr');for(const label of ['row','σxx','σyy','σzz','√2σxy','√2σyz','√2σxz','α','γ']){const th=document.createElement('th');th.textContent=label;header.append(th);}table.append(header);
 for(const point of lastResult.points){const tr=document.createElement('tr');for(const value of [point.step,...point.state]){const td=document.createElement('td');td.textContent=Number(value.toPrecision(8));tr.append(td);}table.append(tr);}
 $('description').textContent=lastResult.ok?'All rows committed. Every plotted point is one complete backward-Euler update.':`Stopped at row ${lastResult.failedRow}; displaying only the ${end.step} accepted rows. The failed row did not commit. ${lastResult.message}`;
}
async function run(event){event?.preventDefault();if(!active)return;invalidate();const mine=token;try{const r=request();if(!engine)throw Error('Engine is not ready.');$('status').className='subtle';$('status').textContent='Running increment path…';
 const result=await runPath(w=>JSON.parse(engine.ccall(w.function,'string',w.types,w.args)),r,identity,{beforeStep:async()=>{await new Promise(resolve=>setTimeout(resolve,0));if(mine!==token||!active)throw Error('Superseded inputs.');}});
 if(mine!==token||!active)return;lastResult=result;render();$('download').disabled=false;$('status').className=result.ok?'subtle':'subtle error';$('status').textContent=result.ok?`Completed ${result.points.length-1} increment rows.`:`Row ${result.failedRow} failed: ${result.message}. Accepted prefix retained; edit inputs or reset to recover.`;
 }catch(error){if(mine===token)fail(error);}}
form.addEventListener('submit',run);form.addEventListener('input',event=>{if(event.target.id==='import')return;invalidate();$('status').className='subtle';$('status').textContent='Inputs changed. Run to update the response.';});$('component').addEventListener('change',render);
$('resetPreset').addEventListener('click',()=>{fill(preset());run();});
$('download').addEventListener('click',()=>{if(!lastResult)return;const url=URL.createObjectURL(new Blob([JSON.stringify(lastResult,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='j2-strain-path.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('import').addEventListener('change',async()=>{invalidate();const mine=token;try{const file=$('import').files[0];if(!file)return;if(file.size>5e6)throw Error('Replay file too large.');const data=JSON.parse(await file.text());if(mine!==token)return;const r=replayRequest(data,identity);fill(r);await run();}catch(error){if(mine===token)fail(error);}finally{$('import').value='';}});
fill(preset());
const digest=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
async function checked(url,expected){const response=await fetch(url);if(!response.ok)throw Error(`Cannot load ${url}`);const bytes=await response.arrayBuffer();if(await digest(bytes)!==expected)throw Error(`File identity mismatch: ${url}`);return bytes;}
async function loadEngine(){
 const response=await fetch(new URL('./material-point-j2/identity.json',import.meta.url));if(!response.ok)throw Error('Package identity unavailable.');identity=validateIdentity(await response.json());
 const entries=[['./material-point-j2/j2.js','module_sha256'],['./material-point-j2/j2.wasm','wasm_sha256'],['./material-point-j2/'+MODEL+'.json','model_sha256'],['./material-point-j2/models.json','catalogue_sha256'],['./material-point-j2/approval.json','approval_sha256'],['./material-point-j2/review.json','review_sha256']];
 const bytes=await Promise.all(entries.map(([url,key])=>checked(new URL(url,import.meta.url),identity[key]))),decode=b=>JSON.parse(new TextDecoder().decode(b));
 const catalogue=decode(bytes[3]),approval=decode(bytes[4]),review=decode(bytes[5]);if(catalogue.sha256!==identity.catalogue_hash||catalogue.models?.length!==1||catalogue.models[0].id!==MODEL||approval.status!=='approved'||approval.definition.sha256!==MODEL_SHA256||review.status!=='accepted'||review.model.sha256!==MODEL_SHA256)throw Error('Catalogue/review/approval binding mismatch.');
 if(active)$('identity').textContent=JSON.stringify(identity,null,2);
 // Import and instantiate the exact bytes already hashed above, without a second network read.
 const moduleURL=URL.createObjectURL(new Blob([bytes[0]],{type:'text/javascript'}));
 try{
  const {default:create}=await import(moduleURL),verifiedWasm=new Uint8Array(bytes[1]);
  const wasmModule=await WebAssembly.compile(verifiedWasm);
  // Emscripten 6.0.8's generated module omits the wasmBinary reader; its supported
  // instantiateWasm hook supplies the verified module before URL resolution/fetch.
  engine=await create({wasmBinary:verifiedWasm,instantiateWasm(imports,receive){const instance=new WebAssembly.Instance(wasmModule,imports);receive(instance);return instance.exports;}});
 }finally{URL.revokeObjectURL(moduleURL);}
 const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));if(descriptor.sha256!==identity.catalogue_hash||descriptor.models?.length!==1||descriptor.models[0].id!==MODEL)throw Error('Loaded engine identity mismatch.');if(active){$('run').disabled=false;$('run').textContent='Run increment path';}
}
function ensureEngine(){
 if(engine)return Promise.resolve();
 if(!initialization)initialization=loadEngine().catch(error=>{initialization=null;throw error;});
 return initialization;
}

 function select(id){
  const next=id===MODEL,changed=next!==active;active=next;panel.hidden=!next;
  if(!next){if(changed)invalidate();return false;}
  cancelOrdinary();document.getElementById('model').value=MODEL;
  if(changed){invalidate('Checking exact J2 package…');const mine=token;ensureEngine().then(()=>{if(active&&mine===token){$('identity').textContent=JSON.stringify(identity,null,2);$('run').disabled=false;$('run').textContent='Run increment path';run();}}).catch(error=>{if(active&&mine===token){fail(error);$('run').textContent='Engine unavailable';}});}
  return true;
 }
 return {modelId:MODEL,get active(){return active;},select,showEquations(){if(!active)return false;$('equations').open=true;$('equations').scrollIntoView({behavior:'smooth',block:'start'});return true;}};
}
