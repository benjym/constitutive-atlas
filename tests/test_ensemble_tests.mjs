import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash,webcrypto} from 'node:crypto';
import {replayGap,validateReplayRecord,filterTests,fetchReplayAsset,loadEnsembleCatalogue} from '../web/ensemble-experiments.mjs';
import {defaultConfigurations,makeStudy,exportStudy,importStudy,resultSeries,stable} from '../web/ensemble.mjs';
import {ensembleFigure} from '../web/ensemble-plots.mjs';
const index=JSON.parse(readFileSync(new URL('../data/curated/index.json',import.meta.url))).records;
const source=id=>{const e=index.find(e=>e.id===id),raw=readFileSync(new URL('../data/curated/'+e.path,import.meta.url));assert.equal(createHash('sha256').update(raw).digest('hex'),e.sha256);return {...JSON.parse(gunzipSync(raw)),source_asset_sha256:e.sha256,version:'atlas-ensemble-experiment-0.2'};};
const catalogue={schema_version:'0.1',sha256:'1'.repeat(64),models:readdirSync(new URL('../models/',import.meta.url)).filter(f=>f.endsWith('.json')).map(f=>JSON.parse(readFileSync(new URL('../models/'+f,import.meta.url))))};
const configs=()=>defaultConfigurations(catalogue);
test('all twelve explicit-state triaxial tests preserve initial state, every source row and exact study identity',()=>{
 for(const entry of index.filter(e=>e.id.startsWith('OPARA-'))){
  const record=source(entry.id),before=stable(record);validateReplayRecord(record);const study=makeStudy(record,catalogue,configs());
  assert.equal(study.experiment.id,entry.id);assert.equal(study.experiment.initial.void_ratio,record.initial.void_ratio);
  for(const job of study.jobs.filter(j=>j.specification)){
   assert.deepEqual(job.specification.initial.slice(0,6),record.initial.effective_stress);
   assert.equal(job.specification.path.knots.length,record.rows.length);
   assert.deepEqual(job.specification.path.knots.map(k=>k.targets[0]),record.rows.map(r=>r.axial_strain-record.rows[0].axial_strain));
  }
  assert.equal(stable(record),before);assert.deepEqual(importStudy(JSON.stringify(exportStudy(study,catalogue,record)),catalogue,record),study);
 }
});
test('undrained replay controls volume and axisymmetry; measured effective radial stress and pore pressure are not imposed',()=>{
 const record=source('OPARA-TXCU-100'),study=makeStudy(record,catalogue,configs()),path=study.jobs[0].specification.path;
 assert.deepEqual(path.controls[1],{kind:'strain',coefficients:[1,1,1,0,0,0]});assert.deepEqual(path.controls[2],{kind:'stress',coefficients:[0,1,-1,0,0,0]});
 assert.ok(path.knots.every(k=>k.targets.slice(1).every(x=>x===0)));
 const changed=structuredClone(record);for(const row of changed.rows.slice(1)){row.radial_effective_stress+=123;row.pore_pressure+=456;}
 assert.deepEqual(makeStudy(changed,catalogue,configs()).jobs[0].specification.path,path);
 const drained=source('OPARA-TXCD-20'),d=makeStudy(drained,catalogue,configs()).jobs[0].specification.path;
 assert.deepEqual(d.knots.map(k=>k.targets[1]),drained.rows.map(r=>r.radial_effective_stress));
 const high=makeStudy(source('OPARA-TXCD-300'),catalogue,configs());assert.equal(high.jobs.find(j=>j.model==='modified-cam-clay'&&!j.change).status,'rejected');
});
test('acquisition order, repeated strains and reversals survive; missing state/scope and source identities fail closed',()=>{
 const r=source('OPARA-TXCD-20');r.rows[2].axial_strain=r.rows[1].axial_strain;r.rows[3].axial_strain=-.0001;
 const s=makeStudy(r,catalogue,configs());assert.equal(s.jobs[0].specification.path.knots[3].targets[0],-.0001);
 const other=source('OPARA-TXCU-20');assert.throws(()=>importStudy(JSON.stringify(exportStudy(s,catalogue,r)),catalogue,other),/identity/);
 assert.match(replayGap(source('GEOLAB-FONTAINEBLEAU-TRIAX-CD-1')),/effective/);
 assert.match(replayGap({kind:'measurement-series'}),/Source channels/);
 for(const mutate of [r=>delete r.initial.void_ratio,r=>r.initial.effective_stress[1]=1,r=>r.provenance.member_sha256='bad',r=>delete r.rows[1].volumetric_strain]){const bad=source('OPARA-TXCU-20');mutate(bad);assert.throws(()=>validateReplayRecord(bad));}
});
test('pore-pressure inference and effective-stress plot use physical channels; absent measurements retain plot gaps',()=>{
 const record=source('OPARA-TXCU-100'),s0=record.initial.effective_stress[1],q=10000;
 const job={id:'linear:baseline',model:'linear',label:'Baseline',change:null,result:{points:[{strain:[0,0,0,0,0,0],state:[s0,s0,s0]},{strain:[.001,-.0005,-.0005,0,0,0],state:[s0+q,s0-q/2,s0-q/2]}]}};
 assert.equal(resultSeries(job,'volume',record)[1][1],0);assert.deepEqual(resultSeries(job,'path',record)[1],[s0/1000,15]);
 assert.ok(Math.abs(resultSeries(job,'pore',record)[1][1]-(record.rows[1].cell_pressure-record.rows[0].cell_pressure+q/2)/1000)<1e-10);
 const p=ensembleFigure(record,[job],'pore',job.id,{},1);assert.ok(Math.abs(p.data[0].y[1]-record.rows[1].pore_pressure/1000)<1e-10);assert.match(p.layout.yaxis.title.text,/Pore-pressure/);
 const missing={rows:[{axial_strain:0,q:0},{axial_strain:.1,q:100}]};assert.deepEqual(ensembleFigure(missing,[],'volume',null,{},1).data[0].y,[null,null]);
 const native={kind:'test-summary',columns:[{key:'c0',name:'Pressure',unit:'kPa'},{key:'c1',name:'Density',unit:'1'}],source_plot:{x:'c0',y:'c1'},rows:[{c0:10,c1:.7},{c0:20,c1:.8}]};const f=ensembleFigure(native,[],'source',null,{},2);assert.deepEqual(f.data[0].x,[10,20]);assert.equal(f.data[0].mode,'markers');
});
test('catalogue filters keep source-only records and loader rejects corrupted replay bytes',async()=>{
 const entries=[{id:'A',protocol:'drained-triaxial',material:'Sand',replay:{}},{id:'B',protocol:'oedometer',material:'Clay',replay:null}];
 assert.deepEqual(filterTests(entries,{search:'clay'}),[entries[1]]);assert.deepEqual(filterTests(entries,{availability:'replay'}),[entries[0]]);assert.deepEqual(filterTests(entries,{protocol:'oedometer'}),[entries[1]]);
 const bytes=new TextEncoder().encode(JSON.stringify({id:'A'})),entry={path:'ensemble-tests/A.json',size_bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};
 const fetcher=async()=>({ok:true,arrayBuffer:async()=>bytes.buffer});
 assert.deepEqual(await fetchReplayAsset(entry,fetcher),{id:'A'});await assert.rejects(()=>fetchReplayAsset({...entry,sha256:'0'.repeat(64)},fetcher),/checksum/);await assert.rejects(()=>fetchReplayAsset({...entry,path:'../A.json'},fetcher),/entry/);
 await assert.rejects(()=>loadEnsembleCatalogue(async url=>({ok:true,json:async()=>url.includes('experiments/')?{schema_version:'0.1',experiments:[entries[0],entries[0]]}:{version:'atlas-ensemble-tests-0.1',tests:[]}})),/identities/);
});
