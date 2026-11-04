// Pure document boundary. Imports validate and return inputs for fresh replay.
import {parseRecordedJSON} from './recorded.mjs';
import {validateScopedLaboratory,verifyScopedLaboratory} from './laboratory-scope.mjs';
import {exportRun,importRunDocument,controlFromBits,normalizeLoading} from './loading.mjs';
const version='atlas-laboratory-export-0.2';
const require=(v,message)=>{if(!v)throw Error(message);};
function legacyContext(s,catalogue){
 require(!Object.hasOwn(s,'response_contract')&&!Object.hasOwn(s,'stress_scope'),'Legacy laboratory request cannot declare a new stress contract.');
 validateScopedLaboratory({...s,response_contract:'stress-scope-0.1',stress_scope:'effective'},catalogue);
}
function savedResult(result,s){
 // JSON numeric zero loses its sign. Only exact loading bits may restore it;
 // all numeric values must first equal their bit-decoded values (±0 compare
 // equal). This cannot turn a different numeric control into the requested one.
 const copy=structuredClone(result),loading=normalizeLoading(s);
 if(loading){
  const bits=loading.controls_bits,wire=copy?.loading;
  require(wire&&Array.isArray(wire.controls)&&Array.isArray(wire.controls_bits)&&wire.controls.length===bits.length&&wire.controls_bits.length===bits.length&&wire.controls_bits.every((b,i)=>b===bits[i]),'Saved exact-loading wire mismatch.');
  require(Array.isArray(copy.points)&&copy.points.length<=bits.length,'Invalid saved control prefix.');
  for(let i=0;i<bits.length;i++){
   const value=controlFromBits(bits[i]);require(typeof wire.controls[i]==='number'&&wire.controls[i]===value,'Saved numeric loading differs from exact bits.');wire.controls[i]=value;
   if(i<copy.points.length){require(typeof copy.points[i]?.control==='number'&&copy.points[i].control===value,'Saved point control differs from exact bits.');copy.points[i].control=value;}
  }
 }
 return copy;
}
export function createLaboratoryDocument(s,result,catalogue){
 if(s?.response_contract===undefined){legacyContext(s,catalogue);return exportRun(catalogue.sha256,s,result);}
 verifyScopedLaboratory(result,s,catalogue);
 return structuredClone({schema_version:version,catalogue_hash:catalogue.sha256,specification:s,result});
}
export function parseLaboratoryDocument(text,catalogue){
 const doc=parseRecordedJSON(text);
 require(doc&&typeof doc==='object'&&!Array.isArray(doc),'Laboratory document must be an object.');
 if(doc.schema_version!==version){
  const s=importRunDocument(doc,catalogue?.sha256);legacyContext(s,catalogue);
  // Legacy saved results retain their historical semantics and are recomputed,
  // exactly as in the old import helper; do not label them as scoped results.
  return s;
 }
 const keys=['schema_version','catalogue_hash','specification','result'];
 require(Object.keys(doc).length===keys.length&&keys.every(k=>Object.hasOwn(doc,k))&&doc.catalogue_hash===catalogue?.sha256,'Invalid scoped laboratory envelope or catalogue.');
 validateScopedLaboratory(doc.specification,catalogue);
 verifyScopedLaboratory(savedResult(doc.result,doc.specification),doc.specification,catalogue);
 return structuredClone(doc.specification);
}
export function laboratoryDocumentCSV(s,result,catalogue){
 if(s?.response_contract===undefined){
  legacyContext(s,catalogue);exportRun(catalogue.sha256,s,result);
  const header='axial_strain,radial_strain,volumetric_strain,p_Pa,q_signed_Pa,pore_pressure_Pa,iterations,substeps';
  return [header,...result.points.map(p=>[p.strain[0],p.strain[1],p.strain.slice(0,3).reduce((a,b)=>a+b,0),p.p,p.q_signed,p.u,p.iterations,p.substeps].join(','))].join('\n');
 }
 verifyScopedLaboratory(result,s,catalogue);
 const scope=s.stress_scope,availability=result.pore_pressure.availability;
 const header=['axial_strain_1','radial_strain_1','volumetric_strain_1',scope+'_mean_stress_Pa',scope+'_signed_deviatoric_stress_Pa','pore_pressure_change_Pa','stress_scope','pore_pressure_availability','iterations','substeps'];
 return [header.join(','),...result.points.map(p=>{
  const volume=p.strain.slice(0,3).reduce((a,b)=>a+b,0);require(Number.isFinite(volume),'Nonfinite laboratory CSV volumetric strain.');
  return [p.strain[0],p.strain[1],volume,p.p,p.q_signed,availability==='reconstructed'?p.u:'',scope,availability,p.iterations,p.substeps].join(',');
 })].join('\n');
}
