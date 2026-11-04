import test from 'node:test';
import assert from 'node:assert/strict';
import {persistentState,stateRole,temporaryStateComponents,laboratoryExample} from '../web/state-contract.mjs';

test('legacy and explicit roles select the same editable persistent state',()=>{
  for(const [legacy,role]of [[{},'persistent'],[{transient:true},'increment_unknown'],[{transient:true,multiplier:true},'plastic_multiplier']]){
    assert.equal(stateRole(legacy),role);
    const current={semantics:{role}};
    assert.equal(persistentState(current),persistentState(legacy));
  }
  assert.equal(persistentState({semantics:{role:'persistent'},transient:true}),true);
  assert.throws(()=>persistentState({semantics:{role:'unknown'}}),/Unsupported state role/);
});
test('temporary state flattens complete tensor slots and preserves legacy examples',()=>{
  const field={shape:'sym',initial:[0,0,0,0,0,0],semantics:{role:'increment_unknown'}};
  const components=temporaryStateComponents(field);
  assert.deepEqual(components,[0,0,0,0,0,0]);components[0]=1;assert.equal(field.initial[0],0);
  assert.deepEqual(temporaryStateComponents({shape:'scalar',initial:0,semantics:{role:'plastic_multiplier'}}),[0]);
  assert.deepEqual(temporaryStateComponents({shape:'scalar',initial:2,transient:true}),[2]);
  assert.throws(()=>temporaryStateComponents({...field,initial:[1,0,0,0,0,0]}),/start at zero/);
  assert.throws(()=>temporaryStateComponents({...field,initial:[0,0]}),/Invalid temporary/);
  assert.throws(()=>temporaryStateComponents({shape:'scalar',initial:0}),/explicit input/);
});
test('a v0.3 plastic state supplies temporary slots without editable inputs',()=>{
  const fields=[{name:'sigma',shape:'sym',semantics:{role:'persistent'}},
    {name:'e',shape:'scalar',semantics:{role:'persistent'}},
    {name:'gamma',shape:'scalar',initial:0,semantics:{role:'plastic_multiplier'}}];
  assert.deepEqual(fields.filter(persistentState).map(f=>f.name),['sigma','e']);
  const inputs={sigma:[100000,100000,100000,0,0,0],e:[.8]};
  const state=fields.flatMap(f=>persistentState(f)?inputs[f.name]:temporaryStateComponents(f));
  assert.deepEqual(state,[100000,100000,100000,0,0,0,.8,0]);
});


import {readFileSync,readdirSync} from 'node:fs';
const readModel=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
test('shipped examples retain declared full state and parameter defaults',()=>{
  const paths=readdirSync(new URL('../models/',import.meta.url)).filter(path=>path.endsWith('.json'));
  assert.ok(paths.length>=7);
  for(const path of paths){
    const model=readModel('../models/'+path),example=laboratoryExample(model);
    assert.deepEqual(example.initial,model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]));
    assert.deepEqual(example.parameters,Object.values(model.parameters).map(p=>p.default));
    assert.equal(example.confinement,model.state[0].initial[1]/1000);assert.equal(example.stressRatio,model.state[0].initial[0]/model.state[0].initial[1]);
  }
});
test('a separately declared 10kPa example replaces the universal stress and copies tensor history',()=>{
  const model=readModel('../docs/ingestion/hypoplastic-clay-2013/preview-plan-v1/model.json');
  model.state.push({name:'history',shape:'sym',initial:[1,2,3,4,5,6],semantics:{role:'persistent'}});
  model.state.push({name:'gamma',shape:'scalar',initial:0,semantics:{role:'plastic_multiplier'}});
  const saved=structuredClone(model),example=laboratoryExample(model);
  assert.equal(example.confinement,10);assert.deepEqual(example.initial,[10000,10000,10000,0,0,0,.8,1,2,3,4,5,6,0]);
  assert.deepEqual(example.parameters,Object.values(model.parameters).map(p=>p.default));
  example.initial[0]=4;example.parameters[0]=8;assert.deepEqual(model,saved);
});
test('unsupported example stresses reject without projection or lost components',()=>{
  const base=readModel('../docs/ingestion/hypoplastic-clay-2013/preview-plan-v1/model.json');
  for(const stress of [[10000,10000,20000,0,0,0],[10000,10000,10000,1,0,0],[0,0,0,0,0,0],[1e10,1e10,1e10,0,0,0],[200000,10000,10000,0,0,0],[10000,10000,10000,0,0,NaN]]){
    const model=structuredClone(base);model.state[0].initial=stress;
    assert.throws(()=>laboratoryExample(model),/laboratory|finite/);
    assert.deepEqual(model.state[0].initial,stress);
  }
  const model=structuredClone(base);model.formulation.stress.scope='total';assert.throws(()=>laboratoryExample(model),/effective/);
});
test('invalid persistent fields and parameter defaults cannot become executable examples',()=>{
  const base=readModel('../docs/ingestion/hypoplastic-clay-2013/preview-plan-v1/model.json');
  for(const value of [NaN,Infinity,true,undefined]){
    const model=structuredClone(base);model.state[1].initial=value;assert.throws(()=>laboratoryExample(model),/finite/);
    const param=structuredClone(base);param.parameters.p_ref.default=value;assert.throws(()=>laboratoryExample(param),/finite/);
  }
  const model=structuredClone(base);model.state[0].initial=[10000,10000,10000];assert.throws(()=>laboratoryExample(model),/complete/);
});
