// Plot import contract. Full archival normalization remains in atlas/data.py.
export function validateExperiment(data){
  if(data?.schema_version!=='0.1'||data.kind!=='experiment'||typeof data.id!=='string'||!data.id.trim()||!Array.isArray(data.rows)||!data.rows.length||data.rows.length>100000)throw Error('Expected an Atlas experiment with an ID and 1–100,000 rows.');
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
