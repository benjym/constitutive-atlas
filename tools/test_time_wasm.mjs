// Analytical temporal fixtures use a separate module and never enter web/dist.
import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const create=(await import(pathToFileURL(resolve(root,'build-wasm/time-fixtures.js')))).default;
const wasm=await create();
const signature=['string','string','string','string',...Array(7).fill('number')];
const cases=[
  ['test-maxwell','', '', '0,0,0,0,0,0', 7,4,1e-10,1e-13,1e-12,1e6,20000],
  ['test-maxwell','', '', '.001,-.0005,-.0005,0,0,0', 0,2,1e-8,1e-11,1e-12,.1,20000],
  ['test-clock','', '', '0,0,0,0,0,0', 3,2,1e-8,1e-11,1e-12,1e6,20000],
  ['test-clock','2,.75', '', '0,0,0,0,0,0', 0,1,1e-8,1e-11,1e-12,1e6,20000],
  ['test-maxwell','', '', '0,0,0,0,0,0', 0,4,1e-10,1e-13,1e-12,1e6,2],
];
for(const args of cases){
  const [id,parameters,initial,rate,t,dt,rtol,atol,min,max,budget]=args;
  const command=['--mode','integrate-time','--model',id,'--strain-rate',rate,'--start-time',String(t),'--duration',String(dt),'--rtol',String(rtol),'--atol',String(atol),'--min-time-step',String(min),'--max-time-step',String(max),'--max-substeps',String(budget)];
  if(parameters)command.push('--parameters',parameters);if(initial)command.push('--initial',initial);
  const native=spawnSync(resolve(root,'build/atlas_time_solver'),command,{encoding:'utf8',timeout:30000});
  assert.ok([0,1].includes(native.status),native.stderr);
  const expected=JSON.parse(native.stdout),actual=JSON.parse(wasm.ccall('atlas_integrate_time','string',signature,args));
  assert.equal(actual.ok,expected.ok);assert.equal(actual.time,expected.time);assert.equal(actual.catalogue_hash,expected.catalogue_hash);
  actual.state.forEach((v,i)=>assert.ok(Math.abs(v-expected.state[i])<1e-8*Math.max(1,Math.abs(expected.state[i]))));
  if(!actual.ok){assert.equal(actual.time,t);assert.match(actual.message,/rolled back/);}
}
const relaxation=JSON.parse(wasm.ccall('atlas_integrate_time','string',signature,cases[0]));
assert.ok(Math.abs(relaxation.state[0]-(100000+40000*Math.exp(-2)))<.01);
const clock=JSON.parse(wasm.ccall('atlas_integrate_time','string',signature,cases[2]));
assert.ok(Math.abs(clock.state[0]-2)<1e-12);
console.log(`Physical-time analytical checks and native/Wasm parity passed for ${cases.length} success/failure cases.`);
