import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const create=(await import(pathToFileURL(resolve(root,'build-wasm/research.js')))).default;
const wasm=await create();
const reference=JSON.parse(readFileSync(resolve(root,'tests/reference/terracotta-2024-author-rhs.json')));
const hold=()=>[0,0,0],rate=v=>[0,1,v];
const signature=[...Array(7).fill('string'),...Array(8).fill('number')];
for(const c of reference.cases){
 const rows=c.stages.flatMap(s=>{
   let controls=Array.from({length:6},hold);
   if(s.kind==='txu')controls=[rate(s.rate),rate(-s.rate/2),rate(-s.rate/2),hold(),hold(),hold()];
   if(s.kind==='iso')controls=[rate(s.rate),rate(s.rate),rate(s.rate),hold(),hold(),hold()];
   if(s.kind==='oed')controls=[rate(s.rate),hold(),hold(),hold(),hold(),hold()];
   return [s.duration,4,...controls.flat()];
 });
 const wire=rows.join(','),ids=c.stages.map((_,i)=>`stage-${i}`).join(',');
 const args=['terracotta-2024-fig1','','','','',wire,ids,0,1e-6,1e-10,1e-12,1e6,100000,1e-10,40];
 const actual=JSON.parse(wasm.ccall('atlas_run_schedule','string',signature,args));assert.equal(actual.ok,true,actual.message);
 const native=spawnSync(resolve(root,'build/atlas_research_solver'),['--mode','schedule','--model',args[0],'--segments',wire,'--segment-ids',ids,'--rtol','1e-6','--atol','1e-10','--max-substeps','100000'],{encoding:'utf8',timeout:60000});
 assert.equal(native.status,0,native.stderr);const expected=JSON.parse(native.stdout);
 assert.equal(actual.catalogue_hash,expected.catalogue_hash);assert.equal(actual.points.length,expected.points.length);
 actual.points.forEach((p,i)=>{const q=expected.points[i];assert.equal(p.time,q.time);assert.equal(p.side,q.side);
   for(const key of ['state','strain','observables'])p[key].forEach((v,j)=>assert.ok(Math.abs(v-q[key][j])<=1e-7*Math.max(1,Math.abs(q[key][j])),`${c.id} ${key}[${j}]`));
   assert.ok(p.nonlinear_residual_norm<=1e-10);assert.ok(p.temporal_error_norm<=1);
 });
 const regular=actual.points.filter(p=>p.segment>=0&&p.side==='left');assert.equal(regular.length,c.points.length);
 regular.forEach((p,i)=>{const q=c.points[i];assert.equal(p.time,q.time);
   assert.ok(Math.abs(p.observables[6]-q.pressure)<=100);assert.ok(Math.abs(p.observables[7]-q.signed_q)<=100);
 });
}
const bad=JSON.parse(wasm.ccall('atlas_integrate_time','string',['string','string','string','string',...Array(7).fill('number')],['terracotta-2024-fig1','','','0,0,0,.00001,0,0',0,1,1e-6,1e-9,1e-12,1e6,20000]));
assert.equal(bad.ok,false);assert.equal(bad.time,0);
console.log(`Terracotta research draft: ${reference.cases.length} source-reference native/Wasm histories and out-of-scope rollback passed.`);
