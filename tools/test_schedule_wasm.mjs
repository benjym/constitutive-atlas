// Independent analytical mixed-control cases, then native/Wasm parity.
import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const create=(await import(pathToFileURL(resolve(root,'build-wasm/time-fixtures.js')))).default;
const wasm=await create();
const hold=(stress=false)=>[+stress,0,0], rate=(value,stress=false)=>[+stress,1,value];
const allHold=(stress=false)=>Array.from({length:6},()=>hold(stress));
const segment=(duration,controls)=>[duration,4,...controls.flat()];
const tests=[
 {id:'test-maxwell',names:'creep',rows:[segment(4,allHold(true))],check(d){
   const p=d.points.at(-1);assert.equal(p.time,4);assert.ok(Math.abs(p.strain[0]-40000/(2*12e6*2)*4)<1e-12);
   assert.ok(Math.abs(p.observables[0]-140000)<1e-5);assert.deepEqual(d.points[1].strain_rate,Array(6).fill(null));
 }},
 {id:'test-kelvin',names:'load,relax',rows:[segment(1,[rate(.001),rate(-.0005),rate(-.0005),hold(),hold(),hold()]),segment(2,allHold())],check(d){
   const [left,right]=d.points.filter(p=>p.time===1);assert.deepEqual(left.state,right.state);assert.deepEqual(left.strain,right.strain);
   assert.ok(Math.abs(left.observables[0]-right.observables[0]-48000)<1e-5);assert.deepEqual(d.points.at(-1).state,right.state);
 }},
 {id:'test-kelvin',names:'ramp,creep',budget:100000,rows:[segment(1,[rate(40000,true),rate(-20000,true),rate(-20000,true),hold(true),hold(true),hold(true)]),segment(2,allHold(true))],check(d){
   const at1=40000*(1-2*(1-Math.exp(-.5))),exact=40000+(at1-40000)*Math.exp(-1),p=d.points.at(-1);
   assert.equal(p.time,3);assert.ok(Math.abs(p.state[0]-100000-exact)<3);assert.ok(Math.abs(p.observables[0]-140000)<1e-4);
 }},
 {id:'test-maxwell',names:'domain',parameters:'20000000,12000000,2,.6',rows:[segment(1,allHold(true))],failure:true,check(d){
   const p=d.points.at(-1);assert.equal(p.time,.5);assert.deepEqual(p.state,[140000,80000,80000,0,0,0]);
   assert.ok(Math.abs(p.strain[0]-40000/(2*12e6*2)*.5)<1e-12);
 }},
 {id:'test-maxwell',names:'budget',budget:2,rows:[segment(4,allHold())],failure:true,check(d){
   assert.equal(d.points.at(-1).time,0);assert.deepEqual(d.points.at(-1).state,[140000,80000,80000,0,0,0]);
 }},
];
function compare(a,b,path=''){
 // Roundoff may alter adaptive work counts and normalized estimates. Compare
 // scientific outputs, while independently checking diagnostic bounds.
 if(/\.(iterations|substeps|rejected)$/.test(path)){assert.ok(Number.isInteger(a)&&a>=0);assert.ok(Number.isInteger(b)&&b>=0);return;}
 if(path.endsWith('.nonlinear_residual_norm')){assert.ok(a>=0&&a<=1e-10);assert.ok(b>=0&&b<=1e-10);return;}
 if(path.endsWith('.temporal_error_norm')){assert.ok(a>=0&&a<=1);assert.ok(b>=0&&b<=1);return;}
 if(typeof a==='number'&&typeof b==='number')assert.ok(Math.abs(a-b)<=1e-8*Math.max(1,Math.abs(b)),`${path}: ${a} != ${b}`);
 else if(Array.isArray(a)){assert.equal(a.length,b.length,path);a.forEach((v,i)=>compare(v,b[i],`${path}[${i}]`));}
 else if(a&&typeof a==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const k of Object.keys(a))compare(a[k],b[k],`${path}.${k}`);}
 else assert.equal(a,b,path);
}
for(const test of tests){
 const wire=test.rows.flat().join(','),parameters=test.parameters??'',budget=test.budget??20000;
 const args=[test.id,parameters,'','','',wire,test.names,0,1e-8,1e-11,1e-12,1e6,budget,1e-10,40];
 const actual=JSON.parse(wasm.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],args));
 assert.equal(actual.ok,!test.failure,actual.message);test.check(actual);
 const command=['--mode','schedule','--model',test.id,'--segments',wire,'--segment-ids',test.names,'--rtol','1e-8','--atol','1e-11','--max-substeps',String(budget)];
 if(parameters)command.push('--parameters',parameters);
 const native=spawnSync(resolve(root,'build/atlas_time_solver'),command,{encoding:'utf8',timeout:30000});
 assert.equal(native.status,test.failure?1:0,native.stderr);compare(actual,JSON.parse(native.stdout));
}
const observed=JSON.parse(wasm.ccall('atlas_observe_time','string',['string','string','string','string','number'],['test-kelvin','','','.001,-.0005,-.0005,0,0,0',0]));
assert.deepEqual(observed,{ok:true,values:[148000,76000,76000,0,0,0]});
console.log(`Timed controls: ${tests.length} analytical success/failure cases and observable native/Wasm verification passed.`);
