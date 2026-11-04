// Presentation derives stress meaning from canonical model metadata.
import {laboratoryStress,laboratoryPoreSeries} from './laboratory-scope.mjs';
import {comparisonAxes} from './experiments.mjs';
export function laboratoryPresentation(model){
 const scope=laboratoryStress(model).scope,total=scope==='total';
 const protocols=total?['One-dimensional strain','Fixed radial total stress','Zero volumetric strain','Signed q control · zero volumetric strain','Isotropic strain']:['Oedometer','Drained triaxial','Undrained triaxial','Undrained stress control','Isotropic compression'];
 const axes=Object.fromEntries(Object.entries(comparisonAxes).map(([k,v])=>[k,{...v}]));
 if(total){axes.path.xLabel='Mean total stress p (kPa)';axes.path.yLabel=axes.stress.yLabel='Total deviator stress q (kPa)';}
 return {scope,protocols,axes,radialLabel:'Radial '+scope+' stress (kPa)',pathTitle:(total?'Total':'Effective')+' stress path',pathAria:'Deviator stress versus '+scope+' mean stress',stressAria:(total?'Total':'Effective')+' deviator stress versus axial strain'};
}
const unavailable=reason=>reason==='total_stress_without_pore_pressure_law'?'Unavailable: total stress has no pore-pressure law.':'Unavailable for this mechanical protocol.';
export function laboratoryPoreView(result,model,protocol){
 const scope=laboratoryStress(model).scope;
 if(!result)return {points:[],caption:scope==='total'?unavailable('total_stress_without_pore_pressure_law'):'Waiting for a matching response.'};
 if(result.api_version==='experimental-laboratory-scope-0.1'){
  if(result.stress?.scope!==scope||result.protocol!==protocol)throw Error('Pore view scope/protocol mismatch.');
  const series=laboratoryPoreSeries(result);
  return {points:series.points,caption:series.reason?unavailable(series.reason):'Reconstructed change: fixed radial total stress; incompressible fluid and grains assumption.'};
 }
 if(scope!=='effective')throw Error('Legacy pore view requires effective stress.');
 if(![2,3].includes(protocol))return {points:[],caption:unavailable('not_reconstructed_for_protocol')};
 if(!Array.isArray(result.points)||result.points.some(p=>typeof p.u!=='number'||!Number.isFinite(p.u)||!Array.isArray(p.strain)||p.strain.length!==6||p.strain.some(x=>typeof x!=='number'||!Number.isFinite(x))))throw Error('Invalid legacy pore-pressure channel.');
 return {points:result.points.map(p=>[p.strain[0]*100,p.u/1000]),caption:'Reconstructed change: fixed radial total stress; incompressible fluid and grains assumption.'};
}
