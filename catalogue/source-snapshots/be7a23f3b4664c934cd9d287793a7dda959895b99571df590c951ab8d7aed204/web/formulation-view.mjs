/** Read-only catalogue view of the packaged definition; no inferred mechanics. */
import {stateRole} from './state-contract.mjs';
const declared=value=>value===undefined?'Not declared':typeof value==='string'?value.replaceAll('_',' '):JSON.stringify(value);
export function formulationSection(document,spec){
  const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const section=el('section');section.className='catalogue-formulation';
  section.append(el('h3','Definition, conventions & preparation'));
  if(!spec){section.append(el('p','No browser definition is packaged for this candidate. Consult its source and research evidence for formulation and preparation requirements.'));return section;}
  section.append(el('p','Definition status: '+declared(spec.status)+'. Browser availability does not establish scientific review or experimental validation. Consult retained evidence for review scope and decisions.'));
  if(spec.description)section.append(el('p',spec.description));
  const formulation=spec.formulation;
  if(!formulation){section.append(el('p','This legacy definition has no explicit formulation contract. Time, kinematics, stress scope and tensor/sign conventions are not inferred here.'));}
  else{
    const conventions=el('details');conventions.open=true;conventions.append(el('summary','Declared formulation'));
    const list=el('dl');
    const pairs=[['Equation form',formulation.equation_form],['Time dependence',formulation.time_dependence],['Kinematics',formulation.kinematics],['Frame',formulation.frame],['Objective rate',formulation.objective_rate],['Tensor representation',formulation.tensor_representation],['Stress sign',formulation.stress_sign],['Strain sign',formulation.strain_sign],['Stress measure',formulation.stress?.measure],['Stress scope',formulation.stress?.scope]];
    for(const [label,value] of pairs)list.append(el('dt',label),el('dd',declared(value)));
    conventions.append(list);
    const inputs=el('details');inputs.append(el('summary','Declared equation and advance inputs'),el('p',JSON.stringify(formulation.inputs??{})));conventions.append(inputs);section.append(conventions);
  }
  const parameters=el('details');parameters.append(el('summary','Parameter examples and declared ranges'));
  parameters.append(el('p','Values below are definition defaults. They do not establish a calibrated material or a source-matched experiment. Declared ranges do not replace the complete model domain constraints.'));
  const parameterList=el('ul');
  for(const [name,p] of Object.entries(spec.parameters??{})){
    parameterList.append(el('li',name+(p.label?' — '+p.label:'')+': '+declared(p.default)+' '+(p.unit??'unit not declared')+'; range '+declared(p.min)+' to '+declared(p.max)));
  }
  if(!parameterList.children.length)parameterList.append(el('li','No parameters declared.'));
  parameters.append(parameterList);section.append(parameters);
  const state=el('details');state.append(el('summary','Initial-state examples and storage roles'),el('p','Stored initial values are examples, not a specimen preparation history. Persistent fields carry material history; temporary solver unknowns are not preparation inputs.'));
  if(formulation?.tensor_representation==='mandel')state.append(el('p','Symmetric tensors use Mandel components: xx, yy, zz, √2 xy, √2 yz, √2 xz.'));
  const stateList=el('ul');
  for(const field of spec.state??[]){
    const role=stateRole(field);
    stateList.append(el('li',field.name+' ('+field.shape+', '+(field.unit??'unit not declared')+'): '+declared(field.initial)+'; '+(role==='persistent'?'persistent history':declared(role)+' — temporary solver field')));
  }
  if(!stateList.children.length)stateList.append(el('li','No state fields declared.'));
  state.append(stateList);section.append(state);
  return section;
}
