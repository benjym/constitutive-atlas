import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=path.resolve(process.argv[2]);
const {validateEvidenceIndex,evidenceSection}=await import(pathToFileURL(path.join(root,'web/catalogue.mjs')));
const rows=JSON.parse(fs.readFileSync(path.join(root,'docs/admission/baseline-hypoplastic-canonical-v1/evidence-export/agent-review-projection.json'),'utf8'));
class Element {constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];}append(...children){this.children.push(...children);}}
const document={createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
const flat=n=>[n,...n.children.flatMap(flat)];
const index=validateEvidenceIndex({schema_version:'0.1',kind:'catalogue-evidence-index',coverage_note:'Isolated source-renderer check only.',records:[],reviews:[],agent_reviews:rows});
const results=[];
for(const row of rows){
 const nodes=flat(evidenceSection(document,row.catalogue_id,index));
 const text=nodes.map(x=>x.textContent).join(' ');
 assert.ok(text.includes(row.scope));
 for(const limitation of row.limitations)assert.ok(text.includes(limitation));
 assert.ok(text.includes('Registered project approval for this exact definition and scope'));
 const links=nodes.filter(x=>x.tag==='a').map(x=>x.href);
 assert.deepEqual(links,['./evidence.json','./evidence-records/'+row.record_path,'./evidence-records/'+row.definition_record_path,'./evidence-records/catalogue/approved-models.json']);
 assert.ok(!/\/Users\/|\/private\/|file:\/\//.test(text+' '+links.join(' ')));
 results.push({model_id:row.catalogue_id,exact_scope:true,exact_limitations:row.limitations.length,links});
}
console.log(JSON.stringify({status:'PASS',qualification:'source renderer with minimal DOM fixture; no actual browser/package/live qualification',models:results}));
