// Catalogue-driven models for one fixed experiment; no constitutive equations here.
import {parseRecordedJSON} from './recorded.mjs';
import {parseRecordedDocument,createRecordedDocument} from './recorded-document.mjs';
import {supportsEffectiveExperiment} from './experiments.mjs';
import {normalizeSettings,settingFields} from './numerics.mjs';
import {controlBits} from './loading.mjs';
import {validateReplayRecord} from './ensemble-experiments.mjs';
import {persistentState,temporaryStateComponents} from './state-contract.mjs';
export const experimentId='OPARA-TXCD-100';
// Preserve historical ordering and sweeps; membership comes from availableModels.
const modelIds=['linear-elastic','drucker-prager','modified-cam-clay'];
export const sweepParameters={'linear-elastic':['E','nu'],'drucker-prager':['M','Md'],'modified-cam-clay':['M','kappa']};
const initialVariations={'linear-elastic':{E:[24e6,36e6],nu:[.2,.3]},'drucker-prager':{M:[.96,1.44],Md:[.16,.24]},'modified-cam-clay':{M:[.96,1.44],kappa:[.032,.048]}};
export const stable=value=>JSON.stringify(value&&typeof value==='object'?Array.isArray(value)?value.map(v=>JSON.parse(stable(v))):Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(stable(value[k]))])):value);
const require=(v,m)=>{if(!v)throw Error(m);};
const finite=v=>typeof v==='number'&&Number.isFinite(v);
function keys(value,expected){return value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join(',')===[...expected].sort().join(',');}
export function validateExperiment(record){
 if(record?.version==='atlas-ensemble-experiment-0.2')return validateReplayRecord(record);
 require(record?.version==='atlas-ensemble-experiment-0.1'&&record.id===experimentId&&record.protocol==='drained-triaxial','Unsupported ensemble experiment.');
 require(record.conventions?.stress==='compression-positive'&&record.conventions?.strain==='compression-positive'&&record.conventions?.stress_unit==='Pa'&&record.conventions?.strain_unit==='1','Experiment conventions differ.');
 require(record.source_asset_sha256?.match(/^[a-f0-9]{64}$/)&&record.provenance?.archive_sha256==='49681ae77388fb0f3f081cbebfd263cb328b9bc678ed5a376a19e6c4dba82b35'&&record.provenance?.member_sha256==='787d207c982beedf99e96b054899ba8069e4261f80fba024fdbc3549745b27cd','Experiment source identity differs.');
 require(Array.isArray(record.rows)&&record.rows.length===1438,'Expected all 1438 source observations.');
 let previous=-Infinity;
 for(const r of record.rows){require(['axial_strain','radial_effective_stress','q','volumetric_strain'].every(k=>finite(r[k]))&&r.axial_strain>=previous&&r.radial_effective_stress>0,'Invalid or reordered source observation.');previous=r.axial_strain;}
 require(stable(record.initial?.effective_stress)===stable([103720,103720,103720,0,0,0])&&record.initial?.void_ratio===.416,'Experiment initial state differs.');
 require(record.rows[0].axial_strain===0&&record.rows[0].radial_effective_stress===103720&&record.rows[0].q===0,'Source row zero contradicts initialization.');
 const rows=record.rows.filter(r=>r.axial_strain<=.01);
 require(rows.length===95&&rows.at(-1).axial_strain===.00992,'Source window differs.');
 require(record.rows.at(-1).axial_strain===.1599,'Source endpoint differs.');return record;
}
// A path-order coordinate cannot represent physical time. Total-stress and
// dedicated engines cannot be substituted for this effective-stress replay.
export function modelExclusion(model){
 if(!supportsEffectiveExperiment(model))return 'Requires effective Cauchy stress in the recorded-replay engine.';
 if(model.schema_version==='0.3'&&(model.formulation?.time_dependence!=='strain_path'||model.formulation?.strain_sign!=='compression_positive'))return 'Requires a compression-positive strain-path formulation; elapsed time is unavailable.';
 try{historyFields(model);}catch(error){return error.message;}
 return '';
}
export function historyFields(model){
 return model.state.slice(1).flatMap(field=>{
  if(!persistentState(field)){temporaryStateComponents(field);return [];}
  if(['e','v'].includes(field.name)&&field.shape==='scalar')return [];
  const values=field.shape==='sym'?field.initial:[field.initial];
  require(['scalar','sym'].includes(field.shape)&&values?.length===(field.shape==='sym'?6:1)&&values.every(finite),'Starting history requires explicit finite scalar or Mandel tensor defaults.');
  return values.map((value,i)=>({key:field.shape==='sym'?field.name+'['+i+']':field.name,value,unit:field.unit}));
 });
}
export function variedParameters(model){return sweepParameters[model.id]||Object.keys(model.parameters).filter(k=>!['p_ref','pref','p_scale','sigma_star','pa','j2_floor','lode_allowance'].includes(k)).slice(0,2);}
export function availableModels(catalogue){
 return catalogue.models.filter(model=>!modelExclusion(model)).sort((a,b)=>{
  const rank=id=>modelIds.includes(id)?modelIds.indexOf(id):-1;
  return (rank(a.id)<0?modelIds.length:rank(a.id))-(rank(b.id)<0?modelIds.length:rank(b.id))||a.id.localeCompare(b.id);
 });
}
export function defaultConfigurations(catalogue){
 return availableModels(catalogue).map(model=>({model:model.id,enabled:true,parameters:Object.fromEntries(Object.entries(model.parameters).map(([k,f])=>[k,f.default])),history:Object.fromEntries(historyFields(model).map(f=>[f.key,f.value])),variations:structuredClone(initialVariations[model.id]||Object.fromEntries(variedParameters(model).map(k=>[k,[]])))}));
}
function checkModel(model){require(model,'Model is absent from this compiled catalogue.');const reason=modelExclusion(model);require(!reason,reason);}
function initialCheck(id,p,history,record){
 if(id==='linear-elastic'||id==='drucker-prager')require(p.E>0&&p.nu>-1&&p.nu<.5,'Elastic modulus or Poisson ratio is inadmissible.');
 if(id==='drucker-prager')require(p.M>=0&&p.Md>=0&&p.c>=0,'Drucker–Prager slopes/intercept must be nonnegative.');
 if(id==='modified-cam-clay'){
  require(p.lambda_c>p.kappa&&p.kappa>0&&p.nu>-1&&p.nu<.5,'MCC requires λ > κ > 0 and −1 < ν < 0.5.');
  require(finite(history.pc)&&history.pc>0&&((record.initial.effective_stress[0]-record.initial.effective_stress[1])**2+p.M*p.M*((record.initial.effective_stress[0]+2*record.initial.effective_stress[1])/3)*((record.initial.effective_stress[0]+2*record.initial.effective_stress[1])/3-history.pc))/(p.p_ref*p.p_ref)<=1e-8,'MCC starting stress lies outside its assumed yield surface.');
 }
}
export function makeStudy(record,catalogue,configurations,lastRow=record.rows.length-1){
 validateExperiment(record);
 require(catalogue?.schema_version==='0.1'&&/^[a-f0-9]{64}$/.test(catalogue.sha256)&&Array.isArray(catalogue.models),'Exact compiled catalogue required.');
 require(Array.isArray(configurations)&&configurations.length>0&&configurations.length<=catalogue.models.length&&new Set(configurations.map(c=>c.model)).size===configurations.length,'Expected unique catalogue model configurations.');
 // The original prefix remains available only for exact replay of saved studies.
 require((record.id===experimentId&&lastRow===94)||lastRow===record.rows.length-1,'Unsupported experiment window.');
 const sourceRows=record.rows.slice(0,lastRow+1),jobs=[],definitions=[];
 const undrained=record.protocol==='undrained-triaxial';
 const controls=Array.from({length:6},(_,i)=>({kind:i===1||i===2?'stress':'strain',coefficients:Array.from({length:6},(_,j)=>Number(i===j))}));
 if(undrained){controls[1]={kind:'strain',coefficients:[1,1,1,0,0,0]};controls[2]={kind:'stress',coefficients:[0,1,-1,0,0,0]};}
 const path={version:'experimental-recorded-path-0.1',coordinate:{name:'source_row_index',unit:'1',meaning:'path_order'},initial_strain:[0,0,0,0,0,0],controls,knots:sourceRows.map((r,i)=>({coordinate:i,targets:[r.axial_strain-record.rows[0].axial_strain,...(undrained?[0,0]:[r.radial_effective_stress,r.radial_effective_stress]),0,0,0]}))};
 for(const config of configurations){
  require(keys(config,['model','enabled','parameters','history','variations'])&&typeof config.enabled==='boolean','Invalid model configuration.');
  require(catalogue.models.some(m=>m.id===config.model),'Model is absent from this compiled catalogue.');
  if(!config.enabled)continue;
  const model=catalogue.models.find(m=>m.id===config.model);checkModel(model);definitions.push(structuredClone(model));
  require(keys(config.parameters,Object.keys(model.parameters))&&keys(config.history,historyFields(model).map(f=>f.key))&&keys(config.variations,variedParameters(model)),'Explicit named parameters, history and variations required.');
  require(Object.values(config.parameters).every(finite)&&Object.values(config.history).every(finite),'Baseline parameters and history must be finite numbers.');
  const candidates=[{label:'Baseline',change:null,parameters:config.parameters,id:config.model+':baseline'}];
  for(const name of variedParameters(model)){
   const values=config.variations[name];require(Array.isArray(values)&&values.length<=6&&values.every(finite),'Use at most six finite values per varied parameter.');
   for(const value of [...new Set(values)].filter(v=>v!==config.parameters[name]))candidates.push({label:name+' = '+value,change:{parameter:name,value},parameters:{...config.parameters,[name]:value},id:config.model+':'+name+':'+controlBits(value)});
  }
  for(const candidate of candidates){
   let error=null,specification=null;
   try{
    for(const [name,field] of Object.entries(model.parameters)){const v=candidate.parameters[name];require(finite(v)&&v>=field.min&&v<=field.max,name+' is outside declared bounds.');}
    if(model.parameters.p_ref)require(candidate.parameters.p_ref===model.parameters.p_ref.default,'Numerical reference scale must remain fixed.');
    initialCheck(model.id,candidate.parameters,config.history,record);
    const initial=model.state.flatMap(field=>{
     if(field.name==='sigma')return [...record.initial.effective_stress];
     if(!persistentState(field))return temporaryStateComponents(field);
     if(field.shape==='scalar'&&field.name==='e')return [record.initial.void_ratio];
     if(field.shape==='scalar'&&field.name==='v')return [1+record.initial.void_ratio];
     return field.shape==='sym'?Array.from({length:6},(_,i)=>config.history[field.name+'['+i+']']):[config.history[field.name]];
    });
    specification={version:'experimental-recorded-run-0.1',model:model.id,parameters:Object.keys(model.parameters).map(k=>candidate.parameters[k]),initial,path:structuredClone(path),integration_settings:Object.fromEntries(settingFields.map(f=>[f.key,normalizeSettings()[f.key]])),control_settings:{control_tolerance:1e-10,max_iterations:30,max_backtracks:10,max_material_trials:20000,finite_difference_step:1e-7}};
    parseRecordedDocument(JSON.stringify(specification),catalogue);
   }catch(e){error=e.message;specification=null;}
   jobs.push({id:candidate.id,model:model.id,label:candidate.label,change:candidate.change,parameters:structuredClone(candidate.parameters),history:structuredClone(config.history),specification,status:error?'rejected':'queued',message:error||'',result:null});
  }
 }
 require(jobs.length>0&&jobs.length<=Math.max(39,catalogue.models.length*13),'Select at least one available model (at most 13 runs per catalogue model).');
 return structuredClone({version:'atlas-ensemble-study-0.1',experiment:{id:record.id,source_asset_sha256:record.source_asset_sha256,archive_sha256:record.provenance.archive_sha256,member_sha256:record.provenance.member_sha256,window:{first_row:0,last_row:lastRow,max_axial_strain:record.id===experimentId&&lastRow===94?.01:sourceRows.at(-1).axial_strain,last_acquired_strain:sourceRows.at(-1).axial_strain},control:undrained?'constant-volume-axisymmetric-effective-stress':'direct-author-membrane-corrected-radial-effective-stress',strain_origin:'first-observation',initial:record.initial,limitations:[undrained?'Idealized undrained replay: zero volumetric strain and equal lateral effective stresses; measured pore pressure and effective radial stress are comparison outputs.':'Conditional replay: measured volumetric strain contributes to membrane-corrected radial input.','No consolidation history is inferred; MCC pc is an explicit unmeasured assumption.','Illustrative parameters; no calibration, applicability or experimental validation claim.']},catalogue_hash:catalogue.sha256,model_definitions:definitions,configurations,jobs});
}
export function resultSeries(job,channel,record){
 if(!job.result)return [];
 return job.result.points.map((p,i)=>{const axial=(p.strain[0]+(record?.rows[0].axial_strain||0))*100,q=(p.state[0]-p.state[1])/1000;
  if(channel==='path')return [(p.state[0]+p.state[1]+p.state[2])/3000,q];
  if(channel==='pore'){if(record?.protocol!=='undrained-triaxial'||!Number.isFinite(record.rows[i]?.cell_pressure))return null;return [axial,(record.rows[i].cell_pressure-record.rows[0].cell_pressure-p.state[1]+record.initial.effective_stress[1])/1000];}
  return [axial,channel==='stress'?q:p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100];
 }).filter(Boolean);
}
export function exportStudy(study,catalogue,record){
 require(study?.experiment?.id===record.id&&study.experiment.source_asset_sha256===record.source_asset_sha256,'Study experiment identity mismatch.');
 const expected=makeStudy(record,catalogue,study.configurations,study.experiment?.window?.last_row);
 for(const key of ['version','experiment','catalogue_hash','model_definitions','configurations'])require(stable(study[key])===stable(expected[key]),'Study identity mismatch: '+key);
 require(Array.isArray(study.jobs)&&study.jobs.length===expected.jobs.length,'Run count mismatch.');
 for(let i=0;i<study.jobs.length;i++){
  const job=study.jobs[i],base=expected.jobs[i];
  for(const key of ['id','model','label','change','parameters','history','specification'])require(stable(job[key])===stable(base[key]),'Run specification mismatch: '+key);
  require(['queued','running','completed','stopped','rejected','error','cancelled','timeout'].includes(job.status)&&typeof job.message==='string','Invalid run outcome.');
  if(base.status==='rejected')require(job.status==='rejected'&&job.result===null,'Rejected input cannot have a result.');
  if(job.result){require(['completed','stopped'].includes(job.status)&&job.status===(job.result.ok?'completed':'stopped'),'Result status mismatch.');createRecordedDocument(job.specification,job.result,catalogue);}
  else require(!['completed','stopped'].includes(job.status),'Missing saved result.');
 }
 return {version:'atlas-ensemble-export-0.1',study:structuredClone(study)};
}
export function importStudy(text,catalogue,record){
 const document=parseRecordedJSON(text);require(keys(document,['version','study'])&&document.version==='atlas-ensemble-export-0.1','Unsupported ensemble export.');
 exportStudy(document.study,catalogue,record);
 // Saved outcomes are inspected for identity, then all executable requests replay afresh.
 return makeStudy(record,catalogue,document.study.configurations,document.study.experiment.window.last_row);
}
