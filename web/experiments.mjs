// Plot import contract. Full archival normalization remains in atlas/data.py.
export function validateExperiment(data){
  if(data?.schema_version!=='0.1'||!['experiment','measurement-series','test-summary'].includes(data.kind)||typeof data.id!=='string'||!data.id.trim()||!Array.isArray(data.rows)||!data.rows.length||data.rows.length>(data.kind==='experiment'?100000:200000))throw Error('Expected an Atlas measurement record with an ID and a supported observation count.');
  if(data.kind!=='experiment'){
    const c=data.conventions,columns=data.columns;
    if(c?.stress!=='source-defined'||c?.strain!=='source-defined'||c?.stress_unit!=='per-channel'||c?.strain_unit!=='per-channel'||!Array.isArray(columns)||columns.length<2||columns.length>100)throw Error('Source measurements must declare native channel conventions.');
    const keys=new Set(columns.map(c=>c.key));
    if(keys.size!==columns.length||columns.some(c=>typeof c.key!=='string'||!/^c\d+$/.test(c.key)||typeof c.name!=='string'||typeof c.unit!=='string')||!keys.has(data.source_plot?.x)||!keys.has(data.source_plot?.y))throw Error('Invalid source measurement columns.');
    for(const row of data.rows)if(!row||!Object.keys(row).length||Object.entries(row).some(([k,v])=>!keys.has(k)||!Number.isFinite(v)))throw Error('Invalid source measurement observation.');
    return data;
  }
  const c=data.conventions;
  if(c?.stress!=='compression-positive'||c?.strain!=='compression-positive'||c?.stress_unit!=='Pa'||c?.strain_unit!=='1')throw Error('Experiment must declare compression-positive Pa / dimensionless strain conventions.');
  for(const row of data.rows){
    if(!row||!Number.isFinite(row.axial_strain)||!Number.isFinite(row.q))throw Error('Every row needs finite axial_strain and q.');
    for(const k of ['p','volumetric_strain','pore_pressure'])if(row[k]!==undefined&&!Number.isFinite(row[k]))throw Error('Nonfinite experiment channel.');
  }
  return data;
}
export function normalizeWichtmann(text,name){
  const match=/^(TMD|TMU)(\d+)\.dat$/i.exec(name);
  if(!match)throw Error('Original-file import currently supports TMD<number>.dat and TMU<number>.dat only.');
  const series=match[1].toUpperCase(),lines=text.replace(/^\uFEFF/,'').trim().split(/\r?\n/);
  const expected=series==='TMD'?['eps1','epsv','eps3','epsq']:['eps1','u','sigma3',"sigma3'"];
  if(lines.length<3||!expected.every((v,i)=>lines[0].trim().split(/\s+/)[i]===v))throw Error('Unrecognized Wichtmann column layout.');
  const units=lines[1].trim().split(/\s+/);
  const expectedUnits=series==='TMD'?['[%]','[%]','[%]','[%]','[%]','[kPa]','[kPa]','[-]']:['[%]','[kPa]','[kPa]','[kPa]','[kPa]','[kPa]','[kPa]','[kPa]'];
  if(!expectedUnits.every((v,i)=>units[i]===v)||units.length!==8)throw Error('Unrecognized Wichtmann units.');
  const raw=lines.slice(2).filter(l=>l.trim()).map((l,i)=>{
    const tokens=l.trim().split(/\s+/),r=tokens.map(Number);
    if(tokens.length!==8||!r.every(Number.isFinite))throw Error('Expected eight finite values at data row '+(i+1));return r;
  });
  if(!raw.length||raw.length>100000)throw Error('Expected 1–100,000 measured rows.');
  const rows=raw.map(r=>series==='TMD'?{axial_strain:r[0]/100,volumetric_strain:r[1]/100,radial_strain:r[2]/100,void_ratio:r[4],q:r[5]*1000,p:r[6]*1000}:{axial_strain:r[0]/100,pore_pressure:(r[1]-raw[0][1])*1000,pore_pressure_absolute:r[1]*1000,radial_effective_stress:r[3]*1000,axial_effective_stress:r[5]*1000,p:r[6]*1000,q:r[7]*1000});
  const first=rows[0],initial={effective_stress:[first.p+2*first.q/3,first.p-first.q/3,first.p-first.q/3,0,0,0]};
  if(series==='TMD')initial.void_ratio=first.void_ratio;
  return validateExperiment({schema_version:'0.1',kind:'experiment',id:'KFS-'+series+match[2],material:'Karlsruhe fine sand',protocol:series==='TMD'?'drained-triaxial':'undrained-triaxial',conventions:{stress:'compression-positive',strain:'compression-positive',stress_unit:'Pa',strain_unit:'1'},initial,provenance:{source_url:'https://www.torsten-wichtmann.de/KFSDB-'+series+'.htm',member:name,original_headers:lines.slice(0,2)},warnings:series==='TMD'?['Void ratio is dimensionless despite the source [%] label.']:['Initial void ratio unavailable in this file. Volumetric strain is not a measured channel.'],rows});
}
export function measuredSeries(experiment,visible,x,y){
  if(!visible||!experiment)return [];
  return experiment.rows.filter(r=>Number.isFinite(r[x])&&Number.isFinite(r[y])).map(r=>[r[x],r[y]]);
}

// The hosted format removes repeated channel names without rounding or sampling.
export function decodeExperiment(data){
  if(!['atlas-experiment-columns-v1','atlas-source-columns-v1'].includes(data?.format)||!data.metadata||!Array.isArray(data.columns)||!Array.isArray(data.values)||data.values.length>200000)throw Error('Unsupported built-in experiment format.');
  const native=data.format==='atlas-source-columns-v1';
  if(native&&data.metadata.kind==='experiment'||!native&&data.metadata.kind!=='experiment')throw Error('Measurement format and record kind differ.');
  const allowed=native?(data.metadata.columns||[]).map(c=>c.key):['axial_strain','q','p','volumetric_strain','pore_pressure'];
  if((!native&&(!data.columns.includes('axial_strain')||!data.columns.includes('q')))||new Set(data.columns).size!==data.columns.length||data.columns.some(c=>!allowed.includes(c))||native&&data.columns.length!==allowed.length)throw Error('Invalid experiment channels.');
  const rows=data.values.map(values=>{
    if(!Array.isArray(values)||values.length!==data.columns.length||!values.every(x=>x===null||Number.isFinite(x)))throw Error('Invalid experiment observation.');
    return Object.fromEntries(data.columns.map((c,i)=>[c,values[i]]).filter(([,v])=>v!==null));
  });
  return validateExperiment({...data.metadata,rows});
}

export async function fetchExperiment(entry,fetcher=fetch){
  // Full-resolution, 24-channel torsion histories exceed 10 MiB. Keep a
  // bounded payload while retaining every measured channel and observation.
  const maxBytes=32*1024*1024;
  if(!/^[A-Za-z0-9][A-Za-z0-9_-]{0,119}$/.test(entry.id)||entry.path!==entry.id+'.json'||!/^[a-f0-9]{64}$/.test(entry.sha256)||!Number.isSafeInteger(entry.size_bytes)||entry.size_bytes<=0||entry.size_bytes>maxBytes)throw Error('Invalid experiment catalogue entry.');
  const response=await fetcher('./experiments/'+entry.path);
  if(!response.ok)throw Error('Measurements could not be loaded. Please try selecting the test again.');
  const bytes=await response.arrayBuffer();
  if(bytes.byteLength>maxBytes||bytes.byteLength!==entry.size_bytes)throw Error('Experiment file size does not match the catalogue.');
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  if(digest!==entry.sha256)throw Error('Experiment checksum differs from the catalogue. Reload the page.');
  const data=decodeExperiment(JSON.parse(new TextDecoder().decode(bytes)));
  if(data.id!==entry.id||data.rows.length!==entry.rows)throw Error('Experiment does not match the selected test.');
  return data;
}

// Axes describe physical quantities, not merely matching unit dimensions.
export const comparisonAxes={
  stress:{x:'axial_strain',y:'q',xLabel:'Axial strain ε₁ (%)',yLabel:'Deviator stress q (kPa)',xScale:100,yScale:.001},
  path:{x:'p',y:'q',xLabel:'Mean effective stress p′ (kPa)',yLabel:'Deviator stress q (kPa)',xScale:.001,yScale:.001},
  volume:{x:'axial_strain',y:'volumetric_strain',xLabel:'Axial strain ε₁ (%)',yLabel:'Volumetric strain εᵥ (%)',xScale:100,yScale:100},
  pore:{x:'axial_strain',y:'pore_pressure',xLabel:'Axial strain ε₁ (%)',yLabel:'Pore-pressure change Δu (kPa)',xScale:100,yScale:.001}
};
const comparisonCache=new WeakMap();
export function comparisonMetadata(record){
  if(record?.kind!=='experiment')return {plots:[],loading:'unreviewed'};
  if(comparisonCache.has(record))return comparisonCache.get(record);
  const plots=Object.entries(comparisonAxes).filter(([,a])=>record.rows.some(r=>Number.isFinite(r[a.x])&&Number.isFinite(r[a.y]))).map(([key])=>key);
  let lo=Infinity,hi=-Infinity;for(const row of record.rows){lo=Math.min(lo,row.axial_strain);hi=Math.max(hi,row.axial_strain);}
  const tolerance=Math.max(1e-8,(hi-lo)*.05);let rising=false,falling=false,low=record.rows[0].axial_strain,high=low;
  for(const row of record.rows){const value=row.axial_strain;rising||=value-low>tolerance;falling||=high-value>tolerance;low=Math.min(low,value);high=Math.max(high,value);}
  const result={plots,loading:rising&&falling?'reversing':'monotonic'};comparisonCache.set(record,result);return result;
}
export function compatibleExperiment(record,protocol,cycles=0){
  const expected={1:'drained-triaxial',2:'undrained-triaxial',3:'undrained-triaxial'}[protocol];
  const meta=record?.rows instanceof Array?comparisonMetadata(record):record?.comparison;
  return !!expected&&record?.kind==='experiment'&&record.protocol===expected&&!!meta?.plots?.length&&meta.loading===(Number(cycles)>0?'reversing':'monotonic');
}
export function comparisonSeries(record,visible,plot,protocol,cycles=0){
  const axes=comparisonAxes[plot];
  if(!axes||!compatibleExperiment(record,protocol,cycles)||plot==='pore'&&![2,3].includes(Number(protocol)))return [];
  return measuredSeries(record,visible,axes.x,axes.y).map(([x,y])=>[x*axes.xScale,y*axes.yScale]);
}
