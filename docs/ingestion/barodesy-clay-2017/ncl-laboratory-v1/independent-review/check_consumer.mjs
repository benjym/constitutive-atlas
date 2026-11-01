// Saved-response/document consumer audit only. Never instantiate an engine.
import {readFile,writeFile,mkdtemp}from 'node:fs/promises';
import {resolve,dirname,join}from 'node:path';
import {fileURLToPath,pathToFileURL}from 'node:url';
import {webcrypto}from 'node:crypto';
import assert from 'node:assert/strict';
const here=dirname(fileURLToPath(import.meta.url)),packet=resolve(here,'..'),root=resolve(here,'../../../../..');
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const source=await read(join(packet,'source-manifest.json')),frozen=join(root,source.snapshot);
const {verifyScopedLaboratory}=await import(pathToFileURL(join(frozen,'web/laboratory-scope.mjs')));
const {createLaboratoryDocument,parseLaboratoryDocument,laboratoryDocumentCSV}=await import(pathToFileURL(join(frozen,'web/laboratory-document.mjs')));
const {bundle}=await import(pathToFileURL(join(frozen,'tools/build_laboratory_examples.mjs')));
const catalogue=await read(join(root,'.local/barodesy2017-ncl-lab-v1/artifacts/native/generated/models.json'));
const requests=await read(join(packet,'results/requests.json'));
let verified=0;
for(const backend of['native','wasm']){
 const rows=await read(join(packet,'results',backend+'.json'));
 assert.equal(rows.length,requests.length);
 for(let i=0;i<requests.length;i++){
  const s=requests[i].specification,r=rows[i].result;
  verifyScopedLaboratory(r,s,catalogue);verified++;
 }
}
const doc=await read(join(packet,'laboratory-document.json'));
assert.deepEqual(createLaboratoryDocument(doc.specification,doc.result,catalogue),doc);
assert.deepEqual(parseLaboratoryDocument(JSON.stringify(doc),catalogue),doc.specification);
const csv=laboratoryDocumentCSV(doc.specification,doc.result,catalogue),lines=csv.split('\n');
assert.equal(lines.length,102);assert.ok(lines[0].includes('effective_mean_stress_Pa'));
for(const line of lines.slice(1)){const values=line.split(',');assert.equal(values[5],'');assert.equal(values[6],'effective');assert.equal(values[7],'unavailable');}
const out=await mkdtemp('/private/tmp/barodesy-ncl-independent-example-');
const index=await bundle(frozen,out,catalogue);
assert.deepEqual(index,await read(join(packet,'packaged-index.json')));
assert.deepEqual(await read(join(out,'laboratory-examples', 'barodesy2017-london-ncl-isotropic-v1.json')),doc);
const mutations=[
 ['wrong catalogue',d=>d.catalogue_hash='0'.repeat(64)],
 ['wrong initial echo',d=>d.result.initial[6]=.8],
 ['missing saved point',d=>d.result.points.pop()],
 ['wrong control bits',d=>d.result.loading.controls_bits[1]='0000000000000000'],
 ['false pore availability',d=>d.result.pore_pressure.availability='reconstructed'],
];
for(const[name,mutate]of mutations){const broken=structuredClone(doc);mutate(broken);assert.throws(()=>parseLaboratoryDocument(JSON.stringify(broken),catalogue),undefined,name);}
const result={version:'barodesy2017-ncl-independent-consumer-review-v1',passed:true,saved_responses_checked:verified,ordinary_document_roundtrip:true,csv_data_rows:101,unavailable_pore_pressure_cells_blank:true,ordinary_example_builder_reproduced_exact_index:true,index_examples:index.examples.map(e=>e.id),rejected_mutations:mutations.map(x=>x[0]),compiled_calls:0,browser_or_live:false,root_registry_modified:false};
const destination=process.argv[2];assert.ok(destination,'output path required');await writeFile(destination,JSON.stringify(result,null,2)+'\n');
