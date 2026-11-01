import fs from 'node:fs';
import {createHash}from'node:crypto';
import {parseLaboratoryDocument}from './source/web/laboratory-document.mjs';
const root='/Users/bmar5496/code/constitutive-atlas';
const doc=JSON.parse(fs.readFileSync(root+'/protocols/gis2024-small-drained-example.json','utf8'));
const catalogue=JSON.parse(fs.readFileSync('./engine/generated/models.json','utf8'));
const definition=JSON.parse(fs.readFileSync(root+'/models/'+doc.specification.model+'.json','utf8'));
const before=structuredClone(doc);let originalError=null;try{parseLaboratoryDocument(JSON.stringify(doc),catalogue);}catch(e){originalError=e.message;}
const originalHash=doc.catalogue_hash;doc.catalogue_hash=catalogue.sha256;
let reboundError=null;try{parseLaboratoryDocument(JSON.stringify(doc),catalogue);}catch(e){reboundError=e.message;}
const hash=x=>createHash('sha256').update(x).digest('hex');
const report={diagnostic_only:true,material_calls:0,model:doc.specification.model,old_catalogue_hash:originalHash,new_catalogue_hash:catalogue.sha256,original_error:originalError,in_memory_rebinding_error:reboundError,definition_semantically_identical:JSON.stringify(definition)===JSON.stringify(catalogue.models.find(m=>m.id===doc.specification.model)),source_document_sha256:hash(fs.readFileSync(root+'/protocols/gis2024-small-drained-example.json')),source_unchanged:JSON.stringify(before)===fs.readFileSync(root+'/protocols/gis2024-small-drained-example.json','utf8').trim(),interpretation:'Rebinding diagnostic only; no replacement document written and no public parser or packaging guard changed.'};
fs.writeFileSync('diagnostic.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
