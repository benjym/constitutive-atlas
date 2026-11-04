// Manufactured, constant-state transport fixtures only. No constitutive evaluation.
import assert from 'node:assert/strict';import fs from 'node:fs';import {dirname,join} from 'node:path';import {fileURLToPath} from 'node:url';
import {collect,parity,withoutElapsed,journalEngine,envelopeNegatives,historicalDifferences} from './collector-core.mjs';
import {laboratoryStress} from './context/web/laboratory-scope.mjs';import {normalizeLoading,controlFromBits} from './context/web/loading.mjs';
const H=dirname(fileURLToPath(import.meta.url)),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),freeze=read(join(H,'input-freeze.json')),rows=read(join(H,'requests.json')),catalogue=read(freeze.metadata.path),policy=read(join(H,'policy.json'));let checks=0;const ok=(v)=>{assert.ok(v);checks++;};
function fixture(s){
 const loading=normalizeLoading(s),m=catalogue.models.find(m=>m.id===s.model),r={ok:true,message:'',schema_version:'0.1',catalogue_hash:catalogue.sha256,model:s.model,elapsed_ms:1,parameters:structuredClone(s.parameters),initial:structuredClone(s.initial),integration_settings:structuredClone(s.integration_settings),protocol:s.protocol,api_version:'experimental-laboratory-scope-0.1',stress:laboratoryStress(m),pore_pressure:{quantity:'change',availability:'unavailable',reason:'not_reconstructed_for_protocol'},steps:s.steps};
 if(loading)r.loading={version:loading.version,encoding:loading.encoding,controls_bits:loading.controls_bits,controls:loading.controls_bits.map(controlFromBits)};else Object.assign(r,{target:s.target,cycles:s.cycles});
 r.points=Array.from({length:s.steps+1},(_,i)=>({control:loading?controlFromBits(loading.controls_bits[i]):s.target*i/s.steps,strain:[i?0.001:0,0,0,0,0,0],state:structuredClone(s.initial),p:100000,q:0,q_signed:0,u:null,iterations:0,substeps:0,rejected:0,error:0}));return r;
}
const fixtures=rows.map(r=>fixture(r.specification));
function engine(alter=()=>{}){let calls=0;return {ccall(name,type,types,args){if(name==='atlas_describe')return JSON.stringify(catalogue);const index=Math.floor(calls++/2);assert.equal(args[0],rows[index].specification.model);const r=structuredClone(fixtures[index]);alter(r,index,calls);return JSON.stringify(r);},count:()=>calls};}
const saved=[],journal=[],mock=engine(),report=collect(rows,catalogue,journalEngine(mock,x=>journal.push(x)),{saveDocument:(id,k,d)=>saved.push({id,k,d}),checkpoint:()=>{},readOld:r=>read(r.old_document.path)});
ok(report.status==='passed'&&report.rows.length===9&&mock.count()===18);ok(saved.length===54);ok(journal.length===72);ok(report.rows.every(r=>r.exact_replay&&r.negatives.length===5&&r.negatives.every(n=>n.rejected)));ok(report.rows.filter(r=>r.old_envelope).length===9);
const second=collect(rows,catalogue,engine(r=>r.elapsed_ms=9),{readOld:r=>read(r.old_document.path)});for(let i=0;i<9;i++){parity(report.rows[i].result,second.rows[i].result,policy);checks++;}
const doc=report.rows[0].document;ok(envelopeNegatives(doc,catalogue).length===5);
const bad=structuredClone(report.rows[0].result);bad.points[1].state[0]+=1;assert.throws(()=>parity(report.rows[0].result,bad,policy));checks++;
const diagnostic=structuredClone(report.rows[0].result);diagnostic.points[1].iterations++;assert.throws(()=>parity(report.rows[0].result,diagnostic,policy));checks++;
const near=structuredClone(report.rows[0].result);near.points[1].state[0]+=1e-6;parity(report.rows[0].result,near,policy);checks++;
let failedReport=null;assert.throws(()=>collect(rows,catalogue,engine((r,i,c)=>{if(c===2)r.points[1].state[0]+=1;}),{checkpoint:r=>failedReport=structuredClone(r)}));ok(failedReport.status==='failed'&&failedReport.rows[0].replay);
const errors=[];assert.throws(()=>journalEngine({ccall(){throw Error('manufactured transport exception');}},x=>errors.push(x)).ccall('test'));ok(errors.length===2&&errors[1].phase==='ccall-exception');
const a={elapsed_ms:1,nested:{value:3}},b={elapsed_ms:99,nested:{value:3}};assert.deepEqual(withoutElapsed(a),withoutElapsed(b));checks++;
console.log(JSON.stringify({status:'PASS_MANUFACTURED_ONLY',checks,requests:9,material_calls_mocked_per_backend:18,description_calls_mocked_per_backend:18,negative_envelopes_per_backend:45,generated_module_or_native_executed:false,raw_journal_rows:journal.length}));

assert.deepEqual(historicalDifferences({catalogue_hash:'new',elapsed_ms:2,a:[2]},{catalogue_hash:'old',elapsed_ms:1,a:[1]}),[{path:'result.a[0]',old:1,current:2,old_missing:false,current_missing:false,absolute_difference:1,relative_difference:.5}]);
