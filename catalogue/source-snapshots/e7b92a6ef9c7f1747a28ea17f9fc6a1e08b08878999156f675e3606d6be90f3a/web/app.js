import {setupKelvinVoigtLaboratory} from './kelvin-voigt-laboratory.mjs';
import {setupOrthotropicLaboratory} from './orthotropic-laboratory.mjs';
import {setupJ2Laboratory} from './j2-laboratory.mjs';
import {setupTimedLaboratory} from './timed-laboratory.mjs';
import {setupSlsLaboratory} from './sls-laboratory.mjs';
import {setupPathLaboratory} from './path-laboratory.mjs';
import {setupMaxwellLaboratory} from './maxwell-laboratory.mjs';
import {setupImplicitPathLaboratory} from './implicit-path-laboratory.mjs';
import {createLaboratoryControllerRouter} from './laboratory-controller-router.mjs';
import {validateSupport,unsupportedReason,requireSupportedControl} from './laboratory-support.mjs';
import {timedLaboratoryRoute} from './timed-route.mjs';
import {setupLaboratoryExamples} from './laboratory-examples-view.mjs';
import {validateApplicability,applicabilitySection} from './applicability-view.mjs';
import {formulationSection,recordedDescription} from './formulation-view.mjs';
import {createLoading,normalizeLoading,verifyReturnedLoading} from './loading.mjs';
import {laboratoryStress,validateScopedLaboratory,verifyScopedLaboratory} from './laboratory-scope.mjs';
import {laboratoryPresentation,laboratoryPoreView} from './laboratory-view.mjs';
import {createLaboratoryDocument,parseLaboratoryDocument,laboratoryDocumentCSV} from './laboratory-document.mjs';
import {persistentState,temporaryStateComponents,laboratoryExample} from './state-contract.mjs';
import {catalogueHash as catalogueModelHash,catalogueRoute,validateEvidenceIndex,evidenceSection} from './catalogue.mjs';
import {settingFields,normalizeSettings,verifyReturnedSettings} from './numerics.mjs';
import {normalizeWichtmann,validateExperiment,measuredSeries,fetchExperiment,comparisonAxes,comparisonMetadata,compatibleExperiment,comparisonSeries,supportsEffectiveExperiment} from './experiments.mjs';
const $ = id => document.getElementById(id);
let j2View=null,timedView=null;
let compiledCatalogue=null, laboratoryExamples=null, controlSupport=null;
let models=[], catalogue=[], catalogueHash='', currentResult=null, lastSpec=null, experiment=null, worker=null, timer=null, sequence=0, activeId=null, pendingRun=null, updateTimer=null;
let experiments=[],builtinExperiments=[],experimentLoadSequence=0;
const experimentCache=new Map();
let applicabilityMatrix=null,applicabilityState='loading';
async function loadApplicability(){
  try{const response=await fetch('./applicability.json');if(!response.ok)throw Error('Applicability unavailable');applicabilityMatrix=validateApplicability(await response.json());applicabilityState='loaded';}
  catch{applicabilityState='failed';}
  const selected=catalogueRoute(location.hash).modelId,entry=catalogue.find(x=>x.id===selected);
  if(entry&&$('catalogue-dialog').open){const body=$('catalogue-detail-body'),scroll=body.scrollTop;body.querySelector('.catalogue-applicability')?.replaceWith(applicabilitySection(document,entry.id,applicabilityMatrix,applicabilityState));body.scrollTop=scroll;}
}
let evidenceIndex=null,evidenceState='loading';
async function loadEvidenceIndex(){
  try{const response=await fetch('./evidence.json');if(!response.ok)throw Error('Evidence unavailable');evidenceIndex=validateEvidenceIndex(await response.json());evidenceState='loaded';refreshRecordedDescriptions();refreshModelSummary();}
  catch{evidenceState='failed';}
  const selected=catalogueRoute(location.hash).modelId,entry=catalogue.find(x=>x.id===selected);
  if(entry&&$('catalogue-dialog').open){const body=$('catalogue-detail-body'),scroll=body.scrollTop;refreshCatalogueStatus(entry,models.find(m=>m.id===entry.id));body.querySelector('.catalogue-evidence')?.replaceWith(evidenceSection(document,entry.id,evidenceIndex,evidenceState));body.scrollTop=scroll;}
}
function refreshRecordedDescriptions(){
  const selected=models.find(m=>m.id===$('model').value);
  if(selected){
    $('model-description').textContent=recordedDescription(selected.description,selected.id,evidenceIndex);
    const equationDescription=$('equation-content')?.querySelector('p');
    if(equationDescription)equationDescription.textContent=recordedDescription(selected.description,selected.id,evidenceIndex);
  }
  const id=catalogueRoute(location.hash).modelId,entry=catalogue.find(e=>e.id===id);
  if(!entry||!$('catalogue-dialog').open)return;
  const spec=models.find(m=>m.id===id),body=$('catalogue-detail-body');
  const note=body.querySelector('.catalogue-detail-note');
  if(note)note.textContent=recordedDescription(entry.note||spec?.description||'Bibliographic and formulation review pending.',id,evidenceIndex);
  const description=body.querySelector('.definition-description');
  if(description&&spec)description.textContent=recordedDescription(spec.description,id,evidenceIndex);
}
function restoreCatalogueFocus(){
  if(!$('catalogue').hidden&&!$('catalogue').contains(document.activeElement)){
    const hash=catalogueModelHash($('catalogue-detail-id').textContent);
    const link=[...document.querySelectorAll('#catalogue-grid .catalogue-open')].find(x=>x.hash===hash);
    (link||$('search')).focus({preventScroll:true});
  }
}
function closeCatalogue(){if(catalogueRoute(location.hash).modelId||catalogueRoute(location.hash).invalid){history.replaceState(null,'','#catalogue');route();}else $('catalogue-dialog').close();restoreCatalogueFocus();}
const protocolNames=['Oedometer','Drained triaxial','Undrained triaxial','Undrained stress control','Isotropic compression'];
function toast(message){$('toast').textContent=message;$('toast').style.display='block';clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').style.display='none',7000);}
function specialLaboratoryActive(){return !!(j2View?.active||timedView?.active);}
function selectJ2(id){
  const active=j2View?.select(id)??false;
  document.querySelector('#laboratory > .lab-layout').hidden=active;
  document.querySelector('#laboratory > .workspace-links').hidden=active;
  $('import-run').hidden=active;
  if(active){
    $('model-description').textContent='Associated J2 plasticity with linear isotropic hardening. All-six prescribed strain increments; full stress and hardening history.';
    $('model-family').textContent='Small-strain plasticity';$('model-status').textContent='Approved bounded scope';
    $('model-sources').replaceChildren();
    for(const [text,path] of [['Independent scientific review and limitations','review.html#law-review'],['Exact approval','approval.json'],['Exact approved definition','j2-linear-isotropic-hardening-be.json']]){const a=element('a',text+' ↗');a.href='./material-point-j2/'+path;a.target='_blank';a.rel='noopener';const row=element('p');row.append(a);$('model-sources').append(row);}
  }
  return active;
}
function selectLaboratory(id){
  if(j2View&&id===j2View.modelId){
    // The timed profile's deactivation restores ordinary visibility, so it must
    // run before the J2 helper establishes the selected workspace.
    if(timedView?.active)timedView.select(false);
    if(!j2View.active)++experimentLoadSequence;
    return selectJ2(id);
  }
  if(timedView?.supports(id)){
    if(j2View?.active)j2View.select(false);
    if(!timedView.active)++experimentLoadSequence;
    const active=timedView.select(id);
    if(active&&id==='orthotropic-linear-elastic-ogs'){ $('model-description').textContent='Nine-constant orthotropic linear elasticity; all-six strain increments and complete stress state. Constant parameters, fixed aligned material axes, dry total Cauchy stress; illustrative parameters and no experimental validation.'; $('model-family').textContent='Orthotropic elasticity';$('model-status').textContent='Approved bounded scope';$('model-sources').replaceChildren();for(const [text,path] of [['Pinned governing OpenGeoSys source','https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.cpp'],['Independent review and source mapping','./material-point-orthotropic/review.html'],['Exact approval','./material-point-orthotropic/approval.json'],['Exact approved definition','./material-point-orthotropic/model.json']]){const a=element('a',text+' ↗');a.href=path;a.target='_blank';a.rel='noopener';const row=element('p');row.append(a);$('model-sources').append(row);}}
    if(active)$('model').value=id;
    if(active&&id==='lade-duncan-1975-midpoint-elastic-eq19-gap-v4'){
      $('model-description').textContent='Lade–Duncan (1975) cohesionless-soil elastoplasticity. Midpoint elastic/local Eq. 19 integration; small strain, compression-positive total mechanical stress, fixed axes and zero pore pressure. Custom paths remain exploratory.';
      $('model-family').textContent='Soil elastoplasticity';$('model-status').textContent='Approved bounded numerical scope';
      $('model-sources').replaceChildren();
      for(const [text,path] of [['Original 1975 source','https://doi.org/10.1061/AJGEB6.0000204'],['Independent scientific checklist','./engine-implicit-path/review.json'],['Exact approval and limitations','./engine-implicit-path/approval.json'],['Exact approved model JSON','./engine-implicit-path/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.json']]){const a=element('a',text+' ↗');a.href=path;a.target='_blank';a.rel='noopener';const row=element('p');row.append(a);$('model-sources').append(row);}
    }
    $('import-run').hidden=active;
    return active;
  }
  if(j2View?.active)j2View.select(false);
  if(timedView?.active)timedView.select(false);
  document.querySelector('#laboratory > .lab-layout').hidden=false;
  document.querySelector('#laboratory > .workspace-links').hidden=false;
  $('import-run').hidden=false;
  return false;
}
function activateLaboratoryModel(id,{run=true}={}){
  if(id!==j2View?.modelId&&!timedView?.supports(id)&&!models.some(m=>m.id===id)){
    toast('That model is not available in this laboratory.');return false;
  }
  cancel('');
  if(selectLaboratory(id))return true;
  $('model').value=id;populate();if(run)simulate();return true;
}
function route({initial=false}={}){
  const anchor=location.hash.slice(1),selection=catalogueRoute(location.hash),page=selection.page;
  if(page==='laboratory'&&anchor.startsWith('laboratory?')){
    const query=new URLSearchParams(anchor.slice(anchor.indexOf('?')+1));
    if(query.has('model')){
      const id=query.get('model');
      if(query.getAll('model').length!==1)toast('Use one model in a laboratory link.');
      else if(id!==$('model').value||(id===j2View?.modelId&&!j2View.active)||(timedView?.supports(id)&&!timedView.active))activateLaboratoryModel(id,{run:!initial});
    }
  }
  const entry=catalogue.find(x=>x.id===selection.modelId);
  if(entry)showCatalogueModel(entry,models.find(x=>x.id===entry.id));
  else{if($('catalogue-dialog').open)$('catalogue-dialog').close();if(selection.modelId||selection.invalid)toast('That model link is not in this catalogue.');}
  document.querySelectorAll('.page').forEach(x=>x.hidden=x.id!==page);
  document.querySelectorAll('.rail nav a').forEach(x=>{const active=x.hash==='#'+page;x.classList.toggle('active',active);if(active)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current');});
  if($('breadcrumb'))$('breadcrumb').textContent={laboratory:'MODEL TESTING',catalogue:'MODEL CATALOGUE',methods:'METHODS & EVIDENCE'}[page];
  const target=$(anchor);
  if(target&&target!==$(page)){
    if(target.tagName==='DETAILS')target.open=true;
    requestAnimationFrame(()=>target.scrollIntoView({behavior:'smooth',block:'start'}));
  }else window.scrollTo(0,0);
}
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
  const input=document.createElement('input');input.type='number';input.id=name;input.name=model().id+':'+name;input.autocomplete='off';input.value=value/factor;input.step='any';input.required=true;input.dataset.factor=factor;
  if(min!==undefined)input.min=min/factor;if(max!==undefined)input.max=max/factor;lab.append(input);container.append(lab);
  const low=min===undefined?Math.min(0,value/factor):min/factor,high=max===undefined?Math.max(1,value/factor*3):max/factor;addSlider(input,label,low,high);
}
// Sliders explore the declared domain; number fields retain precise values and units.
function addSlider(input, label, min=Number(input.min), max=Number(input.max)){
  if(!Number.isFinite(min)||!Number.isFinite(max)||max<=min)return;
  const slider=element('input');slider.type='range';slider.min=0;slider.max=1000;slider.step=1;
  slider.name=(input.name||input.id)+':slider';slider.dataset.for=input.id;slider.setAttribute('aria-label',label+' slider');
  const logarithmic=min>0&&max/min>=1000;
  slider.toValue=t=>logarithmic?min*Math.pow(max/min,t):min+(max-min)*t;
  slider.toPosition=v=>logarithmic?Math.log(Math.max(min,v)/min)/Math.log(max/min):(v-min)/(max-min);
  slider.oninput=()=>{
    let value=slider.toValue(Number(slider.value)/1000);
    if(input.step!=='any'){const step=Number(input.step)||1,base=Number(input.min)||0;value=base+Math.round((value-base)/step)*step;}
    input.value=Math.max(min,Math.min(max,Number(value.toPrecision(5))));
  };
  // Each input has its own explicit label; a range must not share a wrapping label.
  const lab=input.closest('label');lab.htmlFor=input.id;lab.after(slider);
  syncSliders();
}
function syncSliders(){
  document.querySelectorAll('input[type="range"][data-for]').forEach(slider=>{
    const input=$(slider.dataset.for),value=Number(input.value);
    slider.value=Math.max(0,Math.min(1000,slider.toPosition(value)*1000));
    slider.setAttribute('aria-valuetext',input.value);
  });
}
function invalidate(clearUpdate=true){
  ++sequence;pendingRun=null;if(clearUpdate){clearTimeout(updateTimer);updateTimer=null;}
  $('export-run').disabled=$('export-csv').disabled=true;
  $('response-charts').classList.add('updating');$('response-charts').setAttribute('aria-busy','true');
}
function scheduleUpdate(){
  if(specialLaboratoryActive())return;
  invalidate(false);syncSliders();
  if(!$('controls').checkValidity()){
    clearTimeout(updateTimer);updateTimer=null;
    const invalid=$('controls').querySelector(':invalid');
    $('run-state').textContent='Waiting for a valid input';$('response-charts').setAttribute('aria-busy','false');
    $('control-status').textContent=(invalid?.labels?.[0]?.textContent.trim()||'Input')+': '+(invalid?.validationMessage||'Check this value.');
    return;
  }
  $('run-state').textContent='Updating response…';$('control-status').textContent='Updating from your latest settings…';
  // Coalesce rapid edits without waiting for a continuous drag to end.
  if(updateTimer===null)updateTimer=setTimeout(()=>{updateTimer=null;simulate();},100);
}
function updateScopeLabels(){
  if(!model())return;
  const p=laboratoryPresentation(model());
  $('confinement-label').textContent=p.radialLabel;
  document.querySelector('[data-for="confinement"]')?.setAttribute('aria-label',p.radialLabel+' slider');
  for(const option of $('protocol').options)option.textContent=p.protocols[Number(option.value)];
  $('path-title').textContent=p.pathTitle;$('path-chart').setAttribute('aria-label',p.pathAria);$('stress-chart').setAttribute('aria-label',p.stressAria);
  $('target-label').textContent=$('protocol').value==='3'?(p.scope==='total'?'Total deviator stress (kPa)':'Deviator stress (kPa)'):'Axial strain (%)';
  document.querySelector('[data-for="target"]')?.setAttribute('aria-label',$('target-label').textContent+' slider');
}
function updateControlSupport(){
  const chosen={model:model()?.id,protocol:Number($('protocol').value),cycles:1};
  const reason=unsupportedReason(controlSupport,chosen);
  for(const option of $('cycles').options)option.disabled=!!unsupportedReason(controlSupport,{...chosen,cycles:Number(option.value)});
  if($('cycles').selectedOptions[0]?.disabled)$('cycles').value='0';
  $('control-support').textContent=reason;$('control-support').hidden=!reason;
}
function registeredModelReview(id){return (evidenceIndex?.agent_reviews||[]).find(r=>r.catalogue_id===id&&r.status==='accepted'&&r.definition_current&&r.registered_approval_id!==null);}
function refreshModelSummary(){
  if(specialLaboratoryActive())return;
  const m=model();if(!m)return;
  const entry=catalogue.find(e=>e.id===m.id);
  $('model-description').textContent=recordedDescription(entry?.dossier?entry.note:m.description,m.id,evidenceIndex);
  $('model-status').textContent=registeredModelReview(m.id)?'Approved scope':m.status;
}
function populate({loadExample=true}={}){
  if(specialLaboratoryActive())return;
  laboratoryExamples?.refresh();
  const m=model(),example=loadExample?laboratoryExample(m):null;updateScopeLabels();
  if(example){$('confinement').value=example.confinement;$('stress-ratio').value=example.stressRatio;}
  refreshModelSummary();$('model-family').textContent=m.family;
  $('parameter-fields').replaceChildren();
  for(const [name,p] of Object.entries(m.parameters)){
    const angle=p.unit==='rad'||/\[rad\]/.test(p.label||''),factor=angle?Math.PI/180:1;
    const label=angle?(p.label||name).replace(/\s*\[rad\]/,'')+' (°)':p.label||name;
    field($('parameter-fields'),'param-'+name,label,p.default,p.min,p.max,factor);
    if(angle)$('param-'+name).value=Number((p.default/factor).toPrecision(14));
  }
  $('state-fields').replaceChildren();
  for(const s of m.state.slice(1)){
    if(!persistentState(s))continue;
    if(s.shape==='sym'){
      const lab=element('label',s.name+' · 6 Mandel components');const input=document.createElement('input');input.type='text';input.id='state-'+s.name;input.name=m.id+':'+input.id;input.autocomplete='off';input.value=s.initial.join(',');input.required=true;lab.append(input);$('state-fields').append(lab);
    }else field($('state-fields'),'state-'+s.name,s.name+(s.unit==='Pa'?' (kPa)':''),s.initial,undefined,undefined,s.unit==='Pa'?1000:1);
  }
  const content=$('equation-content');content.replaceChildren(element('p',recordedDescription(m.description,m.id,evidenceIndex)));
  content.append(element('p','Equation form: '+(m.formulation?.equation_form??m.integration)+'. State equations are residuals for implicit models, or increments per unit path fraction for strain-path rate models.'));
  for(const d of m.derived)content.append(element('pre',d.name+' = '+d.expr));
  for(const [name,expression]of Object.entries(m.equations))content.append(element('pre',name+' : '+expression));
  if(m.domain?.length){
    content.append(element('h3','Declared domain'));
    for(const constraint of m.domain)content.append(element('pre',constraint));
  }
  sourceLinks(content,m.sources);
  const sources=$('model-sources');sources.replaceChildren();sourceLinks(sources,m.sources);sources.append(definitionLink(m.id));
  updateControlSupport();currentResult=null;lastSpec=null;experimentOptions($('experiment-select').value);renderCharts();$('export-run').disabled=$('export-csv').disabled=true;syncSliders();
}
function valuesForState(m){
  const p=Number($('confinement').value)*1000,ratio=Number($('stress-ratio').value);const z=[p*ratio,p,p,0,0,0];
  for(const s of m.state.slice(1)){
    if(!persistentState(s))z.push(...temporaryStateComponents(s));
    else if(s.shape==='sym'){
      const text=$('state-'+s.name).value;const tokens=text.split(',');if(tokens.length!==6||tokens.some(x=>x.trim()===''))throw Error(s.name+' requires 6 Mandel components');
      z.push(...tokens.map(Number));
    }else z.push(Number($('state-'+s.name).value)*Number($('state-'+s.name).dataset.factor));
  }
  return z;
}
function numericalControls(){
  const container=$('numerical-fields');
  for(const f of settingFields){
    const label=element('label',f.label),input=element('input');input.type='number';input.id='numerical-'+f.key;input.name=input.id;input.autocomplete='off';
    input.value=input.defaultValue=f.value;input.required=true;input.min=f.min;input.step=f.integer?'1':'any';
    if(f.max!==undefined)input.max=f.max;label.append(input);container.append(label);
  }
}
function numericalValues(){
  const s=normalizeSettings();for(const f of settingFields)s[f.key]=Number($('numerical-'+f.key).value);
  return normalizeSettings(s);
}
function setNumericalValues(value){const s=normalizeSettings(value);for(const f of settingFields)$('numerical-'+f.key).value=s[f.key];}
function specification(){
  const m=model(),protocol=Number($('protocol').value);
  const s={response_contract:'stress-scope-0.1',stress_scope:laboratoryStress(m).scope,model:m.id,parameters:Object.keys(m.parameters).map(n=>Number($('param-'+n).value)*Number($('param-'+n).dataset.factor)),initial:valuesForState(m),protocol,target:Number($('target').value)*(protocol===3?1000:.01),steps:Number($('steps').value),cycles:Number($('cycles').value),integration_settings:numericalValues()};
  if($('loading-version').value==='exact')s.loading=createLoading(s);
  return s;
}
function validateSpec(s){
  normalizeSettings(s.integration_settings);normalizeLoading(s);
  const m=models.find(m=>m.id===s.model);if(!m)throw Error('This model is not in the executable catalogue.');
  if(s.response_contract!==undefined)validateScopedLaboratory(s,compiledCatalogue);
  else if(laboratoryStress(m).scope!=='effective')throw Error('Legacy laboratory inputs require effective stress.');
  if(!Array.isArray(s.parameters)||s.parameters.length!==Object.keys(m.parameters).length)throw Error('Parameter array does not match model.');
  Object.values(m.parameters).forEach((p,i)=>{if(typeof s.parameters[i]!=='number'||!Number.isFinite(s.parameters[i])||s.parameters[i]<p.min||s.parameters[i]>p.max)throw Error('Parameter outside declared bounds.');});
  const size=m.state.reduce((n,f)=>n+(f.shape==='sym'?6:1),0);
  if(!Array.isArray(s.initial)||s.initial.length!==size||s.initial.some(x=>typeof x!=='number'||!Number.isFinite(x)))throw Error('Initial state has invalid values or length.');
  if(Math.abs(s.initial[1]-s.initial[2])>1e-6||s.initial.slice(3,6).some(x=>x!==0)||s.initial[1]<=0)throw Error('The laboratory requires axisymmetric initial stress with positive radial confinement.');
  if(!Number.isInteger(s.protocol)||s.protocol<0||s.protocol>4||!Number.isInteger(s.steps)||s.steps<1||s.steps>5000||!Number.isInteger(s.cycles)||s.cycles<0||s.cycles>100||typeof s.target!=='number'||!Number.isFinite(s.target)||Math.abs(s.target)>(s.protocol===3?1e8:.1))throw Error('Invalid loading protocol, amplitude or increment count.');
  requireSupportedControl(controlSupport,s);
  if(s.cycles&&s.steps<16*s.cycles)throw Error('Use at least 16 increments per cycle.');
  return m;
}
function busy(value){$('cancel-button').hidden=!value;}
function cancel(message='Calculation stopped. Adjust a control to resume.'){
  invalidate();activeId=null;clearTimeout(timer);worker?.terminate();worker=null;busy(false);
  $('response-charts').setAttribute('aria-busy','false');
  if(message){$('run-state').textContent='Calculation stopped';$('control-status').textContent=message;$('retry-button').hidden=false;}
}
function calculationError(message){
  $('run-state').textContent='Response needs attention';$('control-status').textContent=message;
  $('retry-button').hidden=false;$('response-charts').setAttribute('aria-busy','false');
}
function startRun(job){
  const {s,id}=job;if(specialLaboratoryActive()||id!==sequence)return;activeId=id;busy(true);$('retry-button').hidden=true;
  $('run-state').textContent='Updating response…';
  worker??=new Worker('./worker.js',{type:'module'});
  worker.onmessage=({data})=>{
    if(data.id!==activeId||specialLaboratoryActive())return;
    clearTimeout(timer);busy(false);activeId=null;
    // A completed older calculation must never replace newer slider settings.
    if(data.id===sequence){
      let responseError=data.error;
      if(!responseError){try{if(s.response_contract!==undefined)verifyScopedLaboratory(data.result,s,compiledCatalogue);else{verifyReturnedSettings(data.result,s.integration_settings);verifyReturnedLoading(data.result,s,catalogueHash);}}catch(error){responseError=error.message;}}
      if(responseError)calculationError(responseError);
      else if(data.result.catalogue_hash!==catalogueHash)calculationError('Wasm and model catalogue differ. Reload a consistent build.');
      else{
        const r=data.result;currentResult=r;lastSpec=structuredClone(s);renderCharts();
        $('export-run').disabled=$('export-csv').disabled=!r.points?.length;
        $('response-charts').classList.remove('updating');$('response-charts').setAttribute('aria-busy','false');
        $('run-state').textContent=r.ok?'✓ Response up to date':'Stopped · last committed state retained';
        $('control-status').textContent=r.ok?'Live · changes update automatically.':r.message;
        $('run-detail').textContent=r.points?.length?`${r.points.length-1} increments · ${Number.isFinite(r.elapsed_ms)?r.elapsed_ms.toFixed(1)+' ms':'duration unavailable'} · ${laboratoryPresentation(model()).protocols[s.protocol]} · ${laboratoryStress(model()).scope} stress`:r.message;
        $('result-note').textContent=r.ok?'Example parameters. No experimental calibration or predictive validity is implied.':r.message;
      }
    }
    if(pendingRun&&!specialLaboratoryActive()){const next=pendingRun;pendingRun=null;startRun(next);}
  };
  worker.onerror=e=>{if(id!==activeId||specialLaboratoryActive())return;const next=pendingRun;const latest=id===sequence&&!specialLaboratoryActive();clearTimeout(timer);worker?.terminate();worker=null;activeId=null;pendingRun=null;busy(false);if(latest)calculationError('Worker error: '+e.message);if(next&&!specialLaboratoryActive())startRun(next);};
  timer=setTimeout(()=>{if(id!==activeId||specialLaboratoryActive())return;const next=pendingRun;const latest=id===sequence&&!specialLaboratoryActive();worker?.terminate();worker=null;activeId=null;pendingRun=null;busy(false);if(latest)calculationError('Calculation exceeded 15 seconds. Reduce increments or check the model domain.');if(next&&!specialLaboratoryActive())startRun(next);},15000);
  worker.postMessage({id,kind:'laboratory',specification:s,catalogue:compiledCatalogue});
}
function simulate(s){
  if(specialLaboratoryActive())return;
  clearTimeout(updateTimer);updateTimer=null;
  try{
    if(!s){if(!$('controls').checkValidity()){scheduleUpdate();return;}s=specification();}
    s={...s,integration_settings:normalizeSettings(s.integration_settings)};validateSpec(s);invalidate();syncSliders();
    const job={s,id:sequence};
    if(activeId!==null)pendingRun=job;else startRun(job);
  }catch(error){invalidate();calculationError(error.message);}
}
function axisRange(values){
  if(!values.length)return [0,1];let lo=Infinity,hi=-Infinity;for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}if(lo===hi){const pad=Math.max(Math.abs(lo)*.05,1e-3);lo-=pad;hi+=pad;}else{const pad=(hi-lo)*.07;lo-=pad;hi+=pad;}return [lo,hi];
}
function numberLabel(v){if(Math.abs(v)<1e-10)return '0';return Number(v.toPrecision(3)).toString();}
function svgNode(name,attributes,text){const n=document.createElementNS('http://www.w3.org/2000/svg',name);for(const[k,v]of Object.entries(attributes))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function chart(id,xLabel,yLabel,predicted,measured=[],emptyMessage){
  const svg=$(id);svg.replaceChildren();svg.append(svgNode('title',{},yLabel+' versus '+xLabel));
  const left=62,top=27,w=392,h=211,all=[...predicted,...measured].filter(a=>a.every(Number.isFinite));
  const [xmin,xmax]=axisRange(all.map(p=>p[0])),[ymin,ymax]=axisRange(all.map(p=>p[1]));
  const x=v=>left+(v-xmin)/(xmax-xmin)*w,y=v=>top+h-(v-ymin)/(ymax-ymin)*h;
  for(let i=0;i<=4;i++){
    const yy=top+i*h/4,xx=left+i*w/4;
    svg.append(svgNode('line',{x1:left,y1:yy,x2:left+w,y2:yy,stroke:'#e6e9df','stroke-dasharray':'3 4'}),svgNode('text',{x:left-10,y:yy+4,'text-anchor':'end'},numberLabel(ymax-i*(ymax-ymin)/4)),svgNode('text',{x:xx,y:top+h+19,'text-anchor':'middle'},numberLabel(xmin+i*(xmax-xmin)/4)));
  }
  svg.append(svgNode('text',{x:left+w/2,y:282,'text-anchor':'middle',class:'axis-label'},xLabel.length>56?xLabel.slice(0,53)+'…':xLabel),svgNode('text',{x:12,y:top-12,class:'axis-label'},yLabel.length>60?yLabel.slice(0,57)+'…':yLabel));
  if(!all.length)svg.append(svgNode('text',{x:left+w/2,y:top+h/2,'text-anchor':'middle'},(emptyMessage||(id==='source-chart'?'No paired observations for these channels':'Preparing response…'))));
  if(predicted.length)svg.append(svgNode('polyline',{points:predicted.map(([a,b])=>`${x(a)},${y(b)}`).join(' '),fill:'none',stroke:'#bc643e','stroke-width':2,'stroke-linejoin':'round'}));
  const stride=Math.max(1,Math.ceil(measured.length/350));measured.filter((_,i)=>i%stride===0).forEach(([a,b])=>svg.append(svgNode('circle',{cx:x(a),cy:y(b),r:2,fill:'#547a95',opacity:.6,class:'experiment-point'})));
  if(predicted.length){
    const marker=svgNode('circle',{r:4,fill:'#bc643e',stroke:'#fff','stroke-width':2,visibility:'hidden'}),label=svgNode('text',{x:left+8,y:top+12,visibility:'hidden'});svg.append(marker,label);
    svg.onpointermove=e=>{const box=svg.getBoundingClientRect(),px=(e.clientX-box.left)/box.width*480;let nearest=predicted[0];for(const pt of predicted)if(Math.abs(x(pt[0])-px)<Math.abs(x(nearest[0])-px))nearest=pt;marker.setAttribute('cx',x(nearest[0]));marker.setAttribute('cy',y(nearest[1]));marker.setAttribute('visibility','visible');label.textContent=`${numberLabel(nearest[0])}, ${numberLabel(nearest[1])}`;label.setAttribute('visibility','visible');};
    svg.onpointerleave=()=>{marker.setAttribute('visibility','hidden');label.setAttribute('visibility','hidden');};
  }
}
function renderCharts(){
  if(specialLaboratoryActive())return;
  const visible=$('show-experiment').checked;
  describeExperiment();
  const native=experiment&&experiment.kind!=='experiment',view=$('source-record-view');view.hidden=!native;
  if(native){
    if(view.dataset.record!==experiment.id){
      for(const axis of ['x','y']){$('source-'+axis).replaceChildren(...experiment.columns.filter(c=>c.unit_status==='standardized').map(c=>new Option(c.name+' ['+c.unit+']',c.key)));const select=$('source-'+axis);if([...select.options].some(o=>o.value===experiment.source_plot[axis]))select.value=experiment.source_plot[axis];else if(axis==='y'&&select.options.length>1)select.selectedIndex=1;}
      view.dataset.record=experiment.id;
    }
    const x=experiment.columns.find(c=>c.key===$('source-x').value),y=experiment.columns.find(c=>c.key===$('source-y').value);
    $('source-chart').hidden=!x||!y;
    $('source-unit-note').textContent=x&&y?'Explicitly labelled units are converted to SI. Original units and conversion factors are retained in the record. Source signs are unchanged; these channels are not model overlays.':'No channels with verified units are available for plotting. See the source and data notes.';
    if(x&&y)chart('source-chart',x.name+' ['+x.unit+']',y.name+' ['+y.unit+']',[],measuredSeries(experiment,visible,x.key,y.key));
  }else delete view.dataset.record;
  const protocol=Number($('protocol').value),cycles=Number($('cycles').value);
  // Do not combine an old solver response with a newly selected test protocol.
  const matching=lastSpec?.protocol===protocol&&lastSpec?.model===model()?.id;
  const pts=matching?currentResult?.points||[]:[];
  const presentation=laboratoryPresentation(model()),pore=laboratoryPoreView(matching?currentResult:null,model(),protocol);
  $('pore-caption').textContent=pore.caption;
  const predicted={
    stress:pts.map(p=>[p.strain[0]*100,p.q_signed/1000]),
    path:pts.map(p=>[p.p/1000,p.q_signed/1000]),
    volume:pts.map(p=>[p.strain[0]*100,p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100]),
    pore:pore.points
  };
  for(const [key,axes] of Object.entries(presentation.axes)){
    const measured=comparisonSeries(experiment,visible,key,protocol,cycles,model());
    chart(key+'-chart',axes.xLabel,axes.yLabel,predicted[key],measured,key==='pore'?pore.caption:undefined);
    const panel=$(key+'-chart').closest('.chart-panel');
    panel.querySelector('.measured-key').hidden=!measured.length;
    panel.querySelector('.measurement-note').textContent=experiment&&experiment.kind==='experiment'&&!measured.length?(visible?'No compatible measured channel pair for these axes.':'Measurements hidden.') : '';
  }
}
function catalogueCards(){
  const query=$('search').value.toLowerCase(),filter=$('availability').value,grid=$('catalogue-grid');grid.replaceChildren();
  for(const entry of catalogue){const spec=models.find(x=>x.id===entry.id),executable=!!spec||!!timedLaboratoryRoute(entry)||entry.id===j2View?.modelId||(timedView?.supports(entry.id)&&(entry.timed_laboratory==='index.html'||entry.path_laboratory==='index.html'||entry.implicit_path_laboratory==='index.html'||entry.material_laboratory==='index.html'));if(filter==='executable'&&!executable||filter==='candidate'&&executable)continue;if(!(entry.name+' '+entry.family+' '+entry.id).toLowerCase().includes(query))continue;
    const card=element('article',undefined,'catalogue-card'),meta=element('div',undefined,'catalogue-card-meta');
    meta.append(element('span',entry.family,'catalogue-family'),element('span',executable?'Available to test':'Research candidate','catalogue-availability'+(executable?' available':'')));
    const heading=element('h2'),open=element('a',entry.name,'catalogue-open');open.href=catalogueModelHash(entry.id);open.setAttribute('aria-haspopup','dialog');heading.append(open);
    const hint=element('span',undefined,'catalogue-card-hint');hint.setAttribute('aria-hidden','true');hint.append(element('span','View details'),element('span','↗','catalogue-arrow'));
    card.append(meta,heading,hint);
    grid.append(card);
  }
  const count=grid.children.length;$('catalogue-results').textContent=count+' '+(count===1?'model':'models')+(query||filter!=='all'?' found':'');
  if(!count)grid.append(element('p','No matching models. Try another name or availability.','catalogue-empty'));
}
function refreshCatalogueStatus(entry,spec){
  $('catalogue-detail-status').textContent=entry.id===j2View?.modelId?'Approved scope · independent agent review':timedView?.supports(entry.id)?(entry.material_laboratory?'Approved bounded scope · strain-increment laboratory':entry.implicit_path_laboratory?'Approved bounded scope · implicit strain-path laboratory':entry.path_laboratory?'Approved bounded scope · controlled-path laboratory':'Approved bounded scope · physical-time laboratory'):registeredModelReview(entry.id)?'Approved scope · independent agent review':spec?'Available to test · '+spec.status:timedLaboratoryRoute(entry)?'Available to test · approved physical-time scope':'Research candidate';
}
function showCatalogueModel(entry,spec){
  const timedRoute=timedLaboratoryRoute(entry);
  const dialog=$('catalogue-dialog'),body=$('catalogue-detail-body');body.replaceChildren();
  $('catalogue-detail-title').textContent=entry.name;$('catalogue-detail-family').textContent=entry.family;
  refreshCatalogueStatus(entry,spec);
  $('catalogue-detail-status').className='catalogue-availability'+(spec||timedRoute||entry.id===j2View?.modelId||timedView?.supports(entry.id)?' available':'');
  body.append(element('p',recordedDescription(entry.note||spec?.description||'Bibliographic and formulation review pending.',entry.id,evidenceIndex),'catalogue-detail-note'));
  if(entry.id===j2View?.modelId){body.append(element('p','The exact approved formulation, complete state and all-six-component controls are available in the main laboratory. Experimental validation is absent.'));}else if(entry.implicit_path_laboratory&&timedView?.supports(entry.id)){body.append(element('p','The main laboratory exposes the original complete 1975 elastoplastic law through a bounded implicit strain-path realization, explicit Table 1 preparation and complete stress/history/work state. Total mechanical Cauchy stress; no pore-pressure law or experimental validation.'));const links=element('p');for(const [label,path] of [['Exact definition','engine-implicit-path/'+entry.id+'.json'],['Independent scientific checklist','engine-implicit-path/review.json'],['Approval and limitations','engine-implicit-path/approval.json']]){const a=element('a',label+' ↗');a.href='./'+path;a.target='_blank';a.rel='noopener';links.append(a,document.createTextNode(' · '));}body.append(links);}else if(entry.path_laboratory&&timedView?.supports(entry.id)){body.append(element('p','The main laboratory exposes dimensionless shear progress, complete initial history and linearly changing stress controls for the original drained active axial law. Experimental comparison is unavailable.'));}else if(timedRoute){const section=element('section');section.append(element('h3','Physical-time formulation'),element('p','Open the dedicated laboratory for supported controls, conventions and source/review links.'));body.append(section);}else body.append(formulationSection(document,spec,{evidenceIndex}));
  if(typeof entry.dossier==='string'&&/^docs\/models\/[a-z0-9-]+\.md$/.test(entry.dossier)){const link=element('a','Source, numerics and limitations dossier ↗');link.href='./'+entry.dossier+'.html';link.target='_blank';link.rel='noopener';body.append(link);}
  if(!spec&&!timedRoute&&entry.id!==j2View?.modelId&&!timedView?.supports(entry.id)){const next=element('section');next.append(element('h3','Development notes'),element('p',entry.capability_gap||'Source extraction, declarative transcription and numerical verification pending.'));body.append(next);}
  const sources=spec?[...spec.sources]:entry.discovery_url?[{url:entry.discovery_url,role:'Discovery reference',locator:'Bibliographic review pending'}]:[];
  sources.push(...entry.research_sources||[],...entry.catalogue_sources||[]);
  if(sources.length){
    const section=element('section'),list=element('ul',undefined,'catalogue-references');section.append(element('h3','Sources & references'),list);
    for(const source of sources){
      const url=new URL(source.url);if(!['https:','http:'].includes(url.protocol))continue;
      const row=element('li'),link=element('a',source.role+' ↗');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';row.append(link,element('p',source.locator));list.append(row);
    }
    body.append(section);
  }
  body.append(evidenceSection(document,entry.id,evidenceIndex,evidenceState));
  body.append(applicabilitySection(document,entry.id,applicabilityMatrix,applicabilityState));
  if(spec){const definition=element('p',undefined,'catalogue-definition');definition.append(definitionLink(entry.id));body.append(definition);}
  $('catalogue-detail-id').textContent=entry.id;
  $('catalogue-permalink').href=catalogueModelHash(entry.id);
  const timed=timedView?.supports(entry.id)&&(entry.timed_laboratory==='index.html'||entry.path_laboratory==='index.html'||entry.implicit_path_laboratory==='index.html'||entry.material_laboratory==='index.html');
  const explore=$('catalogue-explore');explore.hidden=!spec&&!timedRoute&&!timed&&entry.id!==j2View?.modelId;explore.onclick=()=>{if(timedRoute){location.href=timedRoute;return;}dialog.close();if(activateLaboratoryModel(entry.id))location.hash='laboratory?model='+encodeURIComponent(entry.id);$('model').focus({preventScroll:true});};
  if(!dialog.open)dialog.showModal();body.scrollTop=0;
}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function setProtocol(){
  updateControlSupport();
  const input=$('target'),stress=$('protocol').value==='3',wasStress=input.dataset.mode==='stress';
  $('target-label').textContent=stress?'Deviator stress (kPa)':'Axial strain (%)';updateScopeLabels();
  if(stress!==wasStress)input.value=stress?'20':'1';
  input.dataset.mode=stress?'stress':'strain';input.min=stress?'-100000':'-10';input.max=stress?'100000':'10';
  document.querySelector('[data-for="target"]')?.remove();
  addSlider(input,$('target-label').textContent,stress?-500:-10,stress?500:10);syncSliders();
}
async function readFile(file){if(!file)return null;if(file.size>10*1024*1024)throw Error('File exceeds the 10 MB limit.');return JSON.parse(await file.text());}
function applyRunSpecification(imported){
  if(specialLaboratoryActive())return;
    const s={...imported,integration_settings:normalizeSettings(imported.integration_settings)},m=validateSpec(s);cancel('');$('loading-version').value=s.loading?'exact':'legacy';setNumericalValues(s.integration_settings);$('model').value=m.id;populate({loadExample:false});Object.keys(m.parameters).forEach((n,i)=>{const input=$('param-'+n);input.value=s.parameters[i]/Number(input.dataset.factor);});
    $('confinement').value=s.initial[1]/1000;$('stress-ratio').value=s.initial[0]/s.initial[1];let offset=6;
    for(const f of m.state.slice(1)){const size=f.shape==='sym'?6:1;if(persistentState(f)){const input=$('state-'+f.name);input.value=size===6?s.initial.slice(offset,offset+6).join(','):s.initial[offset]/Number(input.dataset.factor);}offset+=size;}
    $('protocol').value=s.protocol;setProtocol();$('target').value=s.target/(s.protocol===3?1000:.01);$('steps').value=s.steps;
    if(![...$('cycles').options].some(o=>Number(o.value)===s.cycles))$('cycles').append(new Option(s.cycles+' sinusoidal cycles',s.cycles));$('cycles').value=s.cycles;
    refreshExperimentFilter();location.hash='laboratory';simulate(s);
}
async function importRun(file){
  const requested=sequence;
  try{if(!file)return;if(file.size>10*1024*1024)throw Error('File exceeds the 10 MB limit.');const text=await file.text();if(requested!==sequence||specialLaboratoryActive())return;applyRunSpecification(parseLaboratoryDocument(text,compiledCatalogue));}
  catch(e){if(requested===sequence&&!specialLaboratoryActive())toast(e.message);}
}
function describeExperiment(){
  if(specialLaboratoryActive())return;
  $('match-experiment').disabled=!experiment||experiment.kind!=='experiment'||!supportsEffectiveExperiment(model());
  const sourceNotes=Array.isArray(experiment?.warnings)?experiment.warnings:[];
  $('experiment-details').hidden=!sourceNotes.length;$('experiment-warnings').textContent=sourceNotes.join(' ');
  if(!experiment){$('experiment-status').textContent=$('experiment-select').value?'Loading selected measurements…':(builtinExperiments.length?($('experiment-select').options.length>1?'Select a protocol-matched test to compare measured and predicted behaviour.':'No measurement overlays match this protocol and loading path. You can browse source records or load your own measurements.'):'No built-in tests are available in this build. You can compare your own measurements below.');return;}
  const stress=experiment.initial?.effective_stress,p=Array.isArray(stress)?stress.slice(0,3).reduce((a,b)=>a+b,0)/3000:null,e=experiment.initial?.void_ratio;
  const label=[experiment.kind==='test-summary'?'Test summary':null,experiment.id,experiment.material,experiment.protocol,Number.isFinite(p)?`initial p′ ${numberLabel(p)} kPa`:null,Number.isFinite(e)?`e₀ ${numberLabel(e)}`:'e₀ unavailable'].filter(Boolean).join(' · ');
  const notes=[`${experiment.rows.length} measured rows. ${$('show-experiment').checked&&compatibleExperiment(experiment,Number($('protocol').value),Number($('cycles').value),model())?'Matching measured channel pairs are overlaid.':'No model overlay is shown.'} Simulation settings are unchanged.`,...(sourceNotes.length?['Source limitations apply; see data notes.']:[])];
  if(experiment.kind!=='experiment'){
    notes[0]=`${experiment.rows.length} source rows. ${$('show-experiment').checked?'Source chart shown.':'Source chart hidden.'} Standardized units where verified; no model overlay.`;
    $('experiment-status').textContent=label+'. '+notes.join(' ');return;
  }
  if(!supportsEffectiveExperiment(model()))notes.push('Normalized overlays and initial-state matching require an effective-stress model. Source measurements remain available.');
  if(lastSpec&&supportsEffectiveExperiment(model())){
    const expected=lastSpec.protocol===1?'drained-triaxial':[2,3].includes(lastSpec.protocol)?'undrained-triaxial':null;
    if(experiment.protocol!==expected)notes.push('Loading protocol differs from the plotted simulation.');
    if(Array.isArray(stress)&&Math.abs(stress[1]-lastSpec.initial[1])>Math.max(100,.02*Math.abs(stress[1])))notes.push('Initial radial effective stress differs from the plotted simulation.');
    const m=model();let offset=0;for(const f of m.state){if(f.name==='e'&&Number.isFinite(e)&&Math.abs(lastSpec.initial[offset]-e)>.001)notes.push('Initial void ratio differs from the plotted simulation.');offset+=f.shape==='sym'?6:1;}
  }
  $('experiment-status').textContent=label+'. '+notes.join(' ');
}
function experimentOptions(selected=''){
  if(specialLaboratoryActive())return;
  const options=[new Option('No measurements selected','')];
  const groups=new Map();
  const query=$('experiment-search').value.trim().toLowerCase();
  const browse=$('browse-source-records').checked,protocol=Number($('protocol').value),cycles=Number($('cycles').value);
  const relevant=entry=>browse||compatibleExperiment(entry,protocol,cycles,model());
  const count=builtinExperiments.filter(entry=>compatibleExperiment(entry,protocol,cycles,model())).length;
  $('experiment-filter-note').textContent=!supportsEffectiveExperiment(model())?'Normalized overlays require an effective-stress model. Browse source records to view measurements.':`${count} protocol-matched tests · ${protocolNames[protocol]} · ${cycles>0?'reversing':'monotonic'} loading. Matching plot axes permit overlays. Other source records are available below.`;
  for(const entry of [...builtinExperiments].filter(relevant).sort((a,b)=>a.material.localeCompare(b.material)||a.protocol.localeCompare(b.protocol)||a.id.localeCompare(b.id,undefined,{numeric:true}))){if(query&&'builtin:'+entry.id!==selected&&!(entry.id+' '+entry.material+' '+entry.protocol).toLowerCase().includes(query))continue;const key=entry.material+' · '+entry.protocol;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(entry);}
  for(const [label,entries] of groups){
    const group=element('optgroup');group.label=label.replace('drained-triaxial','drained triaxial').replace('undrained-triaxial','undrained triaxial');
    for(const entry of entries){const stress=entry.initial?.effective_stress,p=Array.isArray(stress)?stress[1]/1000:null,e=entry.initial?.void_ratio;
      group.append(new Option([entry.kind==='test-summary'?'Summary':null,entry.id.replace(/^GEOLAB-[A-Z]+-/,'').replace('KFS-',''),Number.isFinite(p)?numberLabel(p)+' kPa':null,Number.isFinite(e)?'e₀ '+numberLabel(e):null].filter(Boolean).join(' · '),'builtin:'+entry.id));}
    options.push(group);
  }
  if(experiments.length){const group=element('optgroup');group.label='Your local measurements';experiments.forEach((e,i)=>{if(relevant(e))group.append(new Option(e.id+' · '+e.protocol,'local:'+i));});options.push(group);}
  $('experiment-select').replaceChildren(...options);$('experiment-select').disabled=false;$('experiment-select').value=selected;
  if(selected&&$('experiment-select').value!==selected){$('experiment-select').value='';++experimentLoadSequence;showExperiment(null);}
}
function showExperiment(data){
  if(specialLaboratoryActive())return;
  experiment=data;$('retry-experiment').hidden=true;
  $('match-experiment').hidden=!!data&&data.kind!=='experiment';
  $('show-experiment').disabled=!data;$('show-experiment').checked=!!data;$('match-experiment').disabled=!data||data.kind!=='experiment'||!supportsEffectiveExperiment(model());
  $('match-experiment').textContent=data&&!data.initial?.effective_stress&&!Number.isFinite(data.initial?.void_ratio)?'Use drainage protocol':'Match available test inputs';
  const link=$('experiment-source'),url=data?.provenance?.source_url;link.hidden=true;
  if(typeof url==='string'&&/^https?:\/\//i.test(url)){link.href=url;link.hidden=false;}
  const license=$('experiment-license'),licenseUrl=data?.provenance?.license_url;license.hidden=true;
  if(typeof licenseUrl==='string'&&/^https?:\/\//i.test(licenseUrl)){license.href=licenseUrl;license.textContent=data.provenance.license+' ↗';license.hidden=false;}
  $('experiment-attribution').textContent=data?.provenance?.attribution||'';$('experiment-attribution').hidden=!data?.provenance?.attribution;
  renderCharts();
}
async function selectExperiment(){
  if(specialLaboratoryActive())return;
  const revision=++experimentLoadSequence,choice=$('experiment-select').value;showExperiment(null);
  if(!choice)return;
  try{
    let data;
    if(choice.startsWith('local:'))data=experiments[Number(choice.slice(6))];
    else{
      const entry=builtinExperiments.find(e=>'builtin:'+e.id===choice);if(!entry)throw Error('Selected test is unavailable.');
      data=experimentCache.get(entry.id);
      if(!data){data=await fetchExperiment(entry);experimentCache.set(entry.id,data);}
    }
    if(revision===experimentLoadSequence&&!specialLaboratoryActive()&&choice===$('experiment-select').value)showExperiment(data);
  }catch(error){if(revision===experimentLoadSequence&&!specialLaboratoryActive()){$('experiment-status').textContent=error.message;$('retry-experiment').hidden=false;}}
}
async function loadExperimentCatalogue(){
  try{
    const response=await fetch('./experiments/index.json');if(!response.ok)throw Error('The experiment catalogue could not be loaded. Reload to try again.');
    const manifest=await response.json();
    if(manifest.schema_version!=='0.1'||!Array.isArray(manifest.experiments))throw Error('Unsupported experiment catalogue.');
    builtinExperiments=manifest.experiments;
    if(!specialLaboratoryActive()){experimentOptions($('experiment-select').value);describeExperiment();}
  }catch(error){if(!specialLaboratoryActive()){experimentOptions($('experiment-select').value);$('experiment-status').textContent=error.message;$('retry-experiment').hidden=false;}}
}
function matchExperiment(){
  if(specialLaboratoryActive())return;
  if(!experiment)return;
  if(!supportsEffectiveExperiment(model())){toast('Initial-state matching requires an effective-stress model.');return;}
  const stress=experiment.initial?.effective_stress,e=experiment.initial?.void_ratio;
  if(experiment.protocol==='drained-triaxial')$('protocol').value='1';
  else if(experiment.protocol==='undrained-triaxial')$('protocol').value='2';
  if(comparisonMetadata(experiment).loading==='monotonic')$('cycles').value='0';
  setProtocol();
  if(Array.isArray(stress)&&stress[1]>0){$('confinement').value=stress[1]/1000;$('stress-ratio').value=stress[0]/stress[1];}
  if(Number.isFinite(e)&&$('state-e'))$('state-e').value=e;
  refreshExperimentFilter();scheduleUpdate();
}
async function loadExperiments(files){
  const id=++experimentLoadSequence;
  try{
    const list=Array.from(files||[]);if(!list.length)return;if(list.length>32)throw Error('Load at most 32 files at once.');
    if(list.reduce((n,f)=>n+f.size,0)>50*1024*1024)throw Error('Selected files exceed 50 MB.');
    const loaded=[];for(const file of list){
      if(file.size>25*1024*1024)throw Error('A file exceeds 25 MB.');
      const text=await file.text(),data=/\.dat$/i.test(file.name)?normalizeWichtmann(text,file.name):validateExperiment(JSON.parse(text));
      if(loaded.some(x=>x.id===data.id))throw Error('Duplicate experiment ID: '+data.id);loaded.push(data);
    }
    if(id!==experimentLoadSequence||specialLaboratoryActive())return;
    experiments=loaded;const first=loaded.findIndex(e=>compatibleExperiment(e,Number($('protocol').value),Number($('cycles').value),model()));experimentOptions(first<0?'':'local:'+first);$('clear-experiments').disabled=false;selectExperiment();
  }catch(e){if(id===experimentLoadSequence&&!specialLaboratoryActive())toast(e.message);}
  finally{if(id===experimentLoadSequence&&!specialLaboratoryActive())$('experiment-file').value='';}
}
window.addEventListener('hashchange',route);$('controls').onsubmit=e=>{e.preventDefault();simulate();};$('cancel-button').onclick=()=>cancel();$('model').onchange=()=>{if(activateLaboratoryModel($('model').value))location.hash='laboratory?model='+encodeURIComponent($('model').value);};$('protocol').onchange=()=>{setProtocol();refreshExperimentFilter();scheduleUpdate();};
$('cycles').onchange=()=>{refreshExperimentFilter();const minimum=16*Number($('cycles').value);if(Number($('steps').value)<minimum)$('steps').value=minimum;scheduleUpdate();};
$('load-model-example').onclick=()=>{try{cancel('');populate();simulate();}catch(e){toast(e.message);}};
$('reset').onclick=()=>{cancel('');HTMLFormElement.prototype.reset.call($('controls'));populate();setProtocol();refreshExperimentFilter();simulate();};$('equations-button').onclick=()=>{if(j2View?.showEquations()||timedView?.showEquations())return;$('equations').open=true;$('equations').scrollIntoView({behavior:'smooth'});};
$('import-run').onclick=()=>$('run-file').click();$('run-file').onchange=e=>importRun(e.target.files[0]);$('experiment-file').onchange=e=>loadExperiments(e.target.files);
function refreshExperimentFilter(){experimentOptions($('experiment-select').value);renderCharts();}
$('browse-source-records').onchange=refreshExperimentFilter;
$('show-experiment').onchange=renderCharts;$('experiment-select').onchange=selectExperiment;
$('source-x').onchange=renderCharts;$('source-y').onchange=renderCharts;
$('experiment-search').oninput=()=>experimentOptions($('experiment-select').value);
$('match-experiment').onclick=matchExperiment;
$('retry-experiment').onclick=()=>{if($('experiment-select').value)selectExperiment();else{ $('retry-experiment').hidden=true;loadExperimentCatalogue(); }};
$('clear-experiments').onclick=()=>{const local=$('experiment-select').value.startsWith('local:');experiments=[];$('clear-experiments').disabled=true;$('experiment-file').value='';if(local){++experimentLoadSequence;showExperiment(null);}experimentOptions(local?'':$('experiment-select').value);};
$('controls').addEventListener('input',scheduleUpdate);
$('retry-button').onclick=()=>simulate();
numericalControls();setProtocol();addSlider($('confinement'),'Radial effective stress (kPa)',1,10000);addSlider($('stress-ratio'),'Axial / radial stress ratio',.01,10);
$('export-run').onclick=()=>download(lastSpec.model+'-run.json',JSON.stringify(createLaboratoryDocument(lastSpec,currentResult,compiledCatalogue),null,2),'application/json');
$('export-csv').onclick=()=>download(lastSpec.model+'-results.csv',laboratoryDocumentCSV(lastSpec,currentResult,compiledCatalogue),'text/csv');
$('search').oninput=$('availability').onchange=catalogueCards;
$('catalogue-close').onclick=closeCatalogue;
// Direct links have no opening control for the native dialog to restore.
$('catalogue-dialog').addEventListener('close',restoreCatalogueFocus);
$('catalogue-dialog').addEventListener('cancel',event=>{event.preventDefault();closeCatalogue();});
$('catalogue-dialog').onclick=e=>{if(e.target===$('catalogue-dialog')){const box=e.target.getBoundingClientRect();if(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom)closeCatalogue();}};
try{
  const [response,manifest,support]=await Promise.all([fetch('./models.json'),fetch('./catalogue.json'),fetch('./laboratory-control-support.json')]);if(!response.ok||!manifest.ok||!support.ok)throw Error('Catalogue could not be loaded.');
  const definitions=await response.json();compiledCatalogue=definitions;catalogueHash=definitions.sha256;models=definitions.models;catalogue=(await manifest.json()).models;controlSupport=validateSupport(await support.json(),definitions);
  models.forEach(m=>$('model').append(new Option(m.name,m.id)));$('model').value='hypoplastic-sand-vw96';$('catalogue-count').textContent=catalogue.length;$('build-hash').textContent='Catalogue SHA-256: '+catalogueHash;
  laboratoryExamples=setupLaboratoryExamples({catalogue:definitions,getModel:model,applySpecification:s=>{if(!specialLaboratoryActive())applyRunSpecification(s);},onError:toast});
  populate();timedView=createLaboratoryControllerRouter([setupTimedLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupSlsLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupKelvinVoigtLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupOrthotropicLaboratory({cancelOrdinary:()=>cancel('')}),setupPathLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupMaxwellLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupImplicitPathLaboratory({chart,cancelOrdinary:()=>cancel('')})]);j2View=setupJ2Laboratory({cancelOrdinary:()=>cancel('')});catalogueCards();route({initial:true});simulate();loadExperimentCatalogue();loadEvidenceIndex();loadApplicability();
}catch(e){toast('Initialization failed: '+e.message);$('run-state').textContent='Unable to initialize';}
