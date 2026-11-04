import {laboratoryStress} from './laboratory-scope.mjs';
// Storage semantics shared by laboratory fields and run import/export.
export function stateRole(field){
  if(field.semantics!==undefined){
    const role=field.semantics?.role;
    if(!['persistent','increment_unknown','plastic_multiplier'].includes(role))throw Error('Unsupported state role.');
    return role;
  }
  return field.multiplier?'plastic_multiplier':field.transient?'increment_unknown':'persistent';
}
export function persistentState(field){return stateRole(field)==='persistent';}
export function temporaryStateComponents(field){
  if(persistentState(field))throw Error('Persistent state requires explicit input.');
  const values=field.shape==='sym'?[...field.initial]:[field.initial];
  if(values.length!==(field.shape==='sym'?6:1)||values.some(x=>typeof x!=='number'||!Number.isFinite(x)))throw Error('Invalid temporary state example.');
  if(field.semantics&&values.some(x=>x!==0))throw Error('Temporary v0.3 state must start at zero.');
  return values;
}

// Consumer representation only: example inputs are not specimen preparation.
export function laboratoryExample(model){
  const stress=model.state?.[0];
  if(!stress||stress.name!=='sigma'||stress.shape!=='sym'||stress.unit!=='Pa'||!persistentState(stress))throw Error('The laboratory requires a first persistent Mandel stress field in Pa.');
  laboratoryStress(model);
  const state=model.state.flatMap(field=>{
    if(!persistentState(field))return temporaryStateComponents(field);
    if(field.shape==='sym'&&!Array.isArray(field.initial))throw Error('Model example requires complete finite persistent state.');
    const values=field.shape==='sym'?[...field.initial]:[field.initial];
    if(values.length!==(field.shape==='sym'?6:1)||values.some(x=>typeof x!=='number'||!Number.isFinite(x)))throw Error('Model example requires complete finite persistent state.');
    return values;
  });
  const sigma=state.slice(0,6),confinement=sigma[1]/1000,ratio=sigma[0]/sigma[1];
  if(sigma[1]!==sigma[2]||sigma.slice(3).some(x=>x!==0))throw Error('Model example is outside the axisymmetric laboratory; stress components cannot be discarded.');
  if(confinement<.001||confinement>1000000||!Number.isFinite(ratio)||ratio<.01||ratio>10)throw Error('Model example stress is outside the laboratory control ranges.');
  const parameters=Object.values(model.parameters).map(parameter=>{
    const value=parameter.default;
    if(typeof value!=='number'||!Number.isFinite(value)||value<parameter.min||value>parameter.max)throw Error('Model example requires finite parameter defaults within their declared ranges.');
    return value;
  });
  return {parameters,initial:state,confinement,stressRatio:ratio};
}
