// Caller loading only. Every arithmetic statement rounds to ECMAScript binary64.
export const loadingVersion='laboratory-controls-0.1';
export const waveformVersion='laboratory-waveform-0.1';
export const encoding='ieee754-binary64-hex';
const finite=x=>typeof x==='number'&&Number.isFinite(x);
function closed(value,keys){return value!==null&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).length===keys.length&&keys.every(k=>Object.hasOwn(value,k));}
export function controlBits(value){
  if(!finite(value))throw Error('Loading controls must be finite numbers.');
  const view=new DataView(new ArrayBuffer(8));view.setFloat64(0,value,false);
  return view.getUint32(0,false).toString(16).padStart(8,'0')+view.getUint32(4,false).toString(16).padStart(8,'0');
}
export function controlFromBits(value){
  if(typeof value!=='string'||!/^[0-9a-f]{16}$/.test(value))throw Error('Invalid exact loading bits.');
  const view=new DataView(new ArrayBuffer(8));view.setUint32(0,parseInt(value.slice(0,8),16),false);view.setUint32(4,parseInt(value.slice(8),16),false);
  const number=view.getFloat64(0,false);if(!finite(number))throw Error('Nonfinite exact loading bits.');return number;
}
export function cyclicWave(steps,cycles,index){
  if(!Number.isInteger(steps)||steps<1||steps>5000||!Number.isInteger(cycles)||cycles<0||cycles>100||!Number.isInteger(index)||index<0||index>steps)throw Error('Invalid waveform integer inputs.');
  const phase=(cycles*index)%steps,quadrant=Math.floor(4*phase/steps),rem=4*phase-quadrant*steps;
  const j=quadrant%2===0?rem:steps-rem;
  if(j===0)return 0;
  if(j===steps)return quadrant===1?1:-1;
  const ratio=j/steps,x=1.5707963267948966*ratio,z=x*x;
  let term=x,sum=x;
  for(let n=1;n<=11;n++){const product=-term*z;term=product/((2*n)*(2*n+1));sum=sum+term;}
  return quadrant>=2?-sum:sum;
}
function geometry(s){
  if(!Number.isInteger(s.protocol)||s.protocol<0||s.protocol>4||!finite(s.target)||Math.abs(s.target)>(s.protocol===3?1e8:.1)||!Number.isInteger(s.steps)||s.steps<1||s.steps>5000||!Number.isInteger(s.cycles)||s.cycles<0||s.cycles>100||s.cycles&&s.steps<16*s.cycles)throw Error('Invalid loading amplitude or sampling.');
}
export function createLoading(s){
  geometry(s);
  const controls=[];
  for(let i=0;i<=s.steps;i++){
    let value;
    if(i===0||s.target===0)value=0;
    else if(s.cycles===0)value=i===s.steps?s.target:(s.target*i)/s.steps;
    else {const wave=cyclicWave(s.steps,s.cycles,i);value=wave===0?0:s.target*wave;}
    controls.push(controlBits(value));
  }
  return {version:loadingVersion,encoding,producer:{version:waveformVersion,algorithm:s.cycles===0?'linear-rne-v1':'cyclic-sine-rne12-v1',target_bits:controlBits(s.target),steps:s.steps,cycles:s.cycles},controls_bits:controls};
}
export function normalizeLoading(s){
  if(s.loading===undefined)return undefined; // Absent metadata retains legacy backend waveform semantics.
  geometry(s);const l=s.loading,p=l?.producer;
  if(!closed(l,['version','encoding','producer','controls_bits'])||l.version!==loadingVersion||l.encoding!==encoding||!closed(p,['version','algorithm','target_bits','steps','cycles'])||p.version!==waveformVersion)throw Error('Unsupported loading provenance.');
  const target=controlFromBits(p.target_bits);
  // JSON numeric zero loses its sign; producer target_bits remains authoritative.
  if(target!==s.target||p.steps!==s.steps||p.cycles!==s.cycles)throw Error('Loading producer disagrees with the run specification.');
  const expected=createLoading({...s,target});
  if(p.algorithm!==expected.producer.algorithm||!Array.isArray(l.controls_bits)||l.controls_bits.length!==expected.controls_bits.length||l.controls_bits.some((b,i)=>b!==expected.controls_bits[i]))throw Error('Loading control bits disagree with the declared producer.');
  return expected;
}
export function verifyReturnedLoading(result,s,catalogueHash){
  const l=normalizeLoading(s);
  if(!l){if(result.loading!==undefined||result.api_version!==undefined)throw Error('Legacy loading returned a different API contract.');return;}
  if(typeof catalogueHash!=='string'||!catalogueHash||result.catalogue_hash!==catalogueHash||result.schema_version!=='0.1')throw Error('The engine returned a different catalogue or result version.');
  const r=result.loading;
  if(result.model!==s.model||!Array.isArray(result.parameters)||!Array.isArray(result.initial)||result.parameters.length!==s.parameters.length||result.initial.length!==s.initial.length||result.parameters.some((v,i)=>v!==s.parameters[i])||result.initial.some((v,i)=>v!==s.initial[i]))throw Error('The engine returned a different model, parameters or initial state.');
  if(result.api_version!=='experimental-laboratory-controls-0.1'||!closed(r,['version','encoding','controls','controls_bits'])||r.version!==l.version||r.encoding!==l.encoding||!Array.isArray(r.controls_bits)||r.controls_bits.length!==l.controls_bits.length||r.controls_bits.some((b,i)=>b!==l.controls_bits[i])||!Array.isArray(r.controls)||r.controls.length!==l.controls_bits.length)throw Error('The engine did not preserve the requested exact loading. Reload a matching build.');
  // Raw engine JSON is checked before worker cloning/export; its numeric -0 survives JSON.parse.
  if(r.controls.some((v,i)=>controlBits(v)!==l.controls_bits[i]))throw Error('The engine numeric loading differs from its exact bits.');
  if(typeof result.ok!=='boolean'||result.protocol!==s.protocol||result.steps!==s.steps||Object.hasOwn(result,'target')||Object.hasOwn(result,'cycles')||!Array.isArray(result.points)||result.points.length>l.controls_bits.length||result.ok&&result.points.length!==l.controls_bits.length)throw Error('Invalid exact-loading response or committed prefix.');
  if(result.points.some((p,i)=>!p||controlBits(p.control)!==l.controls_bits[i]))throw Error('Committed point controls differ from the requested prefix.');
}
export function exportRun(catalogueHash,s,result){
  const loading=normalizeLoading(s);verifyReturnedLoading(result,s,catalogueHash);
  if(result.catalogue_hash!==catalogueHash||result.model!==s.model)throw Error('Run result identity does not match the export.');
  return {schema_version:loading?'0.2':'0.1',catalogue_hash:catalogueHash,specification:structuredClone(s),result:structuredClone(result)};
}
export function importRunDocument(doc,catalogueHash){
  if(!closed(doc,['schema_version','catalogue_hash','specification','result'])||!['0.1','0.2'].includes(doc.schema_version))throw Error('Unsupported run schema version.');
  if(doc.catalogue_hash!==catalogueHash)throw Error('Run was created with a different model catalogue. Use the matching release.');
  const s=doc.specification;
  if(!s||typeof s!=='object'||Array.isArray(s))throw Error('Invalid run specification.');
  if(doc.schema_version==='0.1'){
    if(Object.hasOwn(s,'loading')||doc.result?.loading!==undefined||doc.result?.api_version!==undefined)throw Error('Legacy run cannot contain a newer loading contract.');
    return structuredClone(s);
  }
  if(!s.loading)throw Error('Exact loading provenance is required for this run version.');
  normalizeLoading(s);
  // Saved results are untrusted and recomputed on import. JSON.stringify erases numeric -0;
  // retain exact control bits as authority rather than validating exported numeric signs here.
  if(!doc.result||doc.result.schema_version!=='0.1'||doc.result.api_version!=='experimental-laboratory-controls-0.1'||doc.result.catalogue_hash!==catalogueHash||doc.result.model!==s.model)throw Error('Saved run result identity does not match its specification.');
  return structuredClone(s);
}
