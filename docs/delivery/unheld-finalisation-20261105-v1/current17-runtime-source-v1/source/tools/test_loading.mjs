import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {controlBits,controlFromBits,cyclicWave,createLoading,normalizeLoading,verifyReturnedLoading,exportRun,importRunDocument} from '../web/loading.mjs';
import {runLaboratory,normalizeSettings} from '../web/numerics.mjs';
const read=n=>JSON.parse(readFileSync(new URL(n,import.meta.url),'utf8'));
let phaseCases=0,controls=0,ramps=0,negativeChecks=0,contracts=0;
for(const c of read('../catalogue/investigations/browser-loading-provenance-v1/reference/cyclic-bits.json')){
 const wave=cyclicWave(c.steps,c.cycles,c.index);assert.equal(controlBits(wave),c.wave_bits);phaseCases++;
 for(const p of c.controls){const target=controlFromBits(p.target_bits),value=target===0||wave===0?0:target*wave;assert.equal(controlBits(value),p.control_bits);controls++;}
}
for(const c of read('../catalogue/investigations/browser-loading-provenance-v1/reference/monotonic-bits.json')){
 const s={protocol:1,target:controlFromBits(c.target_bits),steps:c.steps,cycles:0};assert.equal(createLoading(s).controls_bits[c.index],c.control_bits);ramps++;
}
const base={model:'linear-elastic',parameters:[3e7,.25],initial:[100000,100000,100000,0,0,0],protocol:1,target:.002,steps:64,cycles:1,integration_settings:normalizeSettings()};
const spec={...base,loading:createLoading(base)};
const response=s=>({ok:true,model:s.model,parameters:[...s.parameters],initial:[...s.initial],catalogue_hash:'test',schema_version:'0.1',protocol:s.protocol,steps:s.steps,api_version:'experimental-laboratory-controls-0.1',integration_settings:normalizeSettings(),loading:{version:s.loading.version,encoding:s.loading.encoding,controls_bits:[...s.loading.controls_bits],controls:s.loading.controls_bits.map(controlFromBits)},points:s.loading.controls_bits.map(b=>({control:controlFromBits(b)}))});
verifyReturnedLoading(response(spec),spec,'test');contracts++;
const stopped=response(spec);stopped.ok=false;stopped.points=stopped.points.slice(0,3);verifyReturnedLoading(stopped,spec,'test');contracts++;
const zero=response(spec);zero.ok=false;zero.points=[];verifyReturnedLoading(zero,spec,'test');contracts++;
const reject=f=>{assert.throws(f);negativeChecks++;};
for(const mutate of [s=>s.loading.version='future',s=>s.loading.encoding='decimal',s=>s.loading.extra=1,s=>s.loading.producer.version='future',s=>s.loading.producer.algorithm='other',s=>s.loading.producer.target_bits=controlBits(.003),s=>s.loading.producer.steps=63,s=>s.loading.producer.cycles=2,s=>s.loading.producer.extra=1,s=>s.loading.controls_bits.pop(),s=>s.loading.controls_bits[1]=controlBits(.1),s=>s.loading.controls_bits[0]='8000000000000000',s=>s.loading.controls_bits=null,s=>s.loading.producer.target_bits='7ff0000000000000',s=>s.target='0.002',s=>s.steps=true,s=>s.cycles=1.5]){const s=structuredClone(spec);mutate(s);reject(()=>normalizeLoading(s));}
for(const mutate of [r=>delete r.catalogue_hash,r=>r.catalogue_hash='',r=>r.catalogue_hash='other',r=>delete r.schema_version,r=>r.schema_version='future',r=>r.api_version='future',r=>r.model='other',r=>r.initial[0]=0,r=>r.parameters[0]=0,r=>r.loading.controls_bits[1]='0000000000000000',r=>r.loading.controls[1]=0,r=>r.points[1].control=0,r=>r.points.pop(),r=>r.protocol=2,r=>r.steps=63,r=>r.target=.002,r=>r.cycles=1,r=>r.ok=1,r=>r.points=null,r=>r.loading.controls[1]=NaN,r=>r.loading.encoding='decimal',r=>r.loading.extra=1,r=>r.loading.controls_bits.pop()]){const r=response(spec);mutate(r);reject(()=>verifyReturnedLoading(r,spec,'test'));}
for(const args of [[0,1,0],[5001,1,0],[64,-1,0],[64,101,0],[64,1,-1],[64,1,65],[64,1,.5],[true,1,0]])reject(()=>cyclicWave(...args));
for(const target of [0,-0,Number.MIN_VALUE,-Number.MIN_VALUE,.002,-.002]){
 const s={...base,target,loading:createLoading({...base,target})};const doc=exportRun('test',s,response(s));const parsed=JSON.parse(JSON.stringify(doc));const imported=importRunDocument(parsed,'test');assert.deepEqual(imported.loading,s.loading);contracts++;
}
const old=exportRun('test',base,{ok:true,catalogue_hash:'test',model:base.model});assert.equal(old.schema_version,'0.1');assert.equal(importRunDocument(old,'test').loading,undefined);contracts++;
for(const mutate of [d=>d.schema_version='future',d=>d.catalogue_hash='other',d=>delete d.specification.loading,d=>d.specification.loading.controls_bits[1]=controlBits(.1),d=>d.result.model='other',d=>d.result.catalogue_hash='other',d=>d.result.api_version='future',d=>d.extra=1,d=>d.schema_version='0.1']){const d=exportRun('test',spec,response(spec));mutate(d);reject(()=>importRunDocument(d,'test'));}
const legacyNew=structuredClone(old);legacyNew.specification.loading=null;reject(()=>importRunDocument(legacyNew,'test'));
let called=[];
const engine={ccall:(name,type,types,args)=>{called.push(name);assert.equal(type,'string');if(name==='atlas_run_controls_with_settings'){assert.equal(types.length,6);assert.equal(args[4],spec.loading.controls_bits.join(','));return JSON.stringify(response(spec));}assert.equal(name,'atlas_run_with_settings');assert.equal(types.length,8);return JSON.stringify({ok:true,integration_settings:normalizeSettings()});}};
runLaboratory(engine,spec,'test');runLaboratory(engine,base);assert.deepEqual(called,['atlas_run_controls_with_settings','atlas_run_with_settings']);contracts++;
reject(()=>runLaboratory({ccall:()=>{throw Error('missing export');}},spec));
reject(()=>runLaboratory({ccall:()=>JSON.stringify({ok:true,integration_settings:normalizeSettings()})},spec));
const report={passed:true,phase_cases:phaseCases,exact_cyclic_controls:controls,exact_ramp_samples:ramps,negative_checks:negativeChecks,contract_cases:contracts,material_calls:0};
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
