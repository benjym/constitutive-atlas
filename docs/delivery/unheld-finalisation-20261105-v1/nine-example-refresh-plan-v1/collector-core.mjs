// Pure boundary/observation logic. Engines and persistence are injected; no module initialization.
import assert from 'node:assert/strict';
import {runScopedLaboratory,verifyScopedLaboratory} from './context/web/laboratory-scope.mjs';
import {createLaboratoryDocument,parseLaboratoryDocument} from './context/web/laboratory-document.mjs';
export function historicalDifferences(a,b,path='result',out=[]){
 if(path.endsWith('.elapsed_ms')||path.endsWith('.catalogue_hash'))return out;
 if(a&&b&&typeof a==='object'&&typeof b==='object'&&Array.isArray(a)===Array.isArray(b)){
  const keys=new Set([...Object.keys(a),...Object.keys(b)]);
  for(const key of keys)historicalDifferences(a[key],b[key],Array.isArray(b)?path+'['+key+']':path+'.'+key,out);
 }else if(!Object.is(a,b)&&!(a===0&&b===0))out.push({path,old:b===undefined?null:b,current:a===undefined?null:a,old_missing:b===undefined,current_missing:a===undefined,...(typeof a==='number'&&typeof b==='number'?{absolute_difference:Math.abs(a-b),relative_difference:Math.abs(a-b)/Math.max(1,Math.abs(a),Math.abs(b))}:{})});
 return out;
}
function finite(value){if(typeof value==='number')assert.ok(Number.isFinite(value),'Nonfinite result channel');else if(value&&typeof value==='object')for(const v of Object.values(value))finite(v);}
const clone=structuredClone;
export function withoutElapsed(v){
 if(Array.isArray(v))return v.map(withoutElapsed);
 if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v).filter(([k])=>k!=='elapsed_ms').map(([k,x])=>[k,withoutElapsed(x)]));
 return v;
}
export function parity(a,b,policy,path='result',floating=false,stats={scalars:0,maximum_budget_fraction:0}){
 if(typeof b==='number'){
  assert.ok(typeof a==='number'&&Number.isFinite(a)&&Number.isFinite(b),path);
  if(!floating)assert.equal(a,b,path);
  else{const f=Math.abs(a-b)/(policy.parity_relative_tolerance*Math.max(1,Math.abs(a),Math.abs(b)));stats.scalars++;stats.maximum_budget_fraction=Math.max(stats.maximum_budget_fraction,f);assert.ok(f<=1,path+': budget fraction '+f);}
 }else if(Array.isArray(b)){assert.ok(Array.isArray(a),path);assert.equal(a.length,b.length,path);b.forEach((v,i)=>parity(a[i],v,policy,path+'['+i+']',floating,stats));}
 else if(b&&typeof b==='object'){
  assert.ok(a&&typeof a==='object'&&!Array.isArray(a),path);assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort(),path);
  for(const k of Object.keys(b))if(k!=='elapsed_ms')parity(a[k],b[k],policy,path+'.'+k,/\.points\[\d+\]$/.test(path)?policy.physical_point_fields.includes(k):floating,stats);
 }else assert.equal(a,b,path);
 return stats;
}
export function envelopeNegatives(doc,catalogue){
 const changes={
  'stale-catalogue':d=>{d.catalogue_hash='0'.repeat(64);},
  model:d=>{d.specification.model='not-a-model';},
  settings:d=>{d.result.integration_settings.max_depth=d.specification.integration_settings.max_depth===0?1:0;},
  loading:d=>{if(d.result.loading)d.result.loading.controls_bits[1]='0'.repeat(16);else d.result.target=d.specification.target+1;},
  state:d=>{d.result.initial[0]=d.specification.initial[0]+1;}
 };
 return Object.entries(changes).map(([id,mutate])=>{const bad=clone(doc);mutate(bad);let error=null;try{parseLaboratoryDocument(JSON.stringify(bad),catalogue);}catch(e){error=String(e);}assert.ok(error,'Negative envelope unexpectedly accepted: '+id);return {id,rejected:true,error,document:bad};});
}
export function journalEngine(engine,emit){let sequence=0;return {ccall(...args){
 const id=sequence++,start=performance.now();emit({phase:'ccall-before',id,arguments:args,started_epoch_ms:Date.now()});
 try{const raw=engine.ccall(...args);emit({phase:'ccall-returned',id,raw,elapsed_ms:performance.now()-start});return raw;}
 catch(e){emit({phase:'ccall-exception',id,error:{name:e.name,message:e.message,stack:e.stack},elapsed_ms:performance.now()-start});throw e;}
 }};}
export function collect(rows,catalogue,engine,{saveDocument=()=>{},checkpoint=()=>{},readOld=()=>null}={}){
 const report={identity:'baseline-nine-named-backend-observation-v1',status:'running',catalogue_hash:catalogue.sha256,rows:[]};checkpoint(report);
 try{
  for(const row of rows){
   const s=clone(row.specification),entry={id:row.id,specification:s};report.rows.push(entry);checkpoint(report);
   const result=runScopedLaboratory(engine,s,catalogue);entry.result=result;checkpoint(report);
   assert.equal(result.ok,true,result.message);finite(result);assert.equal(result.points.length,s.steps+1);verifyScopedLaboratory(result,s,catalogue);
   const document=createLaboratoryDocument(s,result,catalogue);saveDocument(row.id,'current',document);entry.document=document;
   const imported=parseLaboratoryDocument(JSON.stringify(document),catalogue);assert.deepEqual(imported,s);entry.imported=imported;
   entry.negatives=envelopeNegatives(document,catalogue);for(const n of entry.negatives)saveDocument(row.id,'negative-'+n.id,n.document);checkpoint(report);
   // Invalid envelopes are pure boundary checks; no engine is passed to parser.
   entry.replay=runScopedLaboratory(engine,imported,catalogue);checkpoint(report);assert.deepEqual(withoutElapsed(entry.replay),withoutElapsed(result));entry.exact_replay=true;
   if(row.old_document){
    const old=readOld(row);assert.deepEqual(old.specification,s);entry.historical_result_differences=historicalDifferences(result,old.result);entry.historical_comparison_gate='diagnostic-only-no-budget';const observation={original_sha256:row.old_document.sha256,original_catalogue_hash:old.catalogue_hash,current_catalogue_hash:catalogue.sha256};
    let inputs=null,error=null;try{inputs=parseLaboratoryDocument(JSON.stringify(old),catalogue);}catch(e){error=String(e);}
    if(old.catalogue_hash!==catalogue.sha256){assert.ok(error,'Stale old envelope accepted');observation.status='rejected-stale-catalogue';observation.error=error;}
    else{assert.equal(error,null);assert.deepEqual(inputs,s);observation.status='accepted-same-catalogue';}
    entry.old_envelope=observation;
   }
   entry.passed=true;checkpoint(report);
  }
  assert.equal(report.rows.length,9);report.status='passed';checkpoint(report);return report;
 }catch(e){report.status='failed';report.error={name:e.name,message:e.message,stack:e.stack};checkpoint(report);throw e;}
}
