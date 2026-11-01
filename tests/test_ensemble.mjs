import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {makeStudy,defaultConfigurations,exportStudy,importStudy,stable} from '../web/ensemble.mjs';
import {EnsembleQueue} from '../web/ensemble-queue.mjs';
const sourceBytes=readFileSync(new URL('../data/curated/OPARA-TXCD-100.json.gz',import.meta.url));
const source=JSON.parse(gunzipSync(sourceBytes));
const record={...source,version:'atlas-ensemble-experiment-0.1',source_asset_sha256:createHash('sha256').update(sourceBytes).digest('hex')};
const catalogue={schema_version:'0.1',sha256:'a'.repeat(64),models:['linear-elastic','drucker-prager','modified-cam-clay'].map(id=>JSON.parse(readFileSync(new URL('../models/'+id+'.json',import.meta.url))))};
const fresh=()=>makeStudy(record,catalogue,defaultConfigurations(catalogue));
test('15 independent deterministic requests preserve direct radial source order and fixed preparation',()=>{
 const before=stable(record),s=fresh();assert.equal(s.jobs.length,15);assert.equal(new Set(s.jobs.map(j=>j.id)).size,15);assert.equal(stable(s),stable(fresh()));
 for(const j of s.jobs){assert.equal(j.status,'queued');assert.equal(j.specification.path.knots.length,95);assert.deepEqual(j.specification.initial.slice(0,7),[103720,103720,103720,0,0,0,.416]);
  for(let i=0;i<95;i++)assert.deepEqual(j.specification.path.knots[i],{coordinate:i,targets:[record.rows[i].axial_strain,record.rows[i].radial_effective_stress,record.rows[i].radial_effective_stress,0,0,0]});
 }
 assert.equal(s.jobs[10].specification.initial[7],200000);assert.equal(s.jobs[0].specification.path.knots.at(-1).targets[0],.00992);
 s.jobs[0].specification.path.knots[0].targets[0]=12;assert.equal(s.jobs[1].specification.path.knots[0].targets[0],0);assert.equal(stable(record),before);
});
test('variations are OAT, deduplicated, explicit and never mutate baseline',()=>{
 const c=defaultConfigurations(catalogue);c[0].variations.E=[24e6,24e6,30e6];c[0].variations.nu=[];const s=makeStudy(record,catalogue,c);assert.equal(s.jobs.filter(j=>j.model==='linear-elastic').length,2);
 const baseline=s.jobs[0].parameters;for(const j of s.jobs.filter(j=>j.model==='linear-elastic'&&j.change))assert.deepEqual(Object.keys(j.parameters).filter(k=>j.parameters[k]!==baseline[k]),[j.change.parameter]);
});
test('invalid inputs retain per-run rejections rather than silently replacing state',()=>{
 const c=defaultConfigurations(catalogue);c[0].variations.E=[-1];c[2].history.pc=100000;const s=makeStudy(record,catalogue,c);assert.equal(s.jobs.find(j=>j.change?.value===-1).status,'rejected');assert.equal(s.jobs.filter(j=>j.model==='modified-cam-clay'&&j.status==='rejected').length,5);assert.equal(s.jobs[0].status,'queued');
 c[0].parameters.p_ref=200000;assert.match(makeStudy(record,catalogue,c).jobs[0].message,/scale/);
});
test('nonfinite baseline/history fail before snapshots can silently serialize null',()=>{
 for(const mutate of [c=>c[0].parameters.E=NaN,c=>c[2].history.pc=Infinity]){const c=defaultConfigurations(catalogue);mutate(c);assert.throws(()=>makeStudy(record,catalogue,c),/finite/);}
});
test('source conventions, window, ordering and model scope fail closed',()=>{
 for(const mutate of [r=>r.initial.void_ratio=.7,r=>r.rows.reverse(),r=>r.rows.pop(),r=>r.conventions.stress_unit='kPa',r=>r.provenance.member_sha256='0'.repeat(64)]){const r=structuredClone(record);mutate(r);assert.throws(()=>makeStudy(r,catalogue,defaultConfigurations(catalogue)));}
 const c=structuredClone(catalogue);c.models[0].state[0].name='total_stress';assert.throws(()=>makeStudy(record,c,defaultConfigurations(c)));
});
test('queued export roundtrip validates catalogue, source, definitions and exact requests',()=>{
 const s=fresh(),doc=exportStudy(s,catalogue,record);assert.deepEqual(importStudy(JSON.stringify(doc),catalogue,record),s);
 for(const mutate of [d=>d.study.catalogue_hash='b'.repeat(64),d=>d.study.experiment.window.last_row=93,d=>d.study.model_definitions[0].parameters.E.default=1,d=>d.study.jobs[0].specification.initial[6]=.7,d=>d.study.jobs[0].status='completed',d=>d.study.jobs.reverse()]){const d=structuredClone(doc);mutate(d);assert.throws(()=>importStudy(JSON.stringify(d),catalogue,record));}
 assert.throws(()=>importStudy('{"version":1,"version":2}',catalogue,record));
});
test('missing model is visibly excluded and cannot be silently substituted',()=>{
 const c={...catalogue,models:catalogue.models.slice(1)},configs=defaultConfigurations(c);assert.equal(configs[0].enabled,false);assert.equal(makeStudy(record,c,configs).jobs.length,10);configs[0].enabled=true;assert.throws(()=>makeStudy(record,c,configs));
});
const job=(id,status='queued')=>({id,status,message:'',result:null});
test('queue is serial, keeps stopped prefixes, skips rejected jobs and continues after errors',async()=>{
 let active=0,max=0;const calls=[];
 const q=new EnsembleQueue(async j=>{active++;max=Math.max(max,active);calls.push(j.id);await new Promise(r=>setTimeout(r,1));active--;if(j.id===2)throw Error('domain failed');return {ok:j.id===0,points:[j.id],message:'retained'};});
 const s={jobs:[job(0),job(1,'rejected'),job(2),job(3)]};await q.run(s);assert.equal(max,1);assert.deepEqual(calls,[0,2,3]);assert.deepEqual(s.jobs.map(j=>j.status),['completed','rejected','error','stopped']);assert.deepEqual(s.jobs[3].result.points,[3]);
});
test('cancel aborts active work, cancels pending and suppresses late responses',async()=>{
 let late;const q=new EnsembleQueue(()=>new Promise(r=>{late=r;}));const s={jobs:[job(0),job(1)]};const running=q.run(s);q.cancel();await running;late({ok:true});await Promise.resolve();assert.deepEqual(s.jobs.map(j=>j.status),['cancelled','cancelled']);assert.equal(s.jobs[0].result,null);assert.equal(q.running,false);
});
test('timeout aborts executor and proceeds to next request',async()=>{
 let aborted=false;const q=new EnsembleQueue((j,signal)=>j.id===0?new Promise(()=>signal.addEventListener('abort',()=>{aborted=true;})):Promise.resolve({ok:true}),()=>{},5);
 const s={jobs:[job(0),job(1)]};await q.run(s);assert.equal(aborted,true);assert.deepEqual(s.jobs.map(j=>j.status),['timeout','completed']);
});
