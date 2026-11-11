// Small independent Hooke-law reference, real transport and refusal checks.
// This is a smoke gate; independent studies are separate.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const options = {};
for (let i=2;i<process.argv.length;i+=2) {
  assert.ok(['--native','--wasm'].includes(process.argv[i]) && process.argv[i+1]);
  assert.ok(!options[process.argv[i]]);
  options[process.argv[i]]=resolve(process.argv[i+1]);
}
assert.ok(options['--wasm'], '--wasm is required');
const engine=await (await import(pathToFileURL(options['--wasm']))).default();
const initial=[100000,100000,100000,0,0,0,.7];
const strain=[.001,-.0003,.0002,.0004,-.0002,.0001];
const csv=x=>x.join(',');
function request(model, increment) {
  const actual=JSON.parse(engine.ccall('atlas_integrate','string',
    ['string','string','string','string'],[model,'',csv(initial),csv(increment)]));
  if (options['--native']) {
    const native=spawnSync(options['--native'],['--mode','integrate','--model',model,
      '--initial',csv(initial),'--strain',csv(increment)],{encoding:'utf8',timeout:15000});
    assert.ifError(native.error);
    const expected=JSON.parse(native.stdout);
    assert.equal(native.status,expected.ok?0:1,native.stderr);
    assert.equal(actual.ok,expected.ok);
    if (actual.ok) actual.state.forEach((v,i)=>close(v,expected.state[i]));
  }
  return actual;
}
function close(actual,expected) {
  assert.ok(Number.isFinite(actual) && Math.abs(actual-expected)<=1e-7*Math.max(1,Math.abs(expected)),
    `${actual} != ${expected}`);
}
for (const de of [strain,[0,0,0,0,0,0]]) {
  const result=request('linear-elastic',de);
  assert.equal(result.ok,true,result.message);
  assert.equal(result.state.length,7);
  const trace=de.slice(0,3).reduce((a,b)=>a+b,0), K=20e6, G=12e6;
  for (let i=0;i<6;i++) close(result.state[i],initial[i]+(i<3?K*trace:0)+2*G*(de[i]-(i<3?trace/3:0)));
  close(result.state[6],1.7*Math.exp(-trace)-1);
}
assert.equal(request('missing-ci-model',strain).ok,false,'Unknown models must be refused');
assert.equal(request('linear-elastic',strain.slice(1)).ok,false,'Malformed strain must be refused');
console.log('PASS: two independent elastic references and two transport refusals'+(options['--native']?'; native/Wasm agreement.':'.'));
