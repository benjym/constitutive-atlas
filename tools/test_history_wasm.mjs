// Compare the real C ABI with the Python reference matrix; arithmetic fixtures only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const args=process.argv.slice(2);
function option(name, fallback) { const i=args.indexOf(name); return i<0?fallback:args[i+1]; }
const wasm=path.resolve(option('--wasm','build-wasm/history-fixtures.js'));
const casesPath=option('--cases');
assert(casesPath, '--cases must point to a freshly generated Python reference matrix');
const cases=JSON.parse(fs.readFileSync(casesPath,'utf8'));
const create=(await import(pathToFileURL(wasm))).default;
const module=await create({wasmBinary:fs.readFileSync(wasm.replace(/\.js$/,'.wasm'))});
const descriptor=JSON.parse(module.ccall('atlas_history_describe','string',[],[]));
const invoke=wire=>JSON.parse(module.ccall('atlas_history_advance','string',Array(6).fill('string'),wire));
for (const c of cases) {
  const program=descriptor.find(p=>p.id===c.wire[0]);
  assert(program, c.label); assert.equal(program.program_sha256,c.wire[1]);
  const actual=invoke(c.wire);
  assert.equal(typeof actual.message,'string'); delete actual.message;
  const values=actual.values; delete actual.values;
  const expected={...c.expected}; delete expected.values;
  assert.deepEqual(actual,expected,c.label);
  assert.equal(values.length,c.expected.values.length,c.label);
  for (let i=0;i<values.length;i++) {
    const a=values[i], b=c.expected.values[i];
    assert(Number.isFinite(a) && Math.abs(a-b)<=Math.max(1e-300,2e-14*Math.max(Math.abs(a),Math.abs(b))),`${c.label} component ${i}: ${a} vs ${b}`);
  }
  if (!actual.ok) {
    assert.deepEqual(values,c.wire[2].split(',').map(Number),c.label);
    assert.deepEqual(actual.events,[]); assert.equal(actual.generation,Number(c.wire[4]));
    assert.equal(actual.preparation_epoch,Number(c.wire[5]));
  }
  assert.deepEqual(invoke(c.wire),invoke(c.wire),`repeat ${c.label}`);
}
for (const [slot,value] of [[0,'unknown'],[1,'0'.repeat(64)],[2,'nan'],[3,'inf'],[4,'01'],[4,'9007199254740992'],[5,'true']]) {
  const wire=[...cases[0].wire];wire[slot]=value;
  assert.equal(invoke(wire).valid,false);
}
console.log(`${cases.length} phased history cases match Python through Wasm; malformed wires rejected.`);
