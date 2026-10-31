import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,appendFileSync,existsSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const [native,wasmdir,oldnative,oldwasmdir,outfile]=process.argv.slice(2);
const fresh=await (await import(pathToFileURL(resolve(wasmdir,'atlas.js')))).default();
const prior=await (await import(pathToFileURL(resolve(oldwasmdir,'atlas.js')))).default();
assert.ok(!existsSync(outfile)&&!existsSync(outfile+'.jsonl'),'preserve prior evidence');
const record=x=>appendFileSync(outfile+'.jsonl',JSON.stringify(x)+'\n');
const legacyJournals=[];
const dir=mkdtempSync('/private/tmp/atlas-controls-check-');let count=0;const journals=[];
const bits=x=>{const b=Buffer.alloc(8);b.writeDoubleBE(x);return b.toString('hex');};
function cli(binary,args){const r=spawnSync(binary,args,{encoding:'utf8',timeout:30000});assert.equal(r.signal,null,r.stderr);assert.ok([0,1].includes(r.status),r.stderr);return JSON.parse(r.stdout);}
const initial=[100000,100000,100000,0,0,0,.7];
function call(backend,s,wire){
 const params=s.parameters||'',init=(s.initial||initial).join(','),protocol=s.protocol;
 let result;
 if(backend==='native'){const file=resolve(dir,`${count++}.csv`);writeFileSync(file,wire);result=cli(native,['--mode','run-controls','--model',s.model||'linear-elastic','--parameters',params,'--initial',init,'--protocol',String(protocol),'--laboratory-controls-file',file,'--integration-settings',s.settings||'']);}
 else result=JSON.parse(fresh.ccall('atlas_run_controls_with_settings','string',['string','string','string','number','string','string'],[s.model||'linear-elastic',params,init,protocol,wire,s.settings||'']));
 journals.push({backend,specification:s,wire,result});record({kind:'explicit',...journals.at(-1)});return result;
}
function legacy(backend,s,old=false){
 const args=[s.model,s.parameters||'',s.initial.join(','),s.protocol,s.target,s.steps,s.cycles];
 if(backend==='native')return cli(old?oldnative:native,['--model',args[0],'--parameters',args[1],'--initial',args[2],'--protocol',String(args[3]),'--target',String(args[4]),'--steps',String(args[5]),'--cycles',String(args[6]),'--integration-settings','']);
 return JSON.parse((old?prior:fresh).ccall('atlas_run_with_settings','string',['string','string','string','number','number','number','number','string'],[...args,'']));
}
function physical(r){const {elapsed_ms,...rest}=r;return rest;}
function close(a,b,budget,label){assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=budget,`${label}: ${a} vs ${b}, budget ${budget}`);}
let legacyRuns=0,explicitRegressions=0,analyticPoints=0,negativeCases=0;
const catalogue=JSON.parse(readFileSync(resolve(wasmdir,'generated/models.json'),'utf8'));
const expectedIds=['barodesy-clay-2017','barodesy-sand','drucker-prager','hypoplastic-clay-2005','hypoplastic-clay-2013','hypoplastic-sand-igs97','hypoplastic-sand-vw96','linear-elastic','modified-cam-clay'];
assert.deepEqual(catalogue.models.map(m=>m.id).sort(),expectedIds);
const priorCatalogue=JSON.parse(readFileSync(resolve(oldwasmdir,'generated/models.json'),'utf8'));assert.deepEqual(catalogue,priorCatalogue);
for(const model of catalogue.models){
 for(const protocol of [0,1,2,3,4]){
  const s={model:model.id,initial:model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol,target:protocol===3?10000:.002,steps:64,cycles:protocol===3?1:0};
  for(const backend of ['native','wasm']){
   const a=legacy(backend,s,true),b=legacy(backend,s);legacyJournals.push({backend,specification:s,prior:a,current:b});record({kind:'legacy',...legacyJournals.at(-1)});assert.equal(a.ok,true,a.message);assert.deepEqual(physical(b),physical(a));legacyRuns++;
   const controls=a.points.map(p=>p.control),wire=controls.map(bits).join(','),c=call(backend,s,wire);
   assert.equal(c.ok,true,c.message);assert.deepEqual(c.points,a.points);
   const {api_version,loading,...explicitEnvelope}=physical(c),{target,cycles,...legacyEnvelope}=physical(a);assert.deepEqual(explicitEnvelope,legacyEnvelope);assert.deepEqual(c.loading.controls.map(bits),controls.map(bits));assert.deepEqual(c.loading.controls_bits,controls.map(bits));
   assert.equal(c.api_version,'experimental-laboratory-controls-0.1');assert.equal(c.loading.version,'laboratory-controls-0.1');assert.equal(c.loading.encoding,'ieee754-binary64-hex');assert.ok(!('target'in c)&&!('cycles'in c));explicitRegressions++;
  }
 }
}
// Independent closed-form isotropic elasticity: G=12MPa, lambda=12MPa.
// Trial/commit void-ratio bookkeeping telescopes to e=1.7*exp(-tr(eps))-1.
for(const protocol of [0,1,2,3,4]){
 const controls=protocol===3?[0,10000,-5000,0]:[0,.001,-.0005,0];const wire=controls.map(bits).join(',');
 const results=['native','wasm'].map(backend=>call(backend,{protocol},wire));
 assert.deepEqual(results[0].loading,results[1].loading);
 for(let i=0;i<results[0].points.length;i++){const a=results[0].points[i],b=results[1].points[i];
  for(const key of ['state','strain'])a[key].forEach((x,j)=>close(x,b[key][j],1e-10*Math.max(1,Math.abs(x),Math.abs(b[key][j])),'analytic backend parity'));
  for(const key of ['control','p','q','q_signed','u'])close(a[key],b[key],1e-10*Math.max(1,Math.abs(a[key]),Math.abs(b[key])),'analytic backend parity');
 }
 for(const r of results){assert.equal(r.ok,true,r.message);assert.equal(r.points.length,controls.length);assert.deepEqual(r.loading.controls_bits,controls.map(bits));
  for(let i=0;i<controls.length;i++){
   assert.equal(r.points[i].strain.length,6);assert.equal(r.points[i].state.length,7);
   const c=controls[i],a=protocol===3?c/36000000:c;
   const lateral=protocol===1?-.25*a:protocol===2||protocol===3?-.5*a:protocol===4?a:0;
   const strain=[a,lateral,lateral,0,0,0],tr=a+2*lateral;
   const stress=strain.map((x,j)=>j<3?100000+12000000*tr+24000000*x:0);
   r.points[i].strain.forEach((x,j)=>close(x,strain[j],2e-10,'analytic strain'));
   r.points[i].state.slice(0,6).forEach((x,j)=>close(x,stress[j],.003,'analytic stress'));
   close(r.points[i].state[6],1.7*Math.exp(-tr)-1,2e-10,'analytic void ratio');
   close(r.points[i].u,protocol===2||protocol===3?100000-stress[1]:0,.003,'analytic u');analyticPoints++;
  }
 }
}
for(const backend of ['native','wasm']){
 const valid=call(backend,{protocol:0},[0,.001].map(bits).join(','));assert.equal(valid.ok,true);
 const negatives=['',bits(0),[1,2].map(bits).join(','),'0'.repeat(16)+',000000000000000g','0'.repeat(16)+',7FF0000000000000','0'.repeat(16)+',7ff0000000000000','0'.repeat(16)+',7ff8000000000000',[0,.10000000000000002].map(bits).join(','),[0,100000001].map(bits).join(','),Array(5002).fill(bits(0)).join(','),[bits(0),bits(.001),''].join(','),' '+[0,.001].map(bits).join(',')];
 for(let i=0;i<negatives.length;i++){const r=call(backend,{protocol:i===8?3:0},negatives[i]);assert.equal(r.ok,false,`invalid case ${i}`);assert.ok(!r.points||r.points.length===0);negativeCases++;}
 const badProtocol=call(backend,{protocol:5},[0,0].map(bits).join(','));assert.equal(badProtocol.ok,false);negativeCases++;
 const badSettings=call(backend,{protocol:0,settings:'-1,1e-6,45,14,20000,11'},[0,0].map(bits).join(','));assert.equal(badSettings.ok,false);negativeCases++;
 for(const specification of [{protocol:0,model:'unknown-model'},{protocol:0,initial:[100000,100000,100000,0,0,0,-1]}]){const r=call(backend,specification,[0,.001].map(bits).join(','));assert.equal(r.ok,false);assert.ok(!r.points||r.points.length===0);negativeCases++;}
 const maximum=call(backend,{protocol:0},Array(5001).fill(bits(0)).join(','));assert.equal(maximum.ok,true,maximum.message);assert.equal(maximum.points.length,5001);
 if(backend==='native'){const r=call(backend,{protocol:0},[0,.001].map(bits).join(',')+'\0suffix');assert.equal(r.ok,false);negativeCases++;}
 const boundary=call(backend,{protocol:0},[0,.1].map(bits).join(','));assert.equal(boundary.ok,true,boundary.message);
 const small=[-0,Number.MIN_VALUE,-Number.MIN_VALUE,0],smallRun=call(backend,{protocol:0},small.map(bits).join(','));assert.equal(smallRun.ok,true,smallRun.message);assert.deepEqual(smallRun.loading.controls_bits,small.map(bits));assert.deepEqual(smallRun.points.map(p=>bits(p.control)),small.map(bits));
 const fragile={protocol:4,initial:[100000,100000,100000,0,0,0,.01]};
 const failed=call(backend,fragile,[0,.001,.1].map(bits).join(','));assert.equal(failed.ok,false);assert.equal(failed.points.length,2);assert.match(failed.message,/step 2/);
 const recovered=call(backend,fragile,[0,.001].map(bits).join(','));assert.equal(recovered.ok,true);assert.deepEqual(failed.points,recovered.points);
 const again=call(backend,{protocol:0},[0,.001].map(bits).join(','));assert.deepEqual(physical(again),physical(valid));
}
assert.equal(legacyRuns,90);assert.equal(explicitRegressions,90);assert.equal(analyticPoints,40);
const report={passed:true,legacy_backend_runs:legacyRuns,explicit_legacy_equivalences:explicitRegressions,analytic_backend_points:analyticPoints,negative_cases:negativeCases,signed_zero_subnormal_backends:2,native_fresh_process_prefix_repeatability:true,wasm_same_instance_recovery:true,legacyJournals,journals};
writeFileSync(outfile,JSON.stringify(report)+'\n');console.log(JSON.stringify({...report,journals:undefined,legacyJournals:undefined}));
