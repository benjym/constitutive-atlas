import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createLaboratoryDocument,parseLaboratoryDocument,laboratoryDocumentCSV} from '../web/laboratory-document.mjs';
import {verifyScopedLaboratory} from '../web/laboratory-scope.mjs';
import {createLoading,controlFromBits} from '../web/loading.mjs';
const {catalogue,rows,legacy}=JSON.parse(readFileSync(0,'utf8'));
let rejections=0;
const rejects=fn=>{assert.throws(fn);rejections++;};
const parse=d=>parseLaboratoryDocument(JSON.stringify(d),catalogue);
for(const row of rows){
 const {request:s,response:r}=row,before=JSON.stringify(row),d=createLaboratoryDocument(s,r,catalogue);
 assert.equal(d.schema_version,'atlas-laboratory-export-0.2');assert.deepEqual(parse(d),s);assert.deepEqual(d.result,r);assert.deepEqual(d.result.points.at(-1).state,r.points.at(-1).state);
 const csv=laboratoryDocumentCSV(s,r,catalogue),lines=csv.split('\n'),header=lines[0].split(',');
 assert.equal(header[3],s.stress_scope+'_mean_stress_Pa');assert.equal(header[4],s.stress_scope+'_signed_deviatoric_stress_Pa');assert.equal(lines.length,r.points.length+1);
 for(let i=0;i<r.points.length;i++){
  const cells=lines[i+1].split(',');assert.equal(cells.length,header.length);assert.equal(cells[6],s.stress_scope);assert.equal(cells[7],r.pore_pressure.availability);
  if(r.pore_pressure.availability==='unavailable')assert.equal(cells[5],'');else assert.equal(Number(cells[5]),r.points[i].u);
 }
 d.specification.initial[0]++;d.result.points[0].state[0]++;assert.equal(JSON.stringify(row),before);
 for(const kind of ['envelope','catalogue','extra','scope','model','parameters','initial','settings','result-scope','pore','u','version','prefix','null']){
  const bad=createLaboratoryDocument(s,r,catalogue);
  if(kind==='envelope')bad.schema_version='unknown';
  if(kind==='catalogue')bad.catalogue_hash='0'.repeat(64);
  if(kind==='extra')bad.extra=true;
  if(kind==='scope')bad.specification.stress_scope=s.stress_scope==='total'?'effective':'total';
  if(kind==='model')bad.specification.model='missing';
  if(kind==='parameters')bad.result.parameters[0]++;
  if(kind==='initial')bad.result.initial[0]++;
  if(kind==='settings')bad.result.integration_settings.max_depth++;
  if(kind==='result-scope')bad.result.stress.scope=s.stress_scope==='total'?'effective':'total';
  if(kind==='pore')bad.result.pore_pressure.availability='other';
  if(kind==='u')bad.result.points[1].u=r.pore_pressure.availability==='reconstructed'?null:0;
  if(kind==='version')bad.result.api_version='legacy';
  if(kind==='prefix')bad.result.points.pop();
  if(kind==='null')bad.result=null;
  rejects(()=>parse(bad));
 }
 if(s.stress_scope==='total'){
  const old=structuredClone(s);delete old.response_contract;delete old.stress_scope;
  rejects(()=>createLaboratoryDocument(old,r,catalogue));
  rejects(()=>laboratoryDocumentCSV(old,r,catalogue));
 }
 assert.equal(JSON.stringify(row),before);
}
for(const row of legacy){
 const {request:s,response:r}=row,d=createLaboratoryDocument(s,r,catalogue);
 assert.equal(d.schema_version,'0.1');assert.deepEqual(parse(d),s);
 assert.deepEqual(d,{schema_version:'0.1',catalogue_hash:catalogue.sha256,specification:s,result:r});
 const expected=['axial_strain,radial_strain,volumetric_strain,p_Pa,q_signed_Pa,pore_pressure_Pa,iterations,substeps',...r.points.map(p=>[p.strain[0],p.strain[1],p.strain.slice(0,3).reduce((a,b)=>a+b,0),p.p,p.q_signed,p.u,p.iterations,p.substeps].join(','))].join('\n');
 assert.equal(laboratoryDocumentCSV(s,r,catalogue),expected);
 const stale=structuredClone(d);stale.specification.stress_scope='total';rejects(()=>parse(stale));
 const total=structuredClone(d);total.specification.model='scope-synthetic-total-elastic';rejects(()=>parse(total));
}
// A tiny target yields a representable negative zero in an interior control.
// This is a document/transport fixture; its mechanical fields are retained data,
// not a constitutive reference for that artificial target.
const seed=rows.find(x=>x.label==='scoped-elastic-1'),s=structuredClone(seed.request),r=structuredClone(seed.response);
s.target=-Number.MIN_VALUE;s.steps=2;s.cycles=0;s.loading=createLoading(s);
const controls=s.loading.controls_bits.map(controlFromBits);assert.ok(Object.is(controls[1],-0));
delete r.target;delete r.cycles;r.loading={version:s.loading.version,encoding:s.loading.encoding,controls_bits:s.loading.controls_bits,controls};
r.points.forEach((p,i)=>p.control=controls[i]);
const exported=createLaboratoryDocument(s,r,catalogue),serialized=JSON.stringify(exported),parsed=JSON.parse(serialized);assert.ok(!Object.is(parsed.result.points[1].control,-0));
assert.deepEqual(parseLaboratoryDocument(serialized,catalogue),s);
// The raw response checker still requires exact signs; only document import may
// restore a sign erased by JSON, after checking numeric equality and exact bits.
rejects(()=>verifyScopedLaboratory(parsed.result,s,catalogue));
const legacyS=structuredClone(s),legacyR=structuredClone(r);delete legacyS.response_contract;delete legacyS.stress_scope;delete legacyR.stress;delete legacyR.pore_pressure;legacyR.api_version='experimental-laboratory-controls-0.1';legacyR.points.forEach(p=>p.u=0);
const legacyExact=createLaboratoryDocument(legacyS,legacyR,catalogue);assert.equal(legacyExact.schema_version,'0.2');assert.deepEqual(parse(legacyExact),legacyS);
for(const kind of ['bits','numeric','point','wire-shape','prefix-control']){
 const d=JSON.parse(serialized);
 if(kind==='bits')d.result.loading.controls_bits[1]='0'.repeat(16);
 if(kind==='numeric')d.result.loading.controls[1]=1;
 if(kind==='point')d.result.points[1].control=1;
 if(kind==='wire-shape')d.result.loading.controls.pop();
 if(kind==='prefix-control')d.result.points[1].control=false;
 rejects(()=>parse(d));
}
const overflow=structuredClone(seed.response);overflow.points[1].strain=[1e308,1e308,1e308,0,0,0];rejects(()=>laboratoryDocumentCSV(seed.request,overflow,catalogue));
const failure=structuredClone(seed.response);failure.ok=false;failure.points.pop();assert.deepEqual(parse(createLaboratoryDocument(seed.request,failure,catalogue)),seed.request);
const empty=structuredClone(failure);empty.points=[];assert.deepEqual(parse(createLaboratoryDocument(seed.request,empty,catalogue)),seed.request);
rejects(()=>parseLaboratoryDocument('9007199254740993',catalogue));rejects(()=>parseLaboratoryDocument('null',catalogue));
process.stdout.write(JSON.stringify({scoped_roundtrips:rows.length,legacy_roundtrips:legacy.length,zero_sign_roundtrip:true,rejections}));
