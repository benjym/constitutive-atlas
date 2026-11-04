// Transport only: Maxwell constitutive equations execute in the common Wasm engine.
export const modelId = 'maxwell-itasca900-zero-spin-ode';
export const modelSha256 = 'dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f';
export const kind = 'atlas-maxwell-laboratory-v1';
export const solver = Object.freeze({method:'backward-euler-step-doubling',relative_tolerance:1e-8,absolute_scale_fraction:1e-11,minimum_step:1e-12,maximum_step:1e6,maximum_substeps:100000,nonlinear_tolerance:1e-10,maximum_iterations:40,maximum_depth:40});
export const types = Object.freeze([...Array(7).fill('string'), ...Array(8).fill('number')]);
const canonical = v => Array.isArray(v) ? v.map(canonical) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map(k => [k, canonical(v[k])])) : v;
const equal = (a,b) => JSON.stringify(canonical(a)) === JSON.stringify(canonical(b));
const fields = (o,keys) => o && typeof o === 'object' && !Array.isArray(o) && equal(Object.keys(o).sort(), [...keys].sort());
const vector = (a,n=6) => Array.isArray(a) && a.length === n && Array.from(a).every(v => typeof v === 'number' && Number.isFinite(v));
const controlKeys = ['schema_version','units','model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments','solver'];
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
export function validateControls(c) {
  if (!fields(c,controlKeys) || c.schema_version!=='0.2' || c.units!=='SI' || c.model!==modelId) throw Error('Expected a complete SI Maxwell schedule.');
  for (const key of ['initial','initial_strain','initial_strain_rate']) if (!vector(c[key])) throw Error(key+' requires six finite Mandel components.');
  if (!vector(c.parameters,3) || c.parameters.some(x=>x<1e-12 || x>1e30)) throw Error('K, G and eta require positive machine bounds 1e-12–1e30; these are not qualified material ranges.');
  if (!equal(c.solver,solver)) throw Error('Use the fixed qualified schedule solver settings.');
  if (!Number.isFinite(c.start_time) || c.start_time<0 || !Array.isArray(c.segments) || c.segments.length<1 || c.segments.length>100) throw Error('Invalid physical start time or segment count.');
  let time=c.start_time, samples=0; const ids=new Set();
  for (const s of c.segments) {
    if (!fields(s,['id','duration','samples','controls']) || typeof s.id!=='string' || !/^[A-Za-z0-9_-]{1,64}$/.test(s.id) || ids.has(s.id)) throw Error('Segments require unique safe IDs and complete explicit fields.');
    ids.add(s.id);
    if (!Number.isFinite(s.duration) || s.duration<=0 || !Number.isInteger(s.samples) || s.samples<1 || s.samples>200 || (samples+=s.samples)>1000) throw Error('Invalid segment duration or sample budget.');
    const end=time+s.duration;
    if (!Number.isFinite(end) || end<=time) throw Error('Unrepresentable segment endpoint.');
    let previous=time;
    for (let j=1;j<=s.samples;j++) { const next=j===s.samples?end:time+s.duration*(j/s.samples); if(next<=previous)throw Error('Unrepresentable sample spacing.'); previous=next; }
    time=end;
    if (!Array.isArray(s.controls) || s.controls.length!==6) throw Error('Each segment requires six component controls.');
    for (const v of s.controls) {
      if (!v || !['strain','stress'].includes(v.quantity) || !['hold','rate'].includes(v.kind) || !fields(v,v.kind==='hold'?['quantity','kind']:['quantity','kind','value']) || (v.kind==='rate' && !Number.isFinite(v.value))) throw Error('Controls require explicit strain/stress hold or finite rate.');
    }
  }
  return structuredClone(c);
}
function identityCheck(identity) {
  if (identity?.model!==modelId || identity.model_sha256!==modelSha256 || !/^[0-9a-f]{64}$/.test(identity.catalogue_hash)) throw Error('Wrong Maxwell model/package identity.');
}
export function request(controls,identity) {
  const c=validateControls(controls); identityCheck(identity);
  const wire=c.segments.flatMap(s=>[s.duration,s.samples,...s.controls.flatMap(v=>[+(v.quantity==='stress'),+(v.kind==='rate'),v.kind==='rate'?v.value:0])]);
  return [modelId,c.parameters.join(','),c.initial.join(','),c.initial_strain.join(','),c.initial_strain_rate.join(','),wire.join(','),c.segments.map(s=>s.id).join(','),c.start_time,solver.relative_tolerance,solver.absolute_scale_fraction,solver.minimum_step,solver.maximum_step,solver.maximum_substeps,solver.nonlinear_tolerance,solver.maximum_iterations];
}
export function verifyResult(r,identity,controls) {
  const c=validateControls(controls); identityCheck(identity);
  if (!fields(r,[...controlKeys,'ok','catalogue_hash','message','points']) || r.ok!==true || r.model!==modelId || r.catalogue_hash!==identity.catalogue_hash) throw Error(r?.message || 'Engine/model catalogue mismatch or unsuccessful schedule.');
  for (const key of controlKeys) if (!equal(r[key],c[key])) throw Error('Returned '+key+' differs from the explicit request.');
  if (typeof r.message!=='string') throw Error('Missing engine diagnostic message.');
  const expected=[{time:c.start_time,segment:-1,side:'left'}]; let time=c.start_time;
  for (const [i,s] of c.segments.entries()) {
    expected.push({time,segment:i,side:'right'});const end=time+s.duration;
    for(let j=1;j<=s.samples;j++)expected.push({time:j===s.samples?end:time+s.duration*(j/s.samples),segment:i,side:'left'});
    time=end;
  }
  if (!Array.isArray(r.points) || r.points.length!==expected.length) throw Error('Incomplete Maxwell history.');
  for (const [i,p] of r.points.entries()) {
    const e=expected[i];
    if (!fields(p,['time','segment','side','state','strain','strain_rate','observables','iterations','substeps','rejected','temporal_error_norm','nonlinear_residual_norm'])) throw Error('Unexpected or missing history point fields.');
    if (p.time!==e.time || p.segment!==e.segment || p.side!==e.side) throw Error('Invalid sample/event sequence.');
    for (const key of ['state','strain','observables']) if(!vector(p[key]))throw Error('Invalid returned '+key+'.');
    if (!equal(p.state,p.observables)) throw Error('Stress state/observable mismatch.');
    if (!Array.isArray(p.strain_rate) || p.strain_rate.length!==6) throw Error('Incomplete strain rate.');
    Array.from(p.strain_rate).forEach((v,j)=>{
      const unresolved=e.side==='right' && c.segments[e.segment].controls[j].quantity==='stress';
      if(unresolved ? v!==null : typeof v!=='number'||!Number.isFinite(v))throw Error('Invalid component transition strain rate.');
    });
    for(const key of ['iterations','substeps','rejected'])if(!Number.isSafeInteger(p[key])||p[key]<0)throw Error('Invalid iteration diagnostic.');
    for(const key of ['temporal_error_norm','nonlinear_residual_norm'])if(typeof p[key]!=='number'||!Number.isFinite(p[key])||p[key]<0)throw Error('Invalid residual diagnostic.');
    if(i===0 && (!equal(p.state,c.initial)||!equal(p.strain,c.initial_strain)||!equal(p.strain_rate,c.initial_strain_rate)))throw Error('Initial complete state mismatch.');
    if(e.side==='right' && (!equal(p.state,r.points[i-1].state)||!equal(p.strain,r.points[i-1].strain)))throw Error('State changed across a control transition.');
  }
  return r;
}
export function verifyReplay(actual,expected) {
  if(!equal(actual,expected))throw Error('Replayed complete result differs from saved output.');return actual;
}
export function exportRun(controls,result,identity) {
  const c=validateControls(controls);verifyResult(result,identity,c);
  return {kind,provenance:structuredClone(identity),controls:c,request:{function:'atlas_run_schedule',args:request(c,identity)},result:structuredClone(result)};
}
export function importRun(text,identity) {
  const data=parseRunJSON(text);identityCheck(identity);
  if(!fields(data,['kind','provenance','controls','request','result']) || data.kind!==kind || !equal(data.provenance,identity))throw Error('Expected a saved run from this exact Maxwell package.');
  const c=validateControls(data.controls);
  if(!fields(data.request,['function','args']) || data.request.function!=='atlas_run_schedule' || !equal(data.request.args,request(c,identity)))throw Error('Imported ABI request differs from explicit controls/settings.');
  verifyResult(data.result,identity,c);
  return {controls:c,result:structuredClone(data.result)};
}

// The existing source-qualified examples, normalized with explicit solver defaults.
const presetData = {"relaxation":{"schema_version":"0.2","units":"SI","model":"maxwell-itasca900-zero-spin-ode","parameters":[20000000.0,12000000.0,24000000.0],"initial":[140000,80000,80000,3000,-2000,1000],"initial_strain":[0,0,0,0,0,0],"initial_strain_rate":[0,0,0,0,0,0],"start_time":0,"segments":[{"id":"relax","duration":8,"samples":8,"controls":[{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"}]}],"solver":{"method":"backward-euler-step-doubling","relative_tolerance":1e-08,"absolute_scale_fraction":1e-11,"maximum_substeps":100000}},"creep":{"schema_version":"0.2","units":"SI","model":"maxwell-itasca900-zero-spin-ode","parameters":[20000000.0,12000000.0,24000000.0],"initial":[140000,80000,80000,3000,-2000,1000],"initial_strain":[0,0,0,0,0,0],"initial_strain_rate":[0,0,0,0,0,0],"start_time":0,"segments":[{"id":"creep","duration":4,"samples":8,"controls":[{"quantity":"stress","kind":"hold"},{"quantity":"stress","kind":"hold"},{"quantity":"stress","kind":"hold"},{"quantity":"stress","kind":"hold"},{"quantity":"stress","kind":"hold"},{"quantity":"stress","kind":"hold"}]}],"solver":{"method":"backward-euler-step-doubling","relative_tolerance":1e-08,"absolute_scale_fraction":1e-11,"maximum_substeps":100000}},"oedometer":{"schema_version":"0.2","units":"SI","model":"maxwell-itasca900-zero-spin-ode","parameters":[20000000.0,12000000.0,24000000.0],"initial":[33333.333333333336,33333.333333333336,100000.0,0,0,0],"initial_strain":[0,0,0.002777777777777778,0,0,0],"initial_strain_rate":[0,0,0,0,0,0],"start_time":0,"segments":[{"id":"creep","duration":8,"samples":8,"controls":[{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"stress","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"}]}],"solver":{"method":"backward-euler-step-doubling","relative_tolerance":1e-08,"absolute_scale_fraction":1e-11,"maximum_substeps":100000}},"load-hold-reverse":{"schema_version":"0.2","units":"SI","model":"maxwell-itasca900-zero-spin-ode","parameters":[20000000.0,12000000.0,24000000.0],"initial":[140000,80000,80000,3000,-2000,1000],"initial_strain":[0,0,0,0,0,0],"initial_strain_rate":[0,0,0,0,0,0],"start_time":0,"segments":[{"id":"load","duration":1,"samples":4,"controls":[{"quantity":"strain","kind":"rate","value":0.001},{"quantity":"strain","kind":"rate","value":-0.0005},{"quantity":"strain","kind":"rate","value":-0.0005},{"quantity":"strain","kind":"rate","value":0.0004},{"quantity":"strain","kind":"rate","value":-0.0003},{"quantity":"strain","kind":"rate","value":0.0002}]},{"id":"hold","duration":1,"samples":4,"controls":[{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"},{"quantity":"strain","kind":"hold"}]},{"id":"reverse","duration":1,"samples":4,"controls":[{"quantity":"strain","kind":"rate","value":-0.001},{"quantity":"strain","kind":"rate","value":0.0005},{"quantity":"strain","kind":"rate","value":0.0005},{"quantity":"strain","kind":"rate","value":-0.0004},{"quantity":"strain","kind":"rate","value":0.0003},{"quantity":"strain","kind":"rate","value":-0.0002}]}],"solver":{"method":"backward-euler-step-doubling","relative_tolerance":1e-08,"absolute_scale_fraction":1e-11,"maximum_substeps":100000}}};
export const presetNames=Object.freeze(Object.keys(presetData));
export function preset(name) {
  if(!Object.hasOwn(presetData,name))throw Error("Unknown Maxwell preset.");
  return validateControls({...structuredClone(presetData[name]),solver:{...solver}});
}
