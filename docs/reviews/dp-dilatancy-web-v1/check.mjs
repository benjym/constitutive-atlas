// Frozen DP references reused without alteration; one persistent Wasm module.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const [root,wasmDir,output,replay]=process.argv.slice(2);
const base=join(root,'docs/reviews/dp-dilatancy-web-v1');
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const read=p=>JSON.parse(readFileSync(p));
const freeze=read(join(base,'prospective-freeze.json'));
for(const [p,h]of Object.entries(freeze.files))assert.equal(sha(join(root,p)),h,p);
const study=join(root,'catalogue/investigations/dp-dilatancy-domain-v1');
const deck=read(join(study,'cases.json')),native=read(join(study,'results/raw.json'));
let raw;
mkdirSync(output,{recursive:true});
if(replay)raw=read(replay);
else{
 const catalogue=read(join(wasmDir,'generated/models.json'));
 assert.equal(catalogue.sha256,native.catalogue_sha256);
 const engine=await(await import(pathToFileURL(join(wasmDir,'atlas.js')))).default();
 raw={artifacts:Object.fromEntries(['atlas.js','atlas.wasm','generated/models.json'].map(p=>[p,sha(join(wasmDir,p))])),catalogue_sha256:catalogue.sha256,calls:[]};
 for(const c of deck.cases){
  const args=Object.fromEntries(Array.from({length:c.arguments.length/2},(_,i)=>[c.arguments[i*2],c.arguments[i*2+1]]));
  const stdout=engine.ccall('atlas_integrate','string',['string','string','string','string'],[args['--model'],args['--parameters'],args['--initial'],args['--strain']]);
  raw.calls.push({id:c.id,stdout});writeFileSync(join(output,'raw.json'),JSON.stringify(raw,null,2)+'\n');
 }
}
assert.equal(raw.calls.length,deck.cases.length);
const t=deck.tolerances;
const rows=deck.cases.map((c,i)=>{
 const call=raw.calls[i];assert.equal(call.id,c.id);
 const r=JSON.parse(call.stdout),n=JSON.parse(native.calls[i].stdout);
 let passed=false,referenceRatio=null,parityRatio=null;
 if(c.expected_failure)passed=r.ok===false&&JSON.stringify(r.state)===JSON.stringify(c.initial)&&r.message===n.message;
 else if(r.ok===true&&r.state.length===c.expected.length&&r.state.every(Number.isFinite)){
  const ratios=against=>r.state.map((v,j)=>Math.abs(v-against[j])/((j<6?t.stress_absolute_Pa:t.other_state_absolute)+t.relative*Math.abs(against[j])));
  referenceRatio=Math.max(...ratios(c.expected));parityRatio=Math.max(...ratios(n.state));passed=referenceRatio<=1&&parityRatio<=1;
 }
 return{id:c.id,passed,reference_budget_fraction:referenceRatio,native_parity_budget_fraction:parityRatio,message:r.message};
});
const report={kind:'dp-dilatancy-web-v1',freeze_sha256:sha(join(base,'prospective-freeze.json')),artifacts:raw.artifacts,catalogue_sha256:raw.catalogue_sha256,count:rows.length,passed:rows.every(r=>r.passed),cases:rows,scope:'Wasm software/reference parity; sequential calls reuse one module. No experimental validation or scientific admission.'};
writeFileSync(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(`${rows.filter(r=>r.passed).length}/${rows.length} frozen Wasm cases pass`);
assert.equal(report.passed,true);
