import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {formulationSection} from '../web/formulation-view.mjs';
class Element {constructor(tag){this.tag=tag;this.children=[];this.textContent='';} append(...children){this.children.push(...children);}}
const document={createElement:tag=>new Element(tag)};
const flatten=node=>[node,...node.children.flatMap(flatten)];
const text=node=>flatten(node).map(x=>x.textContent).join(' ');
const example=()=>({status:'draft',description:'Zero spin only.',formulation:{equation_form:'physical_time_rate',time_dependence:'physical_time',kinematics:'small_strain_3d',tensor_representation:'mandel',stress:{measure:'cauchy',scope:'effective'},inputs:{equation:{dt:{unit:'s'}}}},parameters:{rate:{default:1e-9,min:0,max:1,unit:'1/s'}},state:[{name:'sigma',shape:'sym',unit:'Pa',initial:[1,2,3,0,0,0],semantics:{role:'persistent'}},{name:'lambda',shape:'scalar',unit:'1',initial:0,semantics:{role:'plastic_multiplier'}}]});
test('physical time, stress scope and explicit tensor conventions remain distinguishable',()=>{
 const view=text(formulationSection(document,example()));
 assert.match(view,/physical time rate/);assert.match(view,/Time dependence physical time/);assert.match(view,/Stress scope effective/);assert.match(view,/√2 xy, √2 yz, √2 xz/);
 assert.match(view,/Objective rate Not declared/);assert.doesNotMatch(view,/Objective rate none/);
});
test('legacy definitions do not acquire inferred v0.3 mechanics',()=>{
 const spec=example();delete spec.formulation;spec.status='transcribed';const view=text(formulationSection(document,spec));
 assert.match(view,/legacy definition has no explicit formulation contract/);assert.match(view,/conventions are not inferred/);assert.doesNotMatch(view,/effective|Mandel|physical time|small strain/);
 assert.match(view,/Definition status: transcribed/);assert.match(view,/does not establish scientific review/);
});
test('default values and solver unknowns do not become experimental preparation',()=>{
 const view=text(formulationSection(document,example()));
 assert.match(view,/do not establish a calibrated material/);assert.match(view,/not a specimen preparation history/);
 assert.match(view,/rate: 1e-9 1\/s; range 0 to 1/);assert.match(view,/sigma .*persistent history/);assert.match(view,/lambda .*temporary solver field/);
});
test('unavailable candidate never inherits a runnable definition',()=>{
 const view=text(formulationSection(document,undefined));assert.match(view,/No browser definition is packaged/);assert.doesNotMatch(view,/Parameter examples|Initial-state examples/);
});
test('definition content is rendered as text and does not mutate canonical records',()=>{
 const spec=example();spec.description='<script>unexpected()</script>';spec.parameters.rate.label='<img src=x>';
 const before=JSON.stringify(spec);const section=formulationSection(document,spec);
 assert.equal(JSON.stringify(spec),before);assert.match(text(section),/<script>/);assert.equal(flatten(section).some(n=>['script','img'].includes(n.tag)),false);
});
test('all current root definitions render their actual status, parameters and state names',()=>{
 const folder=new URL('../models/',import.meta.url);let count=0;
 for(const name of readdirSync(folder).filter(name=>name.endsWith('.json'))){
  const spec=JSON.parse(readFileSync(new URL(name,folder),'utf8'));const view=text(formulationSection(document,spec));
  assert.ok(view.includes('Definition status: '+spec.status),spec.id);
  for(const name of Object.keys(spec.parameters))assert.ok(view.includes(name),spec.id+': '+name);
  for(const field of spec.state)assert.ok(view.includes(field.name),spec.id+': '+field.name);
  if(!spec.formulation)assert.match(view,/conventions are not inferred/);
  count++;
 }
 assert.ok(count>0);
});
