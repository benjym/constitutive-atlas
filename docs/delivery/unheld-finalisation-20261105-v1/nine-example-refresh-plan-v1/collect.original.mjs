// Coordinator execution child only; actual imports are gated by run.py before launch.
import assert from 'node:assert/strict';import fs from 'node:fs';import {dirname,resolve,join} from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {spawnSync} from 'node:child_process';import {createHash} from 'node:crypto';
import {collect,journalEngine,parity} from './collector-core.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const [backend,outArg,freezeArg]=process.argv.slice(2);assert.ok(['native','wasm','compare'].includes(backend)&&outArg&&freezeArg);const out=resolve(outArg),freeze=read(freezeArg),rows=read(join(HERE,'requests.json')),policy=read(join(HERE,'policy.json'));
assert.ok(!fs.existsSync(out),'Never overwrite observation');fs.mkdirSync(out);
const journal=join(out,'transport.ndjson');fs.writeFileSync(journal,'',{flag:'wx'});const emit=r=>fs.appendFileSync(journal,JSON.stringify(r)+'\n');
const checkpoint=r=>fs.writeFileSync(join(out,'report.json'),JSON.stringify(r,null,2)+'\n');
let failure=null;
try{
 if(backend==='compare'){
  const native=read(join(dirname(out),'native/report.json')),wasm=read(join(dirname(out),'wasm/report.json'));assert.equal(native.status,'passed');assert.equal(wasm.status,'passed');assert.equal(native.catalogue_hash,wasm.catalogue_hash);assert.equal(native.rows.length,9);assert.equal(wasm.rows.length,9);
  const pairs=native.rows.map((a,i)=>{const b=wasm.rows[i];assert.equal(a.id,b.id);assert.deepEqual(a.specification,b.specification);return {id:a.id,...parity(a.result,b.result,policy)};});checkpoint({status:'passed',identity:'baseline-nine-named-native-wasm-pair-v1',catalogue_hash:native.catalogue_hash,policy_sha256:sha(join(HERE,'policy.json')),pairs});
 }else{
  const catalogue=read(freeze.metadata.path);let transport;
  if(backend==='wasm'){
   emit({phase:'module-initialization-before',module:freeze.artifacts.module,wasm:freeze.artifacts.wasm});
   try{transport=await(await import(pathToFileURL(freeze.artifacts.module.path))).default();emit({phase:'module-initialization-returned'});}
   catch(e){emit({phase:'module-initialization-exception',error:{name:e.name,message:e.message,stack:e.stack}});throw e;}
  }else{
   fs.mkdirSync(join(out,'controls'));let serial=0;
   transport={ccall(name,type,types,args){
    let argv=['--describe'];
    if(name!=='atlas_describe'){
     assert.ok(['atlas_run_controls_scope_with_settings','atlas_run_scope_with_settings'].includes(name));
     argv=['--response-contract','stress-scope-0.1','--mode',name.includes('controls')?'run-controls':'run','--model',args[0],'--parameters',args[1],'--initial',args[2],'--protocol',String(args[3])];
     if(name.includes('controls')){const wire=join(out,'controls',String(serial++)+'.csv');fs.writeFileSync(wire,args[4],{flag:'wx'});argv.push('--laboratory-controls-file',wire,'--integration-settings',args[5]);}
     else argv.push('--target',String(args[4]),'--steps',String(args[5]),'--cycles',String(args[6]),'--integration-settings',args[7]);
    }
    const command=[freeze.artifacts.native.path,...argv],started=performance.now();emit({phase:'native-process-before',argv:command,cwd:freeze.repo,executable:freeze.artifacts.native,started_epoch_ms:Date.now()});
    let p;
    try{p=spawnSync(command[0],command.slice(1),{cwd:freeze.repo,encoding:'utf8',timeout:policy.native_transport_timeout_ms,maxBuffer:policy.native_transport_max_buffer});}
    catch(e){emit({phase:'native-process-exception',argv:command,error:{name:e.name,message:e.message,stack:e.stack},elapsed_ms:performance.now()-started});throw e;}
    emit({phase:'native-process-returned',argv:command,status:p.status,signal:p.signal,stdout:p.stdout,stderr:p.stderr,error:p.error?{name:p.error.name,message:p.error.message,code:p.error.code}:null,elapsed_ms:performance.now()-started});
    assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');const result=JSON.parse(p.stdout);assert.equal(p.status,name==='atlas_describe'||result.ok?0:1);return p.stdout;
   }};
  }
  collect(rows,catalogue,journalEngine(transport,emit),{checkpoint,readOld:r=>{assert.equal(sha(r.old_document.path),r.old_document.sha256);return read(r.old_document.path);},saveDocument:(id,kind,doc)=>fs.writeFileSync(join(out,id+'-'+kind+'.json'),JSON.stringify(doc,null,2)+'\n',{flag:'wx'})});
 }
}catch(e){failure={name:e.name,message:e.message,stack:e.stack};emit({phase:'collector-exception',error:failure});if(!fs.existsSync(join(out,'report.json')))checkpoint({status:'failed',error:failure});throw e;}
finally{emit({phase:'collector-final',status:failure?'failed':'passed'});}
