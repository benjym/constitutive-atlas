// Named examples are inputs, not model defaults or specimen preparation.
import {parseLaboratoryDocument}from './laboratory-document.mjs';
const require=(ok,message)=>{if(!ok)throw Error(message);};
const hash=value=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
const id=value=>typeof value==='string'&&/^[a-z0-9][a-z0-9-]*$/.test(value);
const text=value=>typeof value==='string'&&value.trim().length>0;
const stable=v=>JSON.stringify(v&&typeof v==='object'?Array.isArray(v)?v.map(x=>JSON.parse(stable(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(stable(v[k]))])):v);
export function validateExampleIndex(index,catalogue){
 require(index?.schema_version==='0.1'&&index.catalogue_hash===catalogue?.sha256&&Array.isArray(index.examples),'Example catalogue mismatch.');
 const seen=new Set();
 for(const e of index.examples){
  require(e&&id(e.id)&&!seen.has(e.id)&&id(e.model)&&catalogue.models.some(m=>m.id===e.model),'Invalid or duplicate example identity.');seen.add(e.id);
  require(text(e.label)&&text(e.description)&&hash(e.definition_sha256)&&hash(e.document_sha256),'Example metadata or hashes missing.');
  require(e.document_url==='./laboratory-examples/'+e.id+'.json'&&e.definition_url==='./models/'+e.model+'.json','Unsafe example asset path.');
  let url;try{url=new URL(e.evidence_url);}catch{throw Error('Invalid example evidence link.');}require(url.protocol==='https:'&&url.hostname,'Invalid example evidence link.');
 }
 return index;
}
async function digest(text,crypto){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(n=>n.toString(16).padStart(2,'0')).join('');}
export async function prepareExample(entry,index,catalogue,{fetcher=fetch,crypto=globalThis.crypto}={}){
 validateExampleIndex(index,catalogue);require(index.examples.some(e=>stable(e)===stable(entry)),'Example is not in this index.');
 const get=async(url,expected)=>{const r=await fetcher(url);require(r.ok,'Example asset could not be loaded.');const body=await r.text();require(new TextEncoder().encode(body).length<=10*1024*1024,'Example exceeds the 10 MB limit.');require(await digest(body,crypto)===expected,'Example asset hash mismatch.');return body;};
 const definition=JSON.parse(await get(entry.definition_url,entry.definition_sha256));require(stable(definition)===stable(catalogue.models.find(m=>m.id===entry.model)),'Example definition differs from compiled model.');
 const document=await get(entry.document_url,entry.document_sha256),specification=parseLaboratoryDocument(document,catalogue);require(specification.model===entry.model,'Example document model mismatch.');
 const target=specification.protocol===3?specification.target/1000:specification.target*100,unit=specification.protocol===3?'kPa deviator stress':'% axial strain';
 const summary=entry.label+' · '+target+' '+unit+' · '+specification.steps+' increments · '+specification.cycles+' cycles. '+specification.initial.length+' initial-state components, '+specification.parameters.length+' parameters. Solver settings: '+JSON.stringify(specification.integration_settings)+'. '+entry.description+' Loading replaces parameters, the complete initial state, loading and solver settings. It starts a fresh replay; it does not continue a saved final state. Examples do not establish specimen preparation, calibration or scientific review.';
 return {specification:structuredClone(specification),summary,document};
}
