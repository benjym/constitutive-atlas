// Pure 0.2 request codec. Existing engine/UI entrypoints remain legacy-only.
import {validateRecordedRun,recordedWire} from './recorded.mjs';
export const scopedRecordedVersion='experimental-recorded-run-0.2';
const fields=['version','model','path','parameters','initial','integration_settings','control_settings','restart_settings','stress_scope'];
function mechanics(s){const {stress_scope,...rest}=s;return {...rest,version:'experimental-recorded-run-0.1'};}
export function validateScopedRecordedRun(s){
 if(!s||typeof s!=='object'||Array.isArray(s)||Object.keys(s).some(k=>!fields.includes(k))||!['version','model','path','stress_scope'].every(k=>Object.hasOwn(s,k))||s.version!==scopedRecordedVersion||!['effective','total'].includes(s.stress_scope))throw Error('Invalid scope-aware recorded request.');
 validateRecordedRun(mechanics(s));return s;
}
export function validateScopedRecordedModel(s,model){
 validateScopedRecordedRun(s);
 const first=model?.state?.[0],f=model?.formulation;
 const b=model?.schema_version==='0.1'?{source:'state',name:'sigma',measure:'cauchy',scope:'effective'}:f?.stress;
 const role=first?.semantics?.role??(first?.transient||first?.multiplier?'increment_unknown':'persistent');
 if(model?.id!==s.model||!['0.1','0.3'].includes(model?.schema_version)||(model.schema_version==='0.3'&&f?.time_dependence!=='strain_path')||b?.source!=='state'||b.name!=='sigma'||b.measure!=='cauchy'||b.scope!==s.stress_scope||Object.keys(b).sort().join(',')!=='measure,name,scope,source'||first?.name!=='sigma'||first.shape!=='sym'||first.unit!=='Pa'||role!=='persistent')throw Error('Recorded stress scope/model binding mismatch.');
 return s;
}
export function scopedRecordedWire(s,model){validateScopedRecordedModel(s,model);return recordedWire(mechanics(s));}
