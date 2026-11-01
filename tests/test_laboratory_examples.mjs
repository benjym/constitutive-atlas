import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,writeFile,mkdir,rm}from 'node:fs/promises';
import {tmpdir}from 'node:os';import {join}from 'node:path';import {createHash,webcrypto}from 'node:crypto';
import {validateExampleIndex,prepareExample}from '../web/laboratory-examples.mjs';
import {bundle}from '../tools/build_laboratory_examples.mjs';
const read=async p=>JSON.parse(await readFile(new URL(p,import.meta.url),'utf8'));
const catalogue=await read('../docs/reviews/gis2024-mixed-catalogue-v1/generated-eleven/models.json');
const modelText=await readFile(new URL('../docs/reviews/gis2024-v03-research-freeze-v1/model.json',import.meta.url),'utf8');
const docText=await readFile(new URL('../docs/reviews/explicit-laboratory-examples-v1/memory-example-fixture.json',import.meta.url),'utf8');
const sha=s=>createHash('sha256').update(s).digest('hex'),mid=JSON.parse(modelText).id;
function fixture(){
 const e={id:'memory-example',model:mid,label:'Small strain with complete memory',description:'Software example; source preparation and scientific review pending.',evidence_url:'https://github.com/benjym/constitutive-atlas/blob/main/docs/reviews/gis2024-laboratory-route-v1/README.md',definition_sha256:sha(modelText),document_sha256:sha(docText),document_url:'./laboratory-examples/memory-example.json',definition_url:'./models/'+mid+'.json'};
 const index={schema_version:'0.1',catalogue_hash:catalogue.sha256,examples:[e]},assets=new Map([[e.document_url,docText],[e.definition_url,modelText]]);return {e,index,assets};
}
async function prepare(f){return prepareExample(f.e,f.index,catalogue,{crypto:webcrypto,fetcher:async u=>({ok:f.assets.has(u),text:async()=>f.assets.get(u)})});}
test('complete nonzero14-state,19parameters,exact loading and settings survive preview without mutation',async()=>{
 const f=fixture(),original=JSON.stringify(f.index),r=await prepare(f),expected=JSON.parse(docText).specification;assert.deepEqual(r.specification,expected);assert.equal(r.specification.initial.length,14);assert.deepEqual(r.specification.initial.slice(7,13),[2e-5,-1e-5,-1e-5,0,0,0]);assert.equal(r.specification.initial[13],.25);assert.equal(r.specification.integration_settings.max_depth,20);assert.match(r.summary,/20/);assert.match(r.summary,/replaces/);assert.match(r.summary,/fresh replay/);assert.equal(JSON.stringify(f.index),original);r.specification.initial[13]=.9;assert.equal(JSON.parse(docText).specification.initial[13],.25);
});
test('empty registry preserves ordinary defaults and exposes no examples',()=>assert.deepEqual(validateExampleIndex({schema_version:'0.1',catalogue_hash:catalogue.sha256,examples:[]},catalogue).examples,[]));
test('stale catalogue, duplicate identity and unsafe asset paths reject',()=>{
 for(const change of[f=>f.index.catalogue_hash='a'.repeat(64),f=>f.index.examples.push({...f.e}),f=>f.e.document_url='../example.json',f=>f.e.evidence_url='javascript:alert(1)',f=>f.e.model='absent']){const f=fixture();change(f);assert.throws(()=>validateExampleIndex(f.index,catalogue));}
});
test('document and model raw-byte corruption reject',async()=>{
 for(const field of ['document_url','definition_url']){const f=fixture();f.assets.set(f.e[field],f.assets.get(f.e[field])+' ');await assert.rejects(prepare(f),/hash/);}
});
test('matching asset hash cannot conceal a changed compiled definition',async()=>{const f=fixture(),m=JSON.parse(modelText);m.description+=' changed';const text=JSON.stringify(m);f.assets.set(f.e.definition_url,text);f.e.definition_sha256=sha(text);await assert.rejects(prepare(f),/compiled model/);});
test('missing or corrupt memory, saved state and settings reject even with an updated file hash',async()=>{
 for(const poison of[d=>d.specification.initial.pop(),d=>d.result.points[0].state.pop(),d=>d.specification.integration_settings.max_depth=14,d=>d.result.points[1].control=.5]){const f=fixture(),doc=JSON.parse(docText);poison(doc);const text=JSON.stringify(doc);f.assets.set(f.e.document_url,text);f.e.document_sha256=sha(text);await assert.rejects(prepare(f));}
});
test('missing asset and unregistered example reject',async()=>{const f=fixture();f.assets.delete(f.e.document_url);await assert.rejects(prepare(f),/loaded/);const g=fixture();await assert.rejects(prepareExample({...g.e,label:'not registered'},g.index,catalogue),/not in this index/);});
test('packaging validates all inputs before writing and keeps safe relative URLs',async()=>{
 const root=await mkdtemp(join(tmpdir(),'atlas-examples-'));try{
  await mkdir(join(root,'catalogue'));await mkdir(join(root,'models'));await mkdir(join(root,'protocols'));const f=fixture(),entry={...f.e,document_path:'protocols/memory-example.json'};delete entry.document_url;delete entry.definition_url;
  await writeFile(join(root,'catalogue/laboratory-examples.json'),JSON.stringify({schema_version:'0.1',examples:[entry]}));await writeFile(join(root,'models',mid+'.json'),modelText);await writeFile(join(root,'protocols/memory-example.json'),docText);const output=join(root,'dist');const index=await bundle(root,output,catalogue);assert.equal(index.examples.length,1);assert.equal(await readFile(join(output,'laboratory-examples/memory-example.json'),'utf8'),docText);
  await writeFile(join(root,'protocols/memory-example.json'),docText+' ');await assert.rejects(bundle(root,join(root,'rejected'),catalogue),/hash/);await assert.rejects(readFile(join(root,'rejected/laboratory-examples.json')));
  entry.document_path='../outside.json';await writeFile(join(root,'catalogue/laboratory-examples.json'),JSON.stringify({schema_version:'0.1',examples:[entry]}));await assert.rejects(bundle(root,output,catalogue),/source path/);
 }finally{await rm(root,{recursive:true,force:true});}
});
