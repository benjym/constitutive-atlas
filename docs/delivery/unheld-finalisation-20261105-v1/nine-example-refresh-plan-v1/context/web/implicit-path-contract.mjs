// Generic profile transport and validation; constitutive equations execute in Wasm.
export const modelId='lade-duncan-1975-midpoint-elastic-eq19-gap-v4';
export const modelSha256='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63';
export const kind='atlas-implicit-path-laboratory-v1';
export const api='atlas_run_scope_with_settings';
export const types=Object.freeze(['string','string','string','number','number','number','number','string']);
export const settings=Object.freeze({residual_tolerance:2e-10,rate_tolerance:1e-6,max_iterations:45,max_depth:20,max_substeps:200000,max_backtracks:11,increment_tolerance:1e-7,positive_stress_metric:true});
export const equal=(a,b)=>{if(typeof a!==typeof b)return false;if(a===null||b===null||typeof a!=='object')return Object.is(a,b);if(Array.isArray(a)!==Array.isArray(b))return false;const ak=Object.keys(a).sort(),bk=Object.keys(b).sort();return ak.length===bk.length&&ak.every((k,i)=>k===bk[i]&&equal(a[k],b[k]));};
export function stringifyRun(v){if(typeof v==='number'){if(!Number.isFinite(v))throw Error('Nonfinite export number.');return Object.is(v,-0)?'-0':JSON.stringify(v);}if(v===null||typeof v!=='object')return JSON.stringify(v);if(Array.isArray(v))return '['+v.map(stringifyRun).join(',')+']';return '{'+Object.keys(v).map(k=>JSON.stringify(k)+':'+stringifyRun(v[k])).join(',')+'}';}
export const controlText=v=>typeof v==='number'?(Object.is(v,-0)?'-0':String(v)):stringifyRun(v);
const csv=v=>v.map(x=>Object.is(x,-0)?'-0':String(x)).join(',');
const fields=(o,keys)=>o&&typeof o==='object'&&!Array.isArray(o)&&equal(Object.keys(o).sort(),[...keys].sort());
const vector=(v,n)=>Array.isArray(v)&&v.length===n&&Array.from(v).every(x=>typeof x==='number'&&Number.isFinite(x));
const controlKeys=['version','units','model','parameters','initial','protocol','target','steps','cycles','settings'];
export function parseRunJSON(text) {
  if (typeof text !== 'string') throw Error('Expected JSON text.');
  const data = JSON.parse(text), stack = [];
  for (const token of text.matchAll(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}[\],:]/g)) {
    const value = token[0], frame = stack.at(-1);
    if (value === '{') stack.push({names:new Set(),key:true});
    else if (value === '[') stack.push(null);
    else if (value === '}' || value === ']') stack.pop();
    else if (value === ',') { if (frame) frame.key = true; }
    else if (value === ':') { if (frame) frame.key = false; }
    else if (value[0] === '"') {
      if (frame?.key) { const name=JSON.parse(value); if(frame.names.has(name)) throw Error('Duplicate JSON key: '+name); frame.names.add(name); }
    } else {
      const number=Number(value);
      if (!Number.isFinite(number)) throw Error('JSON number outside finite binary64 range.');
      if (!/[.eE]/.test(value) && BigInt(value)!==BigInt(number)) throw Error('Integer is not exactly representable in binary64.');
    }
  }
  return data;
}

export function validateControls(c){
 if(!fields(c,controlKeys)||c.version!==kind||c.units!=='SI'||c.model!==modelId)throw Error('Expected a complete SI Lade–Duncan strain-path request.');
 if(!vector(c.parameters,10)||!vector(c.initial,8))throw Error('Require ten finite parameters and eight finite initial-state values.');
 if(!Number.isInteger(c.protocol)||c.protocol<0||c.protocol>4||!Number.isInteger(c.steps)||c.steps<1||c.steps>5000||!Number.isInteger(c.cycles)||c.cycles<0||c.cycles>100||(c.cycles&&c.steps<16*c.cycles))throw Error('Invalid protocol or increment/cycle count.');
 if(typeof c.target!=='number'||!Number.isFinite(c.target)||Math.abs(c.target)>(c.protocol===3?1e8:.1))throw Error('Invalid control amplitude.');
 if(!equal(c.settings,settings))throw Error('This profile requires the displayed fixed qualified numerical settings.');
 return structuredClone(c);
}
export function identityCheck(i){
 if(i?.profile!=='implicit-path-v1'||i.model!==modelId||i.model_sha256!==modelSha256||!equal(i.public_models,[modelId])||!/^[0-9a-f]{64}$/.test(i.catalogue_hash))throw Error('Wrong implicit-path package/model identity.');
}
export function request(input,identity){
 const c=validateControls(input);identityCheck(identity);
 return [modelId,csv(c.parameters),csv(c.initial),c.protocol,c.target,c.steps,c.cycles,Object.keys(settings).map(k=>c.settings[k]).map(v=>typeof v==='boolean'?+v:v).join(',')];
}
export function verifyResult(r,identity,input){
 const c=validateControls(input);identityCheck(identity);
 if(r?.ok===false&&!r.model)throw Error('Engine rejected request: '+(typeof r.message==='string'?r.message:'invalid input'));
 if(!r||r.schema_version!=='0.1'||typeof r.elapsed_ms!=='number'||!Number.isFinite(r.elapsed_ms)||r.elapsed_ms<0||typeof r.ok!=='boolean'||typeof r.message!=='string'||r.model!==modelId||r.catalogue_hash!==identity.catalogue_hash||r.api_version!=='experimental-laboratory-scope-0.1')throw Error('Engine model, catalogue or response contract differs.');
 for(const key of ['parameters','initial','protocol','target','steps','cycles'])if(!equal(r[key],c[key]))throw Error('Returned '+key+' differs from explicit request.');
 const expected={version:'incremental-settings-0.1',norm:'scaled_component_max',...settings,path_control_version:'implicit-step-doubling-0.1',max_reserved_path_trials:3*settings.max_substeps};
 if(!equal(r.integration_settings,expected))throw Error('Engine numerical settings differ.');
 if(!equal(r.stress,{source:'state',name:'sigma',measure:'cauchy',scope:'total',tensor_representation:'mandel',sign:'compression_positive'})||!equal(r.pore_pressure,{quantity:'change',availability:'unavailable',reason:'total_stress_without_pore_pressure_law'}))throw Error('Unexpected stress or pore-pressure scope.');
 if(!Array.isArray(r.points)||r.points.length>c.steps+1||(r.ok&&r.points.length!==c.steps+1))throw Error('Incomplete or oversized response.');
 if(!r.points.length){if(r.ok)throw Error('Successful run lacks initial state.');return r;}
 for(const [index,p] of r.points.entries()){
  if(!fields(p,['control','strain','state','p','q','q_signed','u','iterations','substeps','rejected','error'])||!vector(p.state,8)||!vector(p.strain,6)||p.u!==null)throw Error('Invalid complete state/strain point.');
  for(const key of ['control','p','q','q_signed','error'])if(typeof p[key]!=='number'||!Number.isFinite(p[key]))throw Error('Nonfinite response point.');
  for(const key of ['iterations','substeps','rejected'])if(!Number.isSafeInteger(p[key])||p[key]<0)throw Error('Invalid solver diagnostic.');
  const control=index===0?0:c.cycles?c.target*Math.sin(2*Math.PI*c.cycles*index/c.steps):c.target*index/c.steps;
  if(Math.abs(p.control-control)>1e-12*Math.max(1,Math.abs(control)))throw Error('Returned loading history differs.');
  if(index===0&&(!equal(p.state,c.initial)||!equal(p.strain,[0,0,0,0,0,0])))throw Error('Initial state was changed.');
 }
 return r;
}
const withoutElapsed=r=>{const c=structuredClone(r);delete c.elapsed_ms;return c;};
export function verifyReplay(actual,expected){if(!equal(withoutElapsed(actual),withoutElapsed(expected)))throw Error('Replay differs from saved complete response.');}
export function exportRun(controls,result,identity){const c=validateControls(controls);verifyResult(result,identity,c);if(!result.ok)throw Error('A failed run cannot be exported as complete.');return {kind,provenance:structuredClone(identity),controls:c,request:{function:api,args:request(c,identity)},result:structuredClone(result)};}
export function importRun(text,identity){const d=parseRunJSON(text);identityCheck(identity);if(!fields(d,['kind','provenance','controls','request','result'])||d.kind!==kind||!equal(d.provenance,identity))throw Error('Expected a run from this exact package.');const c=validateControls(d.controls);if(!fields(d.request,['function','args'])||d.request.function!==api||!equal(d.request.args,request(c,identity)))throw Error('Imported request differs from explicit controls.');verifyResult(d.result,identity,c);if(!d.result.ok)throw Error('Import requires a complete successful run.');return {controls:c,result:structuredClone(d.result)};}
export function preset(name='dense'){
 if(!['dense','loose'].includes(name))throw Error('Unknown source preset.');
 const dense=name==='dense';return validateControls({version:kind,units:'SI',model:modelId,parameters:dense?[101325,103,40,.44,.957,.000255,1.32,2300,.8,0]:[101325,58,33,.39,.970,.000680,1.17,1600,.86,0],initial:[60000,60000,60000,0,0,0,dense?13:6,0],protocol:1,target:.005,steps:400,cycles:0,settings:{...settings}});
}
