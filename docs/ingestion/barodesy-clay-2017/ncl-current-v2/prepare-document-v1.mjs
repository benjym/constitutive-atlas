// Pure saved-result document/normal consumer handoff; no compiled calls.
import {readFileSync,writeFileSync,mkdirSync,copyFileSync}from'node:fs';
import {resolve,join,dirname}from'node:path';
import {createHash}from'node:crypto';
import {pathToFileURL}from'node:url';
import assert from'node:assert/strict';
const root=resolve(process.argv[2]),packet=join(root,'docs/ingestion/barodesy-clay-2017/ncl-current-v2'),out=resolve(process.argv[3]);
const read=p=>JSON.parse(readFileSync(p,'utf8')),sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const freeze=read(join(packet,'document-plan-v1.json'));
for(const[p,h]of Object.entries(freeze.files))assert.equal(sha(resolve(root,p)),h,p);
mkdirSync(out,{recursive:false});
const catalogue=read(resolve(root,freeze.catalogue));
const s=read(join(packet,'results/requests.json')).find(r=>r.id==='ncl-isotropic').specification;
const result=read(join(packet,'results/wasm.json')).find(r=>r.id==='ncl-isotropic').result;
const {createLaboratoryDocument,parseLaboratoryDocument}=await import(pathToFileURL(join(root,'web/laboratory-document.mjs')));
const doc=createLaboratoryDocument(s,result,catalogue),text=JSON.stringify(doc,null,2)+'\n';
assert.deepEqual(parseLaboratoryDocument(text,catalogue),s);
const old=read(join(root,'docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1/laboratory-document.json'));
assert.deepEqual(doc.specification,old.specification);
assert.notEqual(doc.catalogue_hash,old.catalogue_hash);
writeFileSync(join(packet,'laboratory-document-v2.json'),text);
const entry=read(join(root,'docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1/proposed-example-entry.json'));
entry.document_path='protocols/barodesy2017-london-ncl-isotropic-fourteen-v2.json';
entry.document_sha256=sha(join(packet,'laboratory-document-v2.json'));
entry.evidence_url='https://github.com/benjym/constitutive-atlas/blob/main/docs/ingestion/barodesy-clay-2017/ncl-current-v2/README.md';
entry.description='Source Table2 London parameters and Eq11 analytical 100kPa initial-state assignment; project-chosen 1% isotropic normal compression in100increments. Original seven native/Wasm requests and independent NCL trajectory gates replayed on current14model runtime. Body2p/zero spin only. No measured preparation, experiment or live-release qualification.';
writeFileSync(join(packet,'proposed-example-entry-v2.json'),JSON.stringify(entry,null,2)+'\n');
const manifest=read(join(root,'catalogue/laboratory-examples.json'));
assert.ok(!manifest.examples.some(e=>e.id===entry.id));manifest.examples.push(entry);
writeFileSync(join(packet,'proposed-registry-v2.json'),JSON.stringify(manifest,null,2)+'\n');
for(const e of manifest.examples){
 for(const name of [e.document_path,'models/'+e.model+'.json']){
  const dst=join(out,'source',name);mkdirSync(dirname(dst),{recursive:true});
  if(name===entry.document_path)writeFileSync(dst,text);else copyFileSync(join(root,name),dst);
 }
}
mkdirSync(join(out,'source/catalogue'),{recursive:true});writeFileSync(join(out,'source/catalogue/laboratory-examples.json'),JSON.stringify(manifest,null,2)+'\n');
const {bundle}=await import(pathToFileURL(join(root,'tools/build_laboratory_examples.mjs')));
const index=await bundle(join(out,'source'),join(out,'package'),catalogue);
assert.equal(index.examples.length,4);
assert.deepEqual(index.examples.slice(0,3).map(e=>e.id),manifest.examples.slice(0,3).map(e=>e.id));
for(const[p,h]of Object.entries(freeze.files))assert.equal(sha(resolve(root,p)),h,p);
const outputs={};for(const name of ['laboratory-document-v2.json','proposed-example-entry-v2.json','proposed-registry-v2.json'])outputs[name]=sha(join(packet,name));
const report={passed:true,scope:'Pure saved-result serialization, exact original specification and normal four-example builder; no engine/browser/root install',catalogue_hash:catalogue.sha256,example_ids:index.examples.map(e=>e.id),outputs,index};
writeFileSync(join(packet,'document-consumer-v1.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,example_ids:report.example_ids,outputs},null,2));
