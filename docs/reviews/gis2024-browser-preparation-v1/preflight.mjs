// Consumer-only preflight. No Wasm loading, worker, C ABI or integration.
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {laboratoryExample} from '../../../web/state-contract.mjs';
import {validateScopedLaboratory} from '../../../web/laboratory-scope.mjs';
import {createLoading,normalizeLoading} from '../../../web/loading.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const model=read('../gis2024-v03-research-freeze-v1/model.json'),catalogue=read('../gis2024-mixed-catalogue-v1/generated-eleven/models.json');
assert.deepEqual(catalogue.models.find(m=>m.id===model.id),model);
const example=laboratoryExample(model);assert.equal(example.initial.length,14);assert.deepEqual(example.initial,model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]));
let complete=0,shapeRejected=0,deferred=0;
for(const row of read('./laboratory-cases.json').cases){
 const s=structuredClone(row.specification),original=structuredClone(s);
 if(row.loading_wire==='exact')s.loading=createLoading(s);
 validateScopedLaboratory(s,catalogue);normalizeLoading(s);assert.deepEqual(row.specification,original);complete++;
}
for(const row of read('./guard-cases.json')){
 if(row.rejection_layer==='consumer_shape'){assert.throws(()=>validateScopedLaboratory(row.specification,catalogue),/initial state/);shapeRejected++;}
 else {validateScopedLaboratory(row.specification,catalogue);deferred++;}
}
console.log(JSON.stringify({consumer_specifications_passed:complete,consumer_shape_rejections:shapeRejected,engine_or_geometry_checks_deferred:deferred,example_full14_pass:true,compiled_calls:0,scientific_admission:false},null,2));
