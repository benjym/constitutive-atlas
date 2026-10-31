import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseRecordedDocument,createRecordedDocument,recordedDocumentCSV} from '../web/recorded-document.mjs';
const {catalogue,rows}=JSON.parse(readFileSync(0,'utf8'));
let roundtrips=0,rejections=0;
function rejects(fn){assert.throws(fn);rejections++;}
const parse=doc=>parseRecordedDocument(JSON.stringify(doc),catalogue);
for(const row of rows){
 const before=JSON.stringify(row),{request:s,response:r}=row;
 const doc=createRecordedDocument(s,r,catalogue),loaded=parse(doc);
 assert.deepEqual(loaded,{specification:s,result:r,stress_scope:s.stress_scope});
 assert.deepEqual(parse(s),{specification:s,result:null,stress_scope:s.stress_scope});
 const csv=recordedDocumentCSV(s,r,catalogue),lines=csv.split('\n'),header=lines[0].split(',');
 assert.equal(lines.length,r.points.length+1);
 assert.equal(header[7],s.stress_scope+'_stress_xx_Pa');
 assert.equal(header.includes((s.stress_scope==='total'?'effective':'total')+'_stress_xx_Pa'),false);
 for(let i=0;i<r.points.length;i++){
  const cells=lines[i+1].split(',');assert.equal(cells.length,header.length);
  assert.deepEqual(cells.slice(-3),[s.stress_scope,'unavailable','']);
  assert.equal(Number(cells[7]),r.points[i].state[0]);
 }
 // All state components remain in JSON, including state not represented by CSV.
 const extendedCatalogue=structuredClone(catalogue),extendedRequest=structuredClone(s),extendedResult=structuredClone(r);
 const m=extendedCatalogue.models.find(m=>m.id===s.model);m.state.push({name:'extra_history',shape:'scalar',initial:0});
 extendedRequest.initial.push(17);extendedResult.initial.push(17);extendedResult.state.push(17);extendedResult.points.forEach(p=>p.state.push(17));
 const extended=createRecordedDocument(extendedRequest,extendedResult,extendedCatalogue);
 assert.equal(parseRecordedDocument(JSON.stringify(extended),extendedCatalogue).result.state.at(-1),17);
 doc.result.state[0]+=1;assert.equal(JSON.stringify(row),before); // detached export
 for(const change of ['catalogue','envelope','request-version','scope','result-scope','result-api','result-catalogue','result-state','extra','null-result']){
  const d=createRecordedDocument(s,r,catalogue);
  if(change==='catalogue')d.catalogue_hash='0'.repeat(64);
  if(change==='envelope')d.schema_version='experimental-recorded-replay-export-0.1';
  if(change==='request-version')d.specification.version='experimental-recorded-run-0.1';
  if(change==='scope')d.specification.stress_scope=s.stress_scope==='total'?'effective':'total';
  if(change==='result-scope')d.result.stress.scope=s.stress_scope==='total'?'effective':'total';
  if(change==='result-api')d.result.api_version='experimental-recorded-replay-0.1';
  if(change==='result-catalogue')d.result.catalogue_hash='0'.repeat(64);
  if(change==='result-state')d.result.state[0]+=1;
  if(change==='extra')d.extra=true;
  if(change==='null-result')d.result=null;
  rejects(()=>parse(d));
 }
 const legacyS=structuredClone(s);legacyS.version='experimental-recorded-run-0.1';delete legacyS.stress_scope;
 const legacyR=structuredClone(r);legacyR.api_version='experimental-recorded-replay-0.1';delete legacyR.stress;
 if(s.stress_scope==='effective'){
  const d=createRecordedDocument(legacyS,legacyR,catalogue);
  assert.equal(d.schema_version,'experimental-recorded-replay-export-0.1');
  assert.deepEqual(parse(d),{specification:legacyS,result:legacyR,stress_scope:'effective'});
  assert.deepEqual(parse(legacyS),{specification:legacyS,result:null,stress_scope:'effective'});
  const expectedHeader=['coordinate_1',...['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz'].map(c=>'strain_'+c+'_1'),...['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz'].map(c=>'effective_stress_'+c+'_Pa'),'control_error','iterations','substeps'];
  const expected=[expectedHeader.join(','),...r.points.map(p=>[p.coordinate,...p.strain,...p.state.slice(0,6),p.control_error,p.diagnostics.iterations,p.diagnostics.substeps].join(','))].join('\n');
  assert.equal(recordedDocumentCSV(legacyS,legacyR,catalogue),expected);
  const stale=structuredClone(d);stale.result.stress=r.stress;rejects(()=>parse(stale));
 }else{
  rejects(()=>parse(legacyS));rejects(()=>createRecordedDocument(legacyS,legacyR,catalogue));
 }
 assert.equal(JSON.stringify(row),before);roundtrips++;
}
const good=rows[0];
for(const change of ['parameters','initial','model','version','extra']){
 const s=structuredClone(good.request);
 if(change==='parameters')s.parameters=[];
 if(change==='initial')s.initial=[];
 if(change==='model')s.model='missing';
 if(change==='version')s.version='unknown';
 if(change==='extra')s.extra=1;
 rejects(()=>parse(s));
}
rejects(()=>parseRecordedDocument('9007199254740993',catalogue));
rejects(()=>parseRecordedDocument('null',catalogue));
process.stdout.write(JSON.stringify({roundtrips,rejections}));
