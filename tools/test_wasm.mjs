// End-to-end native/Wasm parity: the exact same generated models and protocols.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const options={};for(let i=2;i<process.argv.length;i+=2){assert.ok(['--wasm-dir','--native'].includes(process.argv[i]));assert.ok(process.argv[i+1]);assert.ok(!options[process.argv[i]]);options[process.argv[i]]=process.argv[i+1];}
const wasmDir=resolve(options['--wasm-dir']||resolve(root,'build-wasm'));
const nativeSolver=resolve(options['--native']||resolve(root,'build/atlas_solver'));
const createAtlas=(await import(pathToFileURL(resolve(wasmDir,'atlas.js')))).default;
const wasm=await createAtlas();
const catalogue=JSON.parse(readFileSync(resolve(wasmDir,'generated/models.json'),'utf8'));
let runs=0;
for(const model of catalogue.models){
  for(const protocol of [0,1,2,3,4]){
    const target=protocol===3?10000:.002,steps=64,cycles=protocol===3?1:0;
    const native=spawnSync(nativeSolver,['--model',model.id,'--protocol',String(protocol),'--target',String(target),'--steps',String(steps),'--cycles',String(cycles)],{encoding:'utf8',timeout:30000});
    assert.equal(native.status,0,model.id+': '+native.stdout+native.stderr);
    const expected=JSON.parse(native.stdout);
    const actual=JSON.parse(wasm.ccall('atlas_run','string',['string','string','string','number','number','number','number'],[model.id,'','',protocol,target,steps,cycles]));
    assert.equal(actual.ok,true,model.id+': '+actual.message);assert.equal(actual.catalogue_hash,expected.catalogue_hash);assert.equal(actual.points.length,expected.points.length);
    for(let i=0;i<actual.points.length;i++)for(const key of ['state','strain'])actual.points[i][key].forEach((v,j)=>{
      const wanted=expected.points[i][key][j];assert.ok(Math.abs(v-wanted)<=1e-7*Math.max(1,Math.abs(wanted)),`${model.id} protocol ${protocol} step ${i} ${key}[${j}]: ${v} != ${wanted}`);
    });
    runs++;
  }
}
console.log(`Native/WebAssembly parity passed for ${runs} model/protocol combinations.`);

// Increment diagnostics are public in native and Wasm, including failed transactions.
for (const [id,initial,strain] of [
  ['drucker-prager','100000,100000,100000,0,0,0,.7,0','.01,-.005,-.005,0,0,0'],
  ['modified-cam-clay','100000,100000,100000,0,0,0,.7,200000,0','.01,.01,.01,0,0,0'],
  ['drucker-prager','100000,100000,100000,0,0,0,.7,0','-.002,-.002,-.002,.00001,0,0'],
  ['drucker-prager','400000,100000,100000,0,0,0,.7,0','.001,0,0,0,0,0'],
]) {
  const native=spawnSync(nativeSolver,['--model',id,'--mode','integrate','--initial',initial,'--strain',strain],{encoding:'utf8',timeout:30000});
  const expected=JSON.parse(native.stdout);
  const actual=JSON.parse(wasm.ccall('atlas_integrate','string',['string','string','string','string'],[id,'',initial,strain]));
  assert.equal(actual.ok,expected.ok);
  assert.equal(actual.message,expected.message);
  assert.deepEqual(actual.diagnostics,expected.diagnostics);
  for (const key of ['iterations','substeps','rejected']) assert.ok(Number.isInteger(actual.diagnostics[key]) && actual.diagnostics[key]>=0);
  assert.equal(actual.diagnostics.increment_fractions.length,actual.diagnostics.substeps);
  if (actual.ok) assert.equal(actual.diagnostics.increment_fractions.reduce((a,b)=>a+b,0),1);
  actual.state.forEach((v,i)=>assert.ok(Math.abs(v-expected.state[i])<=1e-7*Math.max(1,Math.abs(expected.state[i]))));
  if (!actual.ok) assert.deepEqual(actual.state,initial.split(',').map(Number));
}
console.log('Native/WebAssembly increment diagnostics and rollback parity passed for 4 cases.');

for (const current of ['100000,100000,100000,0,0,0,.7','150000,90000,60000,8000,-5000,3000,.7']) {
  const strain='.001,-.0003,.0002,.0004,-.0002,.0001',id='hypoplastic-sand-vw96';
  const native=spawnSync(nativeSolver,['--model',id,'--mode','evaluate','--current',current,'--initial',current,'--strain',strain],{encoding:'utf8',timeout:30000});
  assert.equal(native.status,0,native.stdout);
  const expected=JSON.parse(native.stdout);
  const actual=JSON.parse(wasm.ccall('atlas_evaluate','string',['string','string','string','string','string'],[id,'',current,current,strain]));
  assert.equal(actual.ok,true);
  actual.values.forEach((v,i)=>assert.ok(Math.abs(v-expected.values[i])<=1e-4+1e-9*Math.abs(expected.values[i])));
}
console.log('Native/WebAssembly Cartesian-rate parity passed for 2 hypoplastic states.');

// Independent analytical history targets for the missed IGS branch crossing
// and a five-segment reversal cycle (beta_r=1/2, R=1e-4).
const igs='hypoplastic-sand-igs97';
for (const [start,increments,analytical] of [
  [[100000,100000,100000,0,0,0,.7,0,0,0,-7.862141684009169e-6,0,0],
   [1e-5],[1.93701012831811e-6]],
  [[100000,100000,100000,0,0,0,.7,0,0,0,0,0,0],
   [2e-5,-4e-5,4e-5,-4e-5,2e-5],
   [1.4682934039814636e-5,-1.7855070763784847e-5,1.5987881160017447e-5,-1.7095642373659458e-5,2.588276509887993e-6]],
]) {
  let nativeState=start,wasmState=start;
  for (let j=0;j<increments.length;j++) {
    const strain=[0,0,0,increments[j],0,0].join(',');
    const native=spawnSync(nativeSolver,['--model',igs,'--mode','integrate','--initial',nativeState.join(','),'--strain',strain],{encoding:'utf8',timeout:30000});
    assert.equal(native.status,0,native.stdout+native.stderr);
    const expected=JSON.parse(native.stdout);
    const actual=JSON.parse(wasm.ccall('atlas_integrate','string',['string','string','string','string'],[igs,'',wasmState.join(','),strain]));
    assert.equal(actual.ok,true,actual.message);
    for (const result of [actual,expected]) {
      assert.ok(Math.abs(result.state[10]-analytical[j])<=1e-9+2e-5*Math.abs(analytical[j]),`IGS analytical history segment ${j}`);
      assert.equal(result.diagnostics.increment_fractions.reduce((a,b)=>a+b,0),1);
      assert.equal(result.diagnostics.increment_fractions.length,result.diagnostics.substeps);
    }
    actual.state.forEach((v,i)=>assert.ok(Math.abs(v-expected.state[i])<=(i<6?1e-4:1e-12)+1e-9*Math.abs(expected.state[i]),`IGS native/Wasm segment ${j} state ${i}`));
    nativeState=expected.state;wasmState=actual.state;
  }
}
console.log('Native/WebAssembly IGS analytical crossing and cyclic history passed for 6 increments.');
