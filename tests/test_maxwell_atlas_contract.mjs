import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {modelId,modelSha256,solver,presetNames,preset,request,verifyResult,verifyReplay,exportRun,importRun,parseRunJSON,validateControls,types} from '../web/maxwell-atlas-contract.mjs';
const base=new URL('../docs/ingestion/maxwell-itasca900/integration-v1/',import.meta.url);
const keys=['schema_version','units','model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments','solver'];
const controls=r=>Object.fromEntries(keys.map(k=>[k,structuredClone(r[k])]));
const fixtures=[];
for(const backend of ['native','wasm'])for(const suffix of ['-raw.json','-transactions-raw.json'])for(const row of JSON.parse(readFileSync(new URL(backend+suffix,base))))for(const [repeat,call]of row.calls.entries()){
 const r=JSON.parse(call.stdout);if(r.points)fixtures.push({backend,id:row.id,repeat,r,c:controls(r),identity:{model:modelId,model_sha256:modelSha256,catalogue_hash:r.catalogue_hash,release_revision:'saved-historical-fixture'}});
}
const usable=fixtures.filter(f=>f.r.ok&&f.id!=='refine-coarse');
const fixture=usable.find(f=>f.id==='load-hold-reverse');
test('four normalized source presets are exact copies of the existing examples',()=>{
 assert.equal(presetNames.length,4);
 for(const name of presetNames){const source=JSON.parse(readFileSync(new URL('../examples/maxwell/'+name+'.json',import.meta.url)));assert.deepEqual(preset(name),{...source,solver:{...solver}});}
 const p=preset('relaxation');p.initial[0]=0;assert.notEqual(preset('relaxation').initial[0],0);
 assert.throws(()=>preset('__proto__'));
});
test('all successful fixed-policy historical responses pass on both backends and repetitions',()=>{
 assert.equal(usable.length,32);
 assert.deepEqual([...new Set(usable.filter(f=>f.id.startsWith('restart-')).map(f=>f.c.start_time))].sort((a,b)=>a-b),[4,8]);
 for(const {r,c,identity}of usable)assert.equal(verifyResult(r,identity,c),r);
});
test('coarse settings and saved solver failure remain rejected',()=>{
 assert.equal(fixtures.filter(f=>f.id==='refine-coarse').length,4);
 for(const f of fixtures.filter(f=>f.id==='refine-coarse'||!f.r.ok))assert.throws(()=>verifyResult(f.r,f.identity,f.c));
});
test('ABI preserves every segment/component, input and fixed setting',()=>{
 for(const f of usable){const a=request(f.c,f.identity);assert.equal(a.length,types.length);assert.equal(a[6],f.c.segments.map(s=>s.id).join(','));const wire=a[5].split(',').map(Number);assert.equal(wire.length,20*f.c.segments.length);for(const[i,s]of f.c.segments.entries()){assert.deepEqual(wire.slice(i*20,i*20+2),[s.duration,s.samples]);for(const[j,v]of s.controls.entries())assert.deepEqual(wire.slice(i*20+2+j*3,i*20+5+j*3),[+(v.quantity==='stress'),+(v.kind==='rate'),v.value??0]);}}
});
test('strict JSON rejects nested duplicate names, escaped aliases and lossy numbers',()=>{
 for(const text of ['{"x":1,"x":2}','{"a":[{"x":1,"\\u0078":2}]}','{"x":1e999}','{"x":9007199254740993}'])assert.throws(()=>parseRunJSON(text));
 assert.deepEqual(parseRunJSON('{"x":[1,{"x":2}],"y":"{1e999}"}'),{x:[1,{x:2}],y:'{1e999}'});
});
test('invalid controls cannot reach the ABI',()=>{
 const changes=[c=>c.parameters[0]=0,c=>c.initial.pop(),c=>delete c.initial[2],c=>c.initial_strain_rate[3]=Infinity,c=>c.solver.maximum_substeps++,c=>c.extra=true,c=>c.segments[0].extra=true,c=>c.segments[0].controls.pop(),c=>c.segments[0].controls[0]={quantity:'stress',kind:'target',value:1},c=>c.segments[0].controls[0]={quantity:'stress',kind:'hold',value:0},c=>c.segments[1].id=c.segments[0].id,c=>c.segments[0].samples=201,c=>c.start_time=1e30,c=>c.start_time=-1,c=>c.segments[0].duration=0];
 for(const change of changes){const c=structuredClone(fixture.c);change(c);assert.throws(()=>request(c,fixture.identity));}
 const c=structuredClone(fixture.c);c.start_time=1e16;c.segments=[{...c.segments[0],duration:2,samples:2}];assert.throws(()=>validateControls(c));
 assert.throws(()=>request(fixture.c,{...fixture.identity,model_sha256:'0'.repeat(64)}));
});
test('complete history mutation rejection includes mixed transition nulls',()=>{
 const changes=[r=>r.extra=1,r=>r.points[2].extra=1,r=>delete r.points[2].strain_rate[0],r=>r.ok=false,r=>r.catalogue_hash='0'.repeat(64),r=>r.units='MPa',r=>r.initial[0]++,r=>r.solver.maximum_depth++,r=>r.segments[0].duration++,r=>r.points.pop(),r=>r.points[2].time+=.1,r=>r.points[2].segment++,r=>r.points[2].side='right',r=>r.points[2].state.pop(),r=>r.points[2].observables[0]++,r=>r.points[2].strain_rate[0]=null,r=>r.points[1].state[0]++,r=>r.points[1].strain[0]++,r=>r.points[0].strain_rate[0]++,r=>r.points[2].iterations=.5,r=>r.points[2].substeps=-1,r=>r.points[2].temporal_error_norm=null];
 for(const change of changes){const r=structuredClone(fixture.r);change(r);assert.throws(()=>verifyResult(r,fixture.identity,fixture.c));}
 const mixed=usable.find(f=>f.id==='oedometer');assert.deepEqual(mixed.r.points[1].strain_rate,[0,0,null,0,0,0]);
 for(const [index,value]of [[2,0],[0,null]]){const r=structuredClone(mixed.r);r.points[1].strain_rate[index]=value;assert.throws(()=>verifyResult(r,mixed.identity,mixed.c));}
});
test('saved runs bind full provenance and ABI; replay detects unplotted changes',()=>{
 for(const f of usable){const saved=exportRun(f.c,f.r,f.identity),restored=importRun(JSON.stringify(saved),f.identity);assert.deepEqual(restored,{controls:f.c,result:f.r});verifyReplay(restored.result,f.r);}
 const saved=exportRun(fixture.c,fixture.r,fixture.identity);
 for(const mutate of [s=>s.provenance.release_revision='other',s=>delete s.provenance.release_revision,s=>s.provenance.extra=1,s=>s.request.args[5]='0',s=>s.result.points[2].state[5]++]){const s=structuredClone(saved);mutate(s);assert.throws(()=>importRun(JSON.stringify(s),fixture.identity));}
 const r=structuredClone(fixture.r);r.points[2].strain[5]+=1e-9;assert.throws(()=>verifyReplay(r,fixture.r));
});
