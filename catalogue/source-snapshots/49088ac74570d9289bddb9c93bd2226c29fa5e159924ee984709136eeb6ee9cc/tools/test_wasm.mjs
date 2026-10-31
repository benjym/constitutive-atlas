// End-to-end native/Wasm parity: the exact same generated models and protocols.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const createAtlas=(await import(pathToFileURL(resolve(root,'build-wasm/atlas.js')))).default;
const wasm=await createAtlas();
const catalogue=JSON.parse(readFileSync(resolve(root,'build-wasm/generated/models.json'),'utf8'));
let runs=0;
for(const model of catalogue.models){
  for(const protocol of [0,1,2,3,4]){
    const target=protocol===3?10000:.002,steps=64,cycles=protocol===3?1:0;
    const native=spawnSync(resolve(root,'build/atlas_solver'),['--model',model.id,'--protocol',String(protocol),'--target',String(target),'--steps',String(steps),'--cycles',String(cycles)],{encoding:'utf8',timeout:30000});
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
  const native=spawnSync(resolve(root,'build/atlas_solver'),['--model',id,'--mode','integrate','--initial',initial,'--strain',strain],{encoding:'utf8',timeout:30000});
  const expected=JSON.parse(native.stdout);
  const actual=JSON.parse(wasm.ccall('atlas_integrate','string',['string','string','string','string'],[id,'',initial,strain]));
  assert.equal(actual.ok,expected.ok);
  assert.equal(actual.message,expected.message);
  assert.deepEqual(actual.diagnostics,expected.diagnostics);
  for (const key of ['iterations','substeps','rejected']) assert.ok(Number.isInteger(actual.diagnostics[key]) && actual.diagnostics[key]>=0);
  actual.state.forEach((v,i)=>assert.ok(Math.abs(v-expected.state[i])<=1e-7*Math.max(1,Math.abs(expected.state[i]))));
  if (!actual.ok) assert.deepEqual(actual.state,initial.split(',').map(Number));
}
console.log('Native/WebAssembly increment diagnostics and rollback parity passed for 4 cases.');
