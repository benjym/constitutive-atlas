// Worker dispatch retains old effective imports and never falls back for scope.
import {runScopedLaboratory,validateScopedLaboratory} from './laboratory-scope.mjs';
import {runLaboratory} from './numerics.mjs';
import {createLaboratoryDocument} from './laboratory-document.mjs';
export function runLaboratoryRequest(engine,s,catalogue){
 if(s?.response_contract!==undefined)return runScopedLaboratory(engine,s,catalogue);
 if(Object.hasOwn(s,'stress_scope'))throw Error('Legacy laboratory request cannot declare stress scope.');
 validateScopedLaboratory({...s,response_contract:'stress-scope-0.1',stress_scope:'effective'},catalogue);
 const result=runLaboratory(engine,s,catalogue.sha256);
 createLaboratoryDocument(s,result,catalogue);
 return result;
}
