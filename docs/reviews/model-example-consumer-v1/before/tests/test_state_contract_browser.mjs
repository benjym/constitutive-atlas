import test from 'node:test';
import assert from 'node:assert/strict';
import {persistentState,stateRole,temporaryStateComponents} from '../web/state-contract.mjs';

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
