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
