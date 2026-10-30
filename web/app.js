const $ = id => document.getElementById(id);
let models=[], catalogue=[], catalogueHash='', currentResult=null, lastSpec=null, experiment=null, worker=null, timer=null, sequence=0, activeId=null;
const protocolNames=['Oedometer','Drained triaxial','Undrained triaxial','Undrained stress control','Isotropic compression'];
function toast(message){$('toast').textContent=message;$('toast').style.display='block';clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').style.display='none',7000);}
function route(){const page=['laboratory','catalogue','methods'].includes(location.hash.slice(1))?location.hash.slice(1):'laboratory';document.querySelectorAll('.page').forEach(x=>x.hidden=x.id!==page);document.querySelectorAll('nav a').forEach(x=>x.classList.toggle('active',x.hash==='#'+page));$('breadcrumb').textContent={laboratory:'MATERIAL LABORATORY',catalogue:'MODEL CATALOGUE',methods:'METHODS & EVIDENCE'}[page];}
function model(){return models.find(x=>x.id===$('model').value);}
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function sourceLinks(container,sources){
  for(const source of sources){
    const url=new URL(source.url);if(!['https:','http:'].includes(url.protocol))continue;
    const row=element('p',undefined,'source-reference'),link=element('a',source.role+' · '+source.locator+' ↗');
    link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';row.append(link);container.append(row);
  }
}
function definitionLink(id){const link=element('a','Model definition (JSON) ↗');link.href='./models/'+encodeURIComponent(id)+'.json';link.target='_blank';link.rel='noopener';return link;}
function field(container,name,label,value,min,max,factor=1){
  const lab=element('label');const span=element('span',label);span.title=label;lab.append(span);
  const input=document.createElement('input');input.type='number';input.id=name;input.value=value/factor;input.step='any';input.required=true;input.dataset.factor=factor;
  if(min!==undefined)input.min=min/factor;if(max!==undefined)input.max=max/factor;lab.append(input);container.append(lab);
}
function populate(){
  const m=model();$('model-description').textContent=m.description;$('model-family').textContent=m.family;$('model-status').textContent=m.status;
  $('parameter-fields').replaceChildren();for(const [name,p] of Object.entries(m.parameters))field($('parameter-fields'),'param-'+name,p.label||name,p.default,p.min,p.max);
  $('state-fields').replaceChildren();
  for(const s of m.state.slice(1)){
    if(s.transient)continue;
    if(s.shape==='sym'){
      const lab=element('label',s.name+' · 6 Mandel components');const input=document.createElement('input');input.type='text';input.id='state-'+s.name;input.value=s.initial.join(',');input.required=true;lab.append(input);$('state-fields').append(lab);
    }else field($('state-fields'),'state-'+s.name,s.name+(s.unit==='Pa'?' (kPa)':''),s.initial,undefined,undefined,s.unit==='Pa'?1000:1);
  }
  const content=$('equation-content');content.replaceChildren(element('p',m.description));
  content.append(element('p','Integration: '+m.integration+'. State equations are residuals for implicit models, or increments per unit path fraction for rate models.'));
  for(const d of m.derived)content.append(element('pre',d.name+' = '+d.expr));
  for(const [name,expression]of Object.entries(m.equations))content.append(element('pre',name+' : '+expression));
  sourceLinks(content,m.sources);
  const sources=$('model-sources');sources.replaceChildren();sourceLinks(sources,m.sources);sources.append(definitionLink(m.id));
  currentResult=null;lastSpec=null;renderCharts();$('export-run').disabled=$('export-csv').disabled=true;
}
function valuesForState(m){
  const p=Number($('confinement').value)*1000,ratio=Number($('stress-ratio').value);const z=[p*ratio,p,p,0,0,0];
  for(const s of m.state.slice(1)){
    if(s.transient)z.push(s.initial);
    else if(s.shape==='sym'){
      const text=$('state-'+s.name).value;const tokens=text.split(',');if(tokens.length!==6||tokens.some(x=>x.trim()===''))throw Error(s.name+' requires 6 Mandel components');
      z.push(...tokens.map(Number));
    }else z.push(Number($('state-'+s.name).value)*Number($('state-'+s.name).dataset.factor));
  }
  return z;
}
function specification(){
  const m=model(),protocol=Number($('protocol').value);
  return {model:m.id,parameters:Object.keys(m.parameters).map(n=>Number($('param-'+n).value)),initial:valuesForState(m),protocol,target:Number($('target').value)*(protocol===3?1000:.01),steps:Number($('steps').value),cycles:Number($('cycles').value)};
}
function validateSpec(s){
  const m=models.find(m=>m.id===s.model);if(!m)throw Error('This model is not in the executable catalogue.');
  if(!Array.isArray(s.parameters)||s.parameters.length!==Object.keys(m.parameters).length)throw Error('Parameter array does not match model.');
  Object.values(m.parameters).forEach((p,i)=>{if(typeof s.parameters[i]!=='number'||!Number.isFinite(s.parameters[i])||s.parameters[i]<p.min||s.parameters[i]>p.max)throw Error('Parameter outside declared bounds.');});
  const size=m.state.reduce((n,f)=>n+(f.shape==='sym'?6:1),0);
  if(!Array.isArray(s.initial)||s.initial.length!==size||s.initial.some(x=>typeof x!=='number'||!Number.isFinite(x)))throw Error('Initial state has invalid values or length.');
  if(Math.abs(s.initial[1]-s.initial[2])>1e-6||s.initial.slice(3,6).some(x=>x!==0)||s.initial[1]<=0)throw Error('The laboratory requires axisymmetric initial stress with positive radial confinement.');
  if(!Number.isInteger(s.protocol)||s.protocol<0||s.protocol>4||!Number.isInteger(s.steps)||s.steps<1||s.steps>5000||!Number.isInteger(s.cycles)||s.cycles<0||s.cycles>100||typeof s.target!=='number'||!Number.isFinite(s.target)||Math.abs(s.target)>(s.protocol===3?1e8:.1))throw Error('Invalid loading protocol, amplitude or increment count.');
  if(s.cycles&&s.steps<16*s.cycles)throw Error('Use at least 16 increments per cycle.');
  return m;
}
function busy(value){$('run-button').disabled=value;$('cancel-button').hidden=!value;}
function cancel(message='Simulation cancelled.'){activeId=null;clearTimeout(timer);worker?.terminate();worker=null;busy(false);if(message){$('run-state').textContent=message;toast(message);}}
function simulate(s){
  try{
    if(!s){if(!$('controls').reportValidity())return;s=specification();}
    validateSpec(s);cancel('');activeId=++sequence;const id=activeId;busy(true);$('run-state').textContent='Integrating constitutive equations…';
    worker=new Worker('./worker.js',{type:'module'});
    worker.onmessage=({data})=>{
      if(data.id!==activeId)return;clearTimeout(timer);busy(false);activeId=null;worker.terminate();worker=null;
      if(data.error){$('run-state').textContent='Execution error';toast(data.error);return;}
      const r=data.result;if(r.catalogue_hash&&r.catalogue_hash!==catalogueHash){toast('Wasm and model catalogue differ. Reload a consistent build.');return;}
      currentResult=r;lastSpec=structuredClone(s);renderCharts();$('export-run').disabled=$('export-csv').disabled=!r.points?.length;
      $('run-state').textContent=r.ok?'✓ Element test complete':'Stopped · last committed state retained';
      $('run-detail').textContent=r.points?.length?`${r.points.length-1} increments · ${r.elapsed_ms.toFixed(1)} ms · ${protocolNames[s.protocol]}`:r.message;
      $('result-note').textContent=r.ok?'Example parameters. No experimental calibration or predictive validity is implied.':r.message;
      $('pore-caption').textContent=[2,3].includes(s.protocol)?'Fixed radial total stress; incompressible fluid / grains assumption':'Not defined for this drained / mechanical protocol';
      if(!r.ok)toast(r.message);
    };
    worker.onerror=e=>cancel('Worker error: '+e.message);
    timer=setTimeout(()=>cancel('Computation exceeded 15 seconds. Reduce the run size or check the model domain.'),15000);
    worker.postMessage({...s,id});
  }catch(error){toast(error.message);}
}
function axisRange(values){
  if(!values.length)return [0,1];let lo=Infinity,hi=-Infinity;for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}if(lo===hi){const pad=Math.max(Math.abs(lo)*.05,1e-3);lo-=pad;hi+=pad;}else{const pad=(hi-lo)*.07;lo-=pad;hi+=pad;}return [lo,hi];
}
function numberLabel(v){if(Math.abs(v)<1e-10)return '0';return Number(v.toPrecision(3)).toString();}
function svgNode(name,attributes,text){const n=document.createElementNS('http://www.w3.org/2000/svg',name);for(const[k,v]of Object.entries(attributes))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function chart(id,xLabel,yLabel,predicted,measured=[]){
  const svg=$(id);svg.replaceChildren();svg.append(svgNode('title',{},yLabel+' versus '+xLabel));
  const left=62,top=27,w=392,h=211,all=[...predicted,...measured].filter(a=>a.every(Number.isFinite));
  const [xmin,xmax]=axisRange(all.map(p=>p[0])),[ymin,ymax]=axisRange(all.map(p=>p[1]));
  const x=v=>left+(v-xmin)/(xmax-xmin)*w,y=v=>top+h-(v-ymin)/(ymax-ymin)*h;
  for(let i=0;i<=4;i++){
    const yy=top+i*h/4,xx=left+i*w/4;
    svg.append(svgNode('line',{x1:left,y1:yy,x2:left+w,y2:yy,stroke:'#e6e9df','stroke-dasharray':'3 4'}),svgNode('text',{x:left-10,y:yy+4,'text-anchor':'end'},numberLabel(ymax-i*(ymax-ymin)/4)),svgNode('text',{x:xx,y:top+h+19,'text-anchor':'middle'},numberLabel(xmin+i*(xmax-xmin)/4)));
  }
  svg.append(svgNode('text',{x:left+w/2,y:282,'text-anchor':'middle',class:'axis-label'},xLabel),svgNode('text',{x:12,y:top-12,class:'axis-label'},yLabel));
  if(!all.length)svg.append(svgNode('text',{x:left+w/2,y:top+h/2,'text-anchor':'middle'},'Run a test to explore the response'));
  if(predicted.length)svg.append(svgNode('polyline',{points:predicted.map(([a,b])=>`${x(a)},${y(b)}`).join(' '),fill:'none',stroke:'#bc643e','stroke-width':2,'stroke-linejoin':'round'}));
  const stride=Math.max(1,Math.ceil(measured.length/350));measured.filter((_,i)=>i%stride===0).forEach(([a,b])=>svg.append(svgNode('circle',{cx:x(a),cy:y(b),r:2,fill:'#547a95',opacity:.6})));
  if(predicted.length){
    const marker=svgNode('circle',{r:4,fill:'#bc643e',stroke:'#fff','stroke-width':2,visibility:'hidden'}),label=svgNode('text',{x:left+8,y:top+12,visibility:'hidden'});svg.append(marker,label);
    svg.onpointermove=e=>{const box=svg.getBoundingClientRect(),px=(e.clientX-box.left)/box.width*480;let nearest=predicted[0];for(const pt of predicted)if(Math.abs(x(pt[0])-px)<Math.abs(x(nearest[0])-px))nearest=pt;marker.setAttribute('cx',x(nearest[0]));marker.setAttribute('cy',y(nearest[1]));marker.setAttribute('visibility','visible');label.textContent=`${numberLabel(nearest[0])}, ${numberLabel(nearest[1])}`;label.setAttribute('visibility','visible');};
    svg.onpointerleave=()=>{marker.setAttribute('visibility','hidden');label.setAttribute('visibility','hidden');};
  }
}
function renderCharts(){
  document.querySelectorAll('.measured-key').forEach(e=>e.hidden=!experiment);
  const pts=currentResult?.points||[],rows=experiment?.rows||[];
  const series=(fx,fy)=>rows.filter(r=>Number.isFinite(fx(r))&&Number.isFinite(fy(r))).map(r=>[fx(r),fy(r)]);
  chart('stress-chart','Axial strain ε₁ (%)','Deviator stress q (kPa)',pts.map(p=>[p.strain[0]*100,p.q_signed/1000]),series(r=>r.axial_strain*100,r=>r.q/1000));
  chart('path-chart','Mean effective stress p′ (kPa)','Deviator stress q (kPa)',pts.map(p=>[p.p/1000,p.q_signed/1000]),series(r=>r.p/1000,r=>r.q/1000));
  chart('volume-chart','Axial strain ε₁ (%)','Volumetric strain εᵥ (%)',pts.map(p=>[p.strain[0]*100,p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100]),series(r=>r.axial_strain*100,r=>r.volumetric_strain*100));
  chart('pore-chart','Axial strain ε₁ (%)','Pore pressure Δu (kPa)',lastSpec&&[2,3].includes(lastSpec.protocol)?pts.map(p=>[p.strain[0]*100,p.u/1000]):[],series(r=>r.axial_strain*100,r=>r.pore_pressure/1000));
}
function catalogueCards(){
  const query=$('search').value.toLowerCase(),filter=$('availability').value,grid=$('catalogue-grid');grid.replaceChildren();
  for(const entry of catalogue){const executable=models.some(x=>x.id===entry.id);if(filter==='executable'&&!executable||filter==='candidate'&&executable)continue;if(!(entry.name+' '+entry.family+' '+entry.id).toLowerCase().includes(query))continue;
    const card=element('article',undefined,'catalogue-card');card.append(element('span',executable?'Executable · '+models.find(x=>x.id===entry.id).status:'Research candidate','badge'),element('h2',entry.name),element('p',entry.family),element('p',entry.note||''));
    if(executable){sourceLinks(card,models.find(x=>x.id===entry.id).sources);card.append(definitionLink(entry.id));}
    else if(entry.discovery_url)sourceLinks(card,[{url:entry.discovery_url,role:'Discovery reference',locator:'Bibliographic review pending'}]);
    if(executable){const b=element('button','Explore in laboratory →','text-button');b.onclick=()=>{$('model').value=entry.id;populate();location.hash='laboratory';simulate();};card.append(b);}
    else {const p=element('p',entry.capability_gap||'Source extraction, declarative transcription and numerical verification pending.');card.append(p);}
    grid.append(card);
  }
  if(!grid.children.length)grid.append(element('p','No matching models.'));
}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function setProtocol(){const stress=$('protocol').value==='3';$('target-label').textContent=stress?'Deviator stress (kPa)':'Axial strain (%)';$('target').value=stress?'20':'1';$('target').min=stress?'-100000':'-10';$('target').max=stress?'100000':'10';}
async function readFile(file){if(!file)return null;if(file.size>10*1024*1024)throw Error('File exceeds the 10 MB limit.');return JSON.parse(await file.text());}
async function importRun(file){
  try{const doc=await readFile(file);if(!doc)return;if(doc.schema_version!=='0.1')throw Error('Unsupported run schema version.');if(doc.catalogue_hash!==catalogueHash)throw Error('Run was created with a different model catalogue. Use the matching release.');
    const s=doc.specification,m=validateSpec(s);$('model').value=m.id;populate();Object.keys(m.parameters).forEach((n,i)=>$('param-'+n).value=s.parameters[i]);
    $('confinement').value=s.initial[1]/1000;$('stress-ratio').value=s.initial[0]/s.initial[1];let offset=6;
    for(const f of m.state.slice(1)){const size=f.shape==='sym'?6:1;if(!f.transient){const input=$('state-'+f.name);input.value=size===6?s.initial.slice(offset,offset+6).join(','):s.initial[offset]/Number(input.dataset.factor);}offset+=size;}
    $('protocol').value=s.protocol;setProtocol();$('target').value=s.target/(s.protocol===3?1000:.01);$('steps').value=s.steps;
    if(![...$('cycles').options].some(o=>Number(o.value)===s.cycles))$('cycles').append(new Option(s.cycles+' sinusoidal cycles',s.cycles));$('cycles').value=s.cycles;
    location.hash='laboratory';simulate(s);
  }catch(e){toast(e.message);}
}
async function loadExperiment(file){
  try{const data=await readFile(file);if(!data)return;
    if(data.schema_version!=='0.1'||data.kind!=='experiment'||!Array.isArray(data.rows)||!data.rows.length||data.rows.length>100000)throw Error('Expected a normalized Atlas experiment file with 1–100,000 rows.');
    if(data.conventions?.stress!=='compression-positive'||data.conventions?.strain!=='compression-positive'||data.conventions?.stress_unit!=='Pa'||data.conventions?.strain_unit!=='1')throw Error('Experiment must declare compression-positive Pa / dimensionless strain conventions.');
    for(const row of data.rows){if(typeof row.axial_strain!=='number'||typeof row.q!=='number'||!Number.isFinite(row.axial_strain)||!Number.isFinite(row.q))throw Error('Every row needs finite axial_strain and q.');for(const k of ['p','volumetric_strain','pore_pressure'])if(row[k]!==undefined&&!Number.isFinite(row[k]))throw Error('Nonfinite experiment channel.');}
    experiment=data;$('experiment-status').textContent=`${data.id}: ${data.rows.length} measured points · comparison applicability must be checked.`;renderCharts();toast('Experimental measurements loaded locally.');
  }catch(e){toast(e.message);}
}
window.addEventListener('hashchange',route);$('controls').onsubmit=e=>{e.preventDefault();simulate();};$('cancel-button').onclick=()=>cancel();$('model').onchange=()=>{cancel('');populate();simulate();};$('protocol').onchange=setProtocol;
$('reset').onclick=()=>{cancel('');$('controls').reset();populate();setProtocol();};$('equations-button').onclick=()=>{$('equations').open=true;$('equations').scrollIntoView({behavior:'smooth'});};
$('import-run').onclick=()=>$('run-file').click();$('run-file').onchange=e=>importRun(e.target.files[0]);$('experiment-file').onchange=e=>loadExperiment(e.target.files[0]);
$('controls').addEventListener('input',()=>{if(currentResult)$('run-state').textContent='Settings changed · run again to update plots';});
$('export-run').onclick=()=>download(lastSpec.model+'-run.json',JSON.stringify({schema_version:'0.1',catalogue_hash:catalogueHash,specification:lastSpec,result:currentResult},null,2),'application/json');
$('export-csv').onclick=()=>{const rows=['axial_strain,radial_strain,volumetric_strain,p_Pa,q_signed_Pa,pore_pressure_Pa,iterations,substeps'];for(const p of currentResult.points)rows.push([p.strain[0],p.strain[1],p.strain.slice(0,3).reduce((a,b)=>a+b,0),p.p,p.q_signed,p.u,p.iterations,p.substeps].join(','));download(lastSpec.model+'-results.csv',rows.join('\n'),'text/csv');};
$('search').oninput=$('availability').onchange=catalogueCards;
try{
  const [response,manifest]=await Promise.all([fetch('./models.json'),fetch('./catalogue.json')]);if(!response.ok||!manifest.ok)throw Error('Catalogue could not be loaded.');
  const definitions=await response.json();catalogueHash=definitions.sha256;models=definitions.models;catalogue=(await manifest.json()).models;
  models.forEach(m=>$('model').append(new Option(m.name,m.id)));$('model').value='hypoplastic-sand-vw96';$('catalogue-count').textContent=catalogue.length;$('build-hash').textContent='Catalogue SHA-256: '+catalogueHash;
  populate();catalogueCards();route();simulate();
}catch(e){toast('Initialization failed: '+e.message);$('run-state').textContent='Unable to initialize';}
