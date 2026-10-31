// Browser contract mirrors incremental-settings-0.1; values are dimensionless
// in the model's state scales. This module does not solve constitutive equations.
export const settingsVersion='incremental-settings-0.1';
export const settingsNorm='scaled_component_max';
export const settingFields=Object.freeze([
  {key:'residual_tolerance',label:'Residual tolerance',value:2e-10,integer:false,min:0},
  {key:'rate_tolerance',label:'Rate integration tolerance',value:1e-6,integer:false,min:0},
  {key:'max_iterations',label:'Newton iterations per candidate',value:45,integer:true,min:1,max:1000},
  {key:'max_depth',label:'Maximum subdivision depth',value:14,integer:true,min:0,max:20},
  {key:'max_substeps',label:'Accepted substeps per increment',value:20000,integer:true,min:1,max:1000000},
  {key:'max_backtracks',label:'Newton line search halvings',value:11,integer:true,min:0,max:30},
].map(Object.freeze));
export function normalizeSettings(value){
  if(value===undefined)return Object.fromEntries([['version',settingsVersion],['norm',settingsNorm],...settingFields.map(f=>[f.key,f.value])]);
  if(!value||typeof value!=='object'||Array.isArray(value)||value.version!==settingsVersion||value.norm!==settingsNorm)
    throw Error('Unsupported numerical settings version or error norm.');
  const allowed=['version','norm',...settingFields.map(f=>f.key)];
  if(Object.keys(value).some(k=>!allowed.includes(k)))throw Error('Unknown numerical setting.');
  for(const f of settingFields){
    const v=value[f.key];
    if(typeof v!=='number'||!Number.isFinite(v)||(f.integer?(!Number.isInteger(v)||v<f.min||v>f.max):v<=0))
      throw Error('Invalid numerical setting: '+f.label+'.');
  }
  return Object.fromEntries(allowed.map(k=>[k,value[k]]));
}
export function settingsCsv(value){const s=normalizeSettings(value);return settingFields.map(f=>s[f.key]).join(',');}
export function verifyReturnedSettings(result,requested){
  if(!result.integration_settings)throw Error(result.ok===false&&result.message?result.message:'The engine does not report numerical settings. Reload a matching build.');
  const actual=normalizeSettings(result.integration_settings),expected=normalizeSettings(requested);
  if(Object.keys(expected).some(k=>actual[k]!==expected[k]))throw Error('The engine used different numerical settings. Reload a matching build.');
}
export function runLaboratory(engine,s){
  const settings=normalizeSettings(s.integration_settings);
  const result=JSON.parse(engine.ccall('atlas_run_with_settings','string',
    ['string','string','string','number','number','number','number','string'],
    [s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.target,s.steps,s.cycles,settingsCsv(settings)]));
  verifyReturnedSettings(result,settings);return result;
}
