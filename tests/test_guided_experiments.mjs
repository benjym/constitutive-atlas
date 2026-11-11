import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {guidedPresets,parseGuidedRecipe,guidedSpecification,guidedLink,guideFromRun} from '../web/guided-experiments.mjs';

const catalogue={models:['modified-cam-clay','linear-elastic','hypoplastic-sand-vw96'].map(id=>JSON.parse(readFileSync(new URL('../models/'+id+'.json',import.meta.url))))};
test('Cam Clay varies just the initial preconsolidation pressure',()=>{
 const recipe=parseGuidedRecipe('#experiment?preset=clay',catalogue);
 const a=guidedSpecification(recipe,recipe.a),b=guidedSpecification(recipe,recipe.b);
 assert.deepEqual(a.initial.slice(0,8),[100000,100000,100000,0,0,0,.7,100000]);
 assert.deepEqual(b.initial.slice(0,8),[100000,100000,100000,0,0,0,.7,200000]);
 assert.deepEqual({...a,initial:b.initial},b);
});
test('preset and lab-generated links replay the same requests after reopening',()=>{
 for(const key of Object.keys(guidedPresets)){
  const recipe=parseGuidedRecipe('#experiment?preset='+key,catalogue);
  const before=[recipe.a,recipe.b].map(v=>guidedSpecification(recipe,v));
  const parsed=parseGuidedRecipe(guidedLink(recipe,recipe.compare,recipe.a,recipe.b),catalogue);
  assert.deepEqual([parsed.a,parsed.b].map(v=>guidedSpecification(parsed,v)),before);
  const fromLab=parseGuidedRecipe(guideFromRun(recipe.model,before[1],recipe.compare),catalogue);
  assert.deepEqual(guidedSpecification(fromLab,fromLab.a),before[1]);
  assert.deepEqual(guidedSpecification(fromLab,fromLab.b),before[1]);
 }
});
test('custom links vary only the selected field and reject ambiguous or invalid values',()=>{
 const base='#experiment?v=1&model=linear-elastic&protocol=3&steps=150&cycles=1&compare=target&a=10000&b=20000';
 const spec=guidedSpecification(parseGuidedRecipe(base+'&solver.max_iterations=60',catalogue),20000);
 assert.equal(spec.target,20000);assert.equal(spec.cycles,1);assert.equal(spec.integration_settings.max_iterations,60);
 for(const [suffix,message] of [['&a=3',/Duplicate/],['&target=3',/with a and b/],['&param.unknown=1',/Unknown/],['&solver.max_depth=99',/numerical setting/]]){
  assert.throws(()=>parseGuidedRecipe(base+suffix,catalogue),message);
 }
 const invalid=parseGuidedRecipe('#experiment?model=linear-elastic&compare=param.E&a=30000000&b=-1',catalogue);
 assert.throws(()=>guidedSpecification(invalid,invalid.b),/bounds/);
 const authored=guideFromRun(catalogue.models[1],spec,'target',{title:'Stress & cycles',prompt:'Which curve turns first?'});
 const restored=parseGuidedRecipe(authored,catalogue);
 assert.equal(restored.title,'Stress & cycles');assert.equal(restored.prompt,'Which curve turns first?');
});
