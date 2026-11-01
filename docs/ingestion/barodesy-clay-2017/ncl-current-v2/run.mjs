// Retained common-engine replay only; preserve original policy and requests.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const [packet,out]=process.argv.slice(2).map(p=>resolve(p));
const read=p=>JSON.parse(readFileSync(p,'utf8'));
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const freeze=read(join(packet,'prospective-freeze-v2.json')),root=freeze.root;
for(const [p,h] of Object.entries(freeze.files))assert.equal(sha(resolve(root,p)),h,p);
const native=resolve(root,freeze.native),wasm=resolve(root,freeze.wasm);
const catalogue=read(resolve(root,freeze.catalogue));
assert.equal(catalogue.sha256,freeze.catalogue_hash);
assert.equal(catalogue.models.length,14);
const requests=read(resolve(root,freeze.requests));
const {settingsCsv}=await import(pathToFileURL(join(root,'web/numerics.mjs')));
const {verifyScopedLaboratory}=await import(pathToFileURL(join(root,'web/laboratory-scope.mjs')));
mkdirSync(out,{recursive:false});writeFileSync(join(out,'requests.json'),JSON.stringify(requests,null,2)+'\n');
const collected={native:[],wasm:[]},raw=[];
const save=()=>writeFileSync(join(out,'raw.json'),JSON.stringify(raw,null,2)+'\n');
function child(args,id){
 const p=spawnSync(native,args,{encoding:'utf8',maxBuffer:10*1024*1024,timeout:120000});
 raw.push({backend:'native',id,args,status:p.status,signal:p.signal,error:p.error?String(p.error):null,stdout:p.stdout,stderr:p.stderr});save();
 assert.equal(p.signal,null,id);assert.ok(!p.error,id);
 return p;
}
const describe=child(['--describe'],'metadata');assert.equal(describe.status,0);assert.deepEqual(JSON.parse(describe.stdout),catalogue);
for(const {id,specification:s} of requests){
 const wire=join(out,id+'-controls.txt');writeFileSync(wire,s.loading.controls_bits.join(','));
 const args=['--mode','run-controls','--model',s.model,'--parameters',s.parameters.join(','),'--initial',s.initial.join(','),'--protocol',String(s.protocol),'--integration-settings',settingsCsv(s.integration_settings),'--laboratory-controls-file',wire,'--response-contract',s.response_contract];
 const p=child(args,id);
 collected.native.push({id,exit_code:p.status,stderr:p.stderr,result:JSON.parse(p.stdout)});
 writeFileSync(join(out,'native.json'),JSON.stringify(collected.native,null,2)+'\n');
}
const create=(await import(pathToFileURL(join(wasm,'atlas.js')))).default,engine=await create();
function call(fn,args,types,id){
 const stdout=engine.ccall(fn,'string',types,args);raw.push({backend:'wasm',id,function:fn,args,stdout});save();return JSON.parse(stdout);
}
assert.deepEqual(call('atlas_describe',[],[],'metadata'),catalogue);
for(const {id,specification:s} of requests){
 const args=[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.loading.controls_bits.join(','),settingsCsv(s.integration_settings)];
 const result=call('atlas_run_controls_scope_with_settings',args,['string','string','string','number','string','string'],id);
 collected.wasm.push({id,result});writeFileSync(join(out,'wasm.json'),JSON.stringify(collected.wasm,null,2)+'\n');
}
for(const backend of Object.keys(collected))for(const {id,result}of collected[backend]){
 const s=requests.find(r=>r.id===id).specification;
 if(id==='invalid-initial'){assert.equal(result.ok,false);if(backend==='native')assert.notEqual(collected.native.find(r=>r.id===id).exit_code,0);}
 else{assert.equal(result.ok,true,backend+'/'+id+': '+result.message);verifyScopedLaboratory(result,s,catalogue);if(backend==='native')assert.equal(collected.native.find(r=>r.id===id).exit_code,0);}
}
for(const [p,h]of Object.entries(freeze.files))assert.equal(sha(resolve(root,p)),h,p);
writeFileSync(join(out,'identity.json'),JSON.stringify({catalogue_hash:catalogue.sha256,files:freeze.files,scope:'Exact retained accepted runtime; original seven requests/gates, no rebuild'},null,2)+'\n');
console.log('PASS: seven original requests per native/Wasm backend; raw responses and unchanged scoped checks retained.');
