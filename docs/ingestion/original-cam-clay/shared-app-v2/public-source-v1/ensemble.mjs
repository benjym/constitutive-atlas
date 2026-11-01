// One fixed experiment; request construction is independent of the DOM and engine.
import {parseRecordedJSON} from './recorded.mjs';
import {parseRecordedDocument,createRecordedDocument} from './recorded-document.mjs';
import {supportsEffectiveExperiment} from './experiments.mjs';
import {normalizeSettings,settingFields} from './numerics.mjs';
import {controlBits} from './loading.mjs';
export const experimentId='OPARA-TXCD-100';
export const modelIds=['linear-elastic','drucker-prager','modified-cam-clay'];
export const sweepParameters={'linear-elastic':['E','nu'],'drucker-prager':['M','Md'],'modified-cam-clay':['M','kappa']};
const initialVariations={'linear-elastic':{E:[24e6,36e6],nu:[.2,.3]},'drucker-prager':{M:[.96,1.44],Md:[.16,.24]},'modified-cam-clay':{M:[.96,1.44],kappa:[.032,.048]}};
export const stable=value=>JSON.stringify(value&&typeof value==='object'?Array.isArray(value)?value.map(v=>JSON.parse(stable(v))):Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(stable(value[k]))])):value);
const require=(v,m)=>{if(!v)throw Error(m);};
const finite=v=>typeof v==='number'&&Number.isFinite(v);
function keys(value,expected){return value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join(',')===[...expected].sort().join(',');}
export function validateExperiment(record){
 require(record?.version==='atlas-ensemble-experiment-0.1'&&record.id===experimentId&&record.protocol==='drained-triaxial','Unsupported ensemble experiment.');
 require(record.conventions?.stress==='compression-positive'&&record.conventions?.strain==='compression-positive'&&record.conventions?.stress_unit==='Pa'&&record.conventions?.strain_unit==='1','Experiment conventions differ.');
 require(record.source_asset_sha256?.match(/^[a-f0-9]{64}$/)&&record.provenance?.archive_sha256==='49681ae77388fb0f3f081cbebfd263cb328b9bc678ed5a376a19e6c4dba82b35'&&record.provenance?.member_sha256==='787d207c982beedf99e96b054899ba8069e4261f80fba024fdbc3549745b27cd','Experiment source identity differs.');
 require(Array.isArray(record.rows)&&record.rows.length===1438,'Expected all 1438 source observations.');
 let previous=-Infinity;
 for(const r of record.rows){require(['axial_strain','radial_effective_stress','q','volumetric_strain'].every(k=>finite(r[k]))&&r.axial_strain>=previous&&r.radial_effective_stress>0,'Invalid or reordered source observation.');previous=r.axial_strain;}
 require(stable(record.initial?.effective_stress)===stable([103720,103720,103720,0,0,0])&&record.initial?.void_ratio===.416,'Experiment initial state differs.');
 require(record.rows[0].axial_strain===0&&record.rows[0].radial_effective_stress===103720&&record.rows[0].q===0,'Source row zero contradicts initialization.');
 const rows=record.rows.filter(r=>r.axial_strain<=.01);
 require(rows.length===95&&rows.at(-1).axial_strain===.00992,'Source window differs.');return record;
}
export function defaultConfigurations(catalogue){
 return modelIds.map(id=>{const model=catalogue.models.find(m=>m.id===id);return {model:id,enabled:!!model,parameters:model?Object.fromEntries(Object.entries(model.parameters).map(([k,f])=>[k,f.default])):{},history:id==='modified-cam-clay'?{pc:200000}:{},variations:structuredClone(initialVariations[id])};});
}
function checkModel(model){
 require(model&&supportsEffectiveExperiment(model),'Model requires state-bound effective Mandel stress.');
 const expected=model.id==='linear-elastic'?['sigma','e']:model.id==='drucker-prager'?['sigma','e','gamma']:['sigma','e','pc','gamma'];
 require(model.state.map(f=>f.name).join(',')===expected.join(',')&&model.state.slice(1).every(f=>f.shape==='scalar'),'Unsupported starting-history layout.');
 if(model.schema_version==='0.3')require(model.formulation?.time_dependence==='strain_path'&&model.formulation?.strain_sign==='compression_positive','Unsupported strain-path formulation.');
}
function initialCheck(id,p,history){
 if(id==='linear-elastic'||id==='drucker-prager')require(p.E>0&&p.nu>-1&&p.nu<.5,'Elastic modulus or Poisson ratio is inadmissible.');
 if(id==='drucker-prager')require(p.M>=0&&p.Md>=0&&p.c>=0,'Drucker–Prager slopes/intercept must be nonnegative.');
 if(id==='modified-cam-clay'){
  require(p.lambda_c>p.kappa&&p.kappa>0&&p.nu>-1&&p.nu<.5,'MCC requires λ > κ > 0 and −1 < ν < 0.5.');
  require(finite(history.pc)&&history.pc>0&&p.M*p.M*103720*(103720-history.pc)/(p.p_ref*p.p_ref)<=1e-8,'MCC starting stress lies outside its assumed yield surface.');
 }
}
export function makeStudy(record,catalogue,configurations){
 validateExperiment(record);
 require(catalogue?.schema_version==='0.1'&&/^[a-f0-9]{64}$/.test(catalogue.sha256)&&Array.isArray(catalogue.models),'Exact compiled catalogue required.');
 require(Array.isArray(configurations)&&configurations.length===3&&new Set(configurations.map(c=>c.model)).size===3&&configurations.every(c=>modelIds.includes(c.model)),'Expected one configuration for each supported model.');
 const sourceRows=record.rows.slice(0,95),jobs=[],definitions=[];
 const controls=Array.from({length:6},(_,i)=>({kind:i===1||i===2?'stress':'strain',coefficients:Array.from({length:6},(_,j)=>Number(i===j))}));
 const path={version:'experimental-recorded-path-0.1',coordinate:{name:'source_row_index',unit:'1',meaning:'path_order'},initial_strain:[0,0,0,0,0,0],controls,knots:sourceRows.map((r,i)=>({coordinate:i,targets:[r.axial_strain,r.radial_effective_stress,r.radial_effective_stress,0,0,0]}))};
 for(const config of configurations){
  require(keys(config,['model','enabled','parameters','history','variations'])&&typeof config.enabled==='boolean','Invalid model configuration.');
  if(!config.enabled)continue;
  const model=catalogue.models.find(m=>m.id===config.model);checkModel(model);definitions.push(structuredClone(model));
  require(keys(config.parameters,Object.keys(model.parameters))&&keys(config.history,config.model==='modified-cam-clay'?['pc']:[])&&keys(config.variations,sweepParameters[config.model]),'Explicit named parameters, history and variations required.');
  require(Object.values(config.parameters).every(finite)&&Object.values(config.history).every(finite),'Baseline parameters and history must be finite numbers.');
  const candidates=[{label:'Baseline',change:null,parameters:config.parameters,id:config.model+':baseline'}];
  for(const name of sweepParameters[config.model]){
   const values=config.variations[name];require(Array.isArray(values)&&values.length<=6&&values.every(finite),'Use at most six finite values per varied parameter.');
   for(const value of [...new Set(values)].filter(v=>v!==config.parameters[name]))candidates.push({label:name+' = '+value,change:{parameter:name,value},parameters:{...config.parameters,[name]:value},id:config.model+':'+name+':'+controlBits(value)});
  }
  for(const candidate of candidates){
   let error=null,specification=null;
   try{
    for(const [name,field] of Object.entries(model.parameters)){const v=candidate.parameters[name];require(finite(v)&&v>=field.min&&v<=field.max,name+' is outside declared bounds.');}
    require(candidate.parameters.p_ref===model.parameters.p_ref.default,'Numerical reference scale must remain fixed.');
    initialCheck(model.id,candidate.parameters,config.history);
    const state={sigma:record.initial.effective_stress,e:record.initial.void_ratio,...config.history,gamma:0};
    specification={version:'experimental-recorded-run-0.1',model:model.id,parameters:Object.keys(model.parameters).map(k=>candidate.parameters[k]),initial:model.state.flatMap(f=>f.shape==='sym'?[...state[f.name]]:[state[f.name]]),path:structuredClone(path),integration_settings:Object.fromEntries(settingFields.map(f=>[f.key,normalizeSettings()[f.key]])),control_settings:{control_tolerance:1e-10,max_iterations:30,max_backtracks:10,max_material_trials:20000,finite_difference_step:1e-7}};
    parseRecordedDocument(JSON.stringify(specification),catalogue);
   }catch(e){error=e.message;specification=null;}
   jobs.push({id:candidate.id,model:model.id,label:candidate.label,change:candidate.change,parameters:structuredClone(candidate.parameters),history:structuredClone(config.history),specification,status:error?'rejected':'queued',message:error||'',result:null});
  }
 }
 require(jobs.length>0&&jobs.length<=39,'Select at least one available model (maximum 39 runs).');
 return structuredClone({version:'atlas-ensemble-study-0.1',experiment:{id:record.id,source_asset_sha256:record.source_asset_sha256,archive_sha256:record.provenance.archive_sha256,member_sha256:record.provenance.member_sha256,window:{first_row:0,last_row:94,max_axial_strain:.01,last_acquired_strain:.00992},control:'direct-author-membrane-corrected-radial-effective-stress',strain_origin:'first-observation',initial:record.initial,limitations:['Conditional replay: measured volumetric strain contributes to membrane-corrected radial input.','No consolidation history is inferred; MCC pc is an explicit unmeasured assumption.','Illustrative parameters; no calibration, applicability or experimental validation claim.']},catalogue_hash:catalogue.sha256,model_definitions:definitions,configurations,jobs});
}
export function resultSeries(job,channel){
 if(!job.result)return [];
 return job.result.points.map(p=>[p.strain[0]*100,channel==='stress'?(p.state[0]-p.state[1])/1000:p.strain.slice(0,3).reduce((a,b)=>a+b,0)*100]);
}
export function exportStudy(study,catalogue,record){
 const expected=makeStudy(record,catalogue,study.configurations);
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
 return makeStudy(record,catalogue,document.study.configurations);
}
