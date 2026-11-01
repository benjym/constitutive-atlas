// Repackage an already qualified saved result. No new C ABI/ODE call.
import {readFileSync,writeFileSync}from 'node:fs';
import assert from 'node:assert/strict';
import {createLaboratoryDocument,parseLaboratoryDocument}from '../../../web/laboratory-document.mjs';
const read=p=>JSON.parse(readFileSync(p,'utf8'));
const catalogue=read(new URL('../gis2024-mixed-catalogue-v1/generated-eleven/models.json',import.meta.url)),rows=read(new URL('../gis2024-laboratory-route-v1/laboratory-requests.json',import.meta.url)),source=read('/private/tmp/atlas-gis2024-laboratory-route-v1-wasm/result.json');
const id='model-example-origin/p1/monotonic/exact',row=rows.find(r=>r.id===id),result=source.laboratory.find(r=>r.id===id).call.response;
const doc=createLaboratoryDocument(row.specification,result,catalogue);assert.deepEqual(parseLaboratoryDocument(JSON.stringify(doc),catalogue),row.specification);assert.equal(result.ok,true);assert.equal(result.points.length,9);assert.ok(result.points.every(p=>p.state.length===14));
writeFileSync(new URL('./example-proposal.json',import.meta.url),JSON.stringify(doc,null,2)+'\n');
console.log(JSON.stringify({saved_document_validation_pass:true,case_id:id,complete_state_components:14,parameters:row.specification.parameters.length,points:9,target:row.specification.target,steps:8,max_depth:row.specification.integration_settings.max_depth,compiled_calls:0,new_qualification:false,public_installation:false},null,2));
