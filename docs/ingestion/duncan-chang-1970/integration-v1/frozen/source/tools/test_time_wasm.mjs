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

// Cartesian reference for the generated tensor-square primitive; no Atlas math.
const toMatrix=v=>[[v[0],v[3]/Math.SQRT2,v[5]/Math.SQRT2],[v[3]/Math.SQRT2,v[1],v[4]/Math.SQRT2],[v[5]/Math.SQRT2,v[4]/Math.SQRT2,v[2]]];
const squareReference=v=>{
  const a=toMatrix(v),b=Array.from({length:3},()=>Array(3).fill(0));
  for(let i=0;i<3;i++)for(let j=0;j<3;j++)for(let k=0;k<3;k++)b[i][j]+=a[i][k]*a[k][j];
  return [b[0][0],b[1][1],b[2][2],Math.SQRT2*b[0][1],Math.SQRT2*b[1][2],Math.SQRT2*b[0][2]].map(x=>x/2);
};
const tensorCases=[Array(6).fill(0),[1,2,-3,0,0,0],[0,0,0,2*Math.SQRT2,0,0],[1,-2,3,.4,-.7,1.2],
  ...Array.from({length:20},(_,i)=>Array.from({length:6},(_,j)=>3*Math.sin((i+1)*(j+2))))];
for(const v of tensorCases){
  const initial=v.join(','),rate='0,0,0,0,0,0';
  const native=spawnSync(resolve(root,'build/atlas_time_solver'),['--model','test-tensor-square','--mode','evaluate-time','--initial',initial,'--strain-rate',rate,'--start-time','0'],{encoding:'utf8',timeout:30000});
  assert.equal(native.status,0,native.stderr+native.stdout);
  const expected=JSON.parse(native.stdout),actual=JSON.parse(wasm.ccall('atlas_evaluate_time','string',['string','string','string','string','number'],['test-tensor-square','',initial,rate,0]));
  assert.equal(actual.ok,true);
  for(const result of [actual,expected])result.values.forEach((x,i)=>assert.ok(Math.abs(x-squareReference(v)[i])<1e-12*Math.max(1,Math.abs(x)),`Cartesian tensor square component ${i}`));
}
console.log(`Generated tensor square: Cartesian native/Wasm checks passed for ${tensorCases.length} tensors.`);

// Parent-increment reset contract: synthetic legacy fixtures share the private
// module so these checks run in the same CI native/Wasm gate as temporal cases.
const {readFileSync}=await import('node:fs');
const resetCases=JSON.parse(readFileSync(resolve(root,'tests/fixtures/parent-reset-cases.json'),'utf8')).cases;
const resetCatalogue=JSON.parse(wasm.ccall('atlas_describe','string',[],[]));
for(const id of new Set(resetCases.map(c=>c.model))){
  const source=JSON.parse(readFileSync(resolve(root,'tests/fixtures/time',id.replace(/^test-/,'')+'.json'),'utf8'));
  assert.deepEqual(resetCatalogue.models.find(m=>m.id===id),source,'Wasm reset fixture is stale: '+id);
}
function resetStep(id,initial,increment,parameters=null){
  const args=[id,parameters?.join(',')??'',initial.join(','),increment.join(',')];
  const actual=JSON.parse(wasm.ccall('atlas_integrate','string',Array(4).fill('string'),args));
  const command=['--mode','integrate','--model',id,'--initial',args[2],'--strain',args[3]];
  if(parameters)command.push('--parameters',args[1]);
  const native=spawnSync(resolve(root,'build/atlas_time_solver'),command,{encoding:'utf8',timeout:30000});
  assert.equal(native.status,actual.ok?0:1,native.stderr);
  const reference=JSON.parse(native.stdout);assert.equal(actual.ok,reference.ok);assert.equal(actual.message,reference.message);
  actual.state.forEach((x,i)=>assert.ok(Math.abs(x-reference.state[i])<1e-8*Math.max(1,Math.abs(reference.state[i]))));
  return actual;
}
for(const test of resetCases){
  const actual=resetStep(test.model,test.initial,test.increment,test.parameters);
  assert.equal(actual.ok,test.ok,test.name);assert.equal(actual.state.length,test.expected.length);
  actual.state.forEach((x,i)=>assert.ok(Math.abs(x-test.expected[i])<=(test.tolerance??1e-10),`${test.name} component ${i}`));
  for(const key of ['substeps','rejected'])assert.ok(actual.diagnostics[key]>=(test[`minimum_${key}`]??0),test.name);
  if(!actual.ok)assert.deepEqual(actual.state,test.initial);
}
let resetState=[100,100,100,0,0,0,1,0];
for(const [increment,coordinate,anchor] of [[-.5,.5,1],[-1,-.5,1],[.25,-.25,-.5],[.5,.25,-.5],[-.1,.15,.25],[0,.15,.25]]){
  const result=resetStep('test-parent-reset',resetState,[increment,0,0,0,0,0]);assert.equal(result.ok,true);
  assert.ok(Math.abs(result.state[6]-coordinate)<1e-12);assert.ok(Math.abs(result.state[7]-anchor)<1e-12);resetState=result.state;
}
const resetInitial=[100,100,100,0,0,0,1,0],resetDe=[-.5,0,0,0,0,0];
const resetFirst=resetStep('test-parent-reset',resetInitial,resetDe);
resetStep('test-parent-reset',resetInitial,[.7,0,0,0,0,0]);
assert.deepEqual(resetStep('test-parent-reset',resetInitial,resetDe),resetFirst);
// A caller split deliberately re-runs the parent guard at its new boundary.
const boundaryFirst=resetStep('test-parent-boundary-cutback',resetInitial,resetDe);
const boundarySecond=resetStep('test-parent-boundary-cutback',boundaryFirst.state,resetDe);
assert.equal(boundaryFirst.state[7],0);assert.equal(boundarySecond.state[7],boundaryFirst.state[6]);
const outer=JSON.parse(wasm.ccall('atlas_run','string',['string','string','string','number','number','number','number'],['test-parent-reset','','',1,-.01,1,0]));
assert.equal(outer.ok,true);assert.ok(Math.abs(outer.points.at(-1).state[6]-.99)<1e-10);assert.equal(outer.points.at(-1).state[7],1);
console.log(`Parent resets: ${resetCases.length} analytical cases, six reversal steps, repeated trials, parent boundaries and mixed-control native/Wasm checks passed.`);
