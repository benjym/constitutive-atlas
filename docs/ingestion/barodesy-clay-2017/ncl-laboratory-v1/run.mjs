// Execute only the frozen requests; save responses before assessing them.
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const packet=dirname(fileURLToPath(import.meta.url)), [source,native,wasm,out]=process.argv.slice(2).map(p=>resolve(p));
assert.ok(source&&native&&wasm&&out);
const read=p=>JSON.parse(readFileSync(p,'utf8')),sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const policy=read(join(packet,'policy.json')),manifest=read(join(packet,'source-manifest.json'));
for(const [name,expected] of Object.entries(manifest.files))assert.equal(sha(join(source,name)),expected,name);
const catalogue=read(join(dirname(native),'generated/models.json')),model=catalogue.models.find(m=>m.id==='barodesy-clay-2017');
assert.equal(sha(join(source,'models/barodesy-clay-2017.json')),policy.model_sha256);
assert.deepEqual(read(join(wasm,'generated/models.json')),catalogue);
const {createLoading}=await import(pathToFileURL(join(source,'web/loading.mjs')));
const {settingsCsv}=await import(pathToFileURL(join(source,'web/numerics.mjs')));
const {verifyScopedLaboratory}=await import(pathToFileURL(join(source,'web/laboratory-scope.mjs')));
const parameters=Object.values(model.parameters).map(p=>p.default),initial=[1e5,1e5,1e5,0,0,0,1.3831693930553504];
const requests=policy.cases.map(c=>{const s={response_contract:'stress-scope-0.1',stress_scope:'effective',model:model.id,parameters,initial:c.initial==='unchanged-model-default'?model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]):c.initial==='zero-stress-invalid'?[0,0,0,0,0,0,initial[6]]:initial,protocol:c.protocol,target:c.target,steps:c.steps,cycles:0,integration_settings:{...policy.settings,...(c.rate_tolerance?{rate_tolerance:c.rate_tolerance}:{})}};s.loading=createLoading(s);return {id:c.id,specification:s};});
mkdirSync(out,{recursive:true});writeFileSync(join(out,'requests.json'),JSON.stringify(requests,null,2)+'\n');
const results={native:[],wasm:[]}, tmp=mkdtempSync('/private/tmp/barodesy-ncl-wire-');
try{
 const described=spawnSync(native,['--describe'],{encoding:'utf8'});assert.equal(described.status,0);assert.deepEqual(JSON.parse(described.stdout),catalogue);
 for(const {id,specification:s}of requests){
  const wire=join(tmp,id+'.txt');writeFileSync(wire,s.loading.controls_bits.join(','));
  const args=['--mode','run-controls','--model',s.model,'--parameters',s.parameters.join(','),'--initial',s.initial.join(','),'--protocol',String(s.protocol),'--integration-settings',settingsCsv(s.integration_settings),'--laboratory-controls-file',wire,'--response-contract',s.response_contract];
  const child=spawnSync(native,args,{encoding:'utf8',maxBuffer:10*1024*1024});
  results.native.push({id,exit_code:child.status,stderr:child.stderr,result:JSON.parse(child.stdout)});
  writeFileSync(join(out,'native.json'),JSON.stringify(results.native,null,2)+'\n');
 }
 const createAtlas=(await import(pathToFileURL(join(wasm,'atlas.js')))).default,engine=await createAtlas();
 assert.deepEqual(JSON.parse(engine.ccall('atlas_describe','string',[],[])),catalogue);
 for(const{id,specification:s}of requests){
  const result=JSON.parse(engine.ccall('atlas_run_controls_scope_with_settings','string',['string','string','string','number','string','string'],[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.loading.controls_bits.join(','),settingsCsv(s.integration_settings)]));
  results.wasm.push({id,result});writeFileSync(join(out,'wasm.json'),JSON.stringify(results.wasm,null,2)+'\n');
 }
 // Preserve every raw response first. Only then enforce the prospective contract.
 for(const backend of Object.keys(results))for(const row of results[backend]){
  const s=requests.find(x=>x.id===row.id).specification;
  if(row.id==='invalid-initial')assert.equal(row.result.ok,false);else{assert.equal(row.result.ok,true,backend+'/'+row.id+': '+row.result.message);verifyScopedLaboratory(row.result,s,catalogue);assert.equal(row.result.points.length,s.steps+1);}
 }
 writeFileSync(join(out,'artifact-receipts.json'),JSON.stringify({catalogue_sha256:catalogue.sha256,files:Object.fromEntries([native,join(wasm,'atlas.js'),join(wasm,'atlas.wasm'),join(dirname(native),'generated/models.json')].map(p=>[p,sha(p)])),scope:'Frozen working source snapshot; not clean release or browser/live qualification'},null,2)+'\n');
 console.log('Seven requests per backend saved; scoped transport and expected success/rejection checks pass.');
}finally{rmSync(tmp,{recursive:true,force:true});}
