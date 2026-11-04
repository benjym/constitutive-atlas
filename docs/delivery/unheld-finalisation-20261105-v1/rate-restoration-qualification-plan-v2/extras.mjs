// Supplemental exact public replay. Existing generic scope helper; no material kernel.
import assert from'node:assert/strict';import fs from'node:fs';import{join,dirname,resolve}from'node:path';import{fileURLToPath,pathToFileURL}from'node:url';import{spawnSync}from'node:child_process';import{createHash}from'node:crypto';
import{runScopedLaboratory}from'../nine-example-refresh-plan-v1/context/web/laboratory-scope.mjs';
import{parity,withoutElapsed,journalEngine}from'../nine-example-refresh-plan-v1/collector-core.mjs';
const H=dirname(fileURLToPath(import.meta.url)),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const[backend,actualArg,manifestSHA]=process.argv.slice(2),plan=read(join(H,'plan.json'));assert.ok(['native','wasm','pair'].includes(backend));assert.equal(resolve(actualArg),plan.actual);const actual=resolve(actualArg),f=read(join(actual,'execution-freeze.json')),requests=read(join(H,'requests.json')),policy=read(join(H,'../nine-example-refresh-plan-v1/policy.json'));
const pinCheck=p=>{assert.equal(sha(p.path),p.sha256);assert.equal(fs.statSync(p.path).size,p.bytes);};
function guard(full=false){const binding=read(join(actual,'plan-binding.json'));pinCheck(binding.launch_binding);const launch=read(binding.launch_binding.path);pinCheck(launch.plan_review);for(const item of Object.values(launch.installations)){pinCheck(item.receipt);pinCheck(item.review);for(const pin of item.source_pins)pinCheck(pin);}assert.equal(sha(join(H,'manifest.json')),manifestSHA);for(const r of read(join(H,'manifest.json')).files){assert.ok(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));assert.equal(sha(join(H,r.path)),r.sha256);assert.equal(fs.statSync(join(H,r.path)).size,r.size_bytes);}for(const p of read(join(H,'external-pins.json')))pinCheck(p);for(const p of Object.values(f.artifacts))pinCheck(p);if(full)for(const p of f.inputs)pinCheck(p);}
guard(true);assert.equal(read(join(actual,'native/receipt.json')).passed,true);assert.equal(read(join(actual,'wasm/receipt.json')).passed,true);assert.equal(read(join(actual,'pair.json')).passed,true);
const catalogue=read(join(plan.work,'native/generated/models.json'));assert.equal(catalogue.models.length,17);assert.equal(catalogue.sha256,'4e31188499b5d19e52439451a709775f00e08a1f4d94570e40f43d825cd0e0a1');
const out=join(actual,'extra-'+backend);assert.ok(!fs.existsSync(out),'never overwrite supplemental observation');fs.mkdirSync(out);const journal=join(out,'transport.ndjson'),emit=r=>fs.appendFileSync(journal,JSON.stringify(r)+'\n');
const report={identity:'control-restoration-C-twelve-public-supplement-v2',backend,status:'running',rows:[],catalogue_hash:catalogue.sha256,manifest_sha256:manifestSHA};const save=()=>fs.writeFileSync(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');save();let primary=null;
function normalized702(reference){assert.equal(reference.catalogue_hash,'beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575');const d=structuredClone(reference);d.catalogue_hash=catalogue.sha256;return d;}
try{
 if(backend==='pair'){
  const native=read(join(actual,'extra-native/report.json')),wasm=read(join(actual,'extra-wasm/report.json'));assert.equal(native.status,'passed');assert.equal(wasm.status,'passed');assert.equal(native.rows.length,12);assert.equal(wasm.rows.length,12);assert.deepEqual(native.rows.map(r=>r.id),requests.map(r=>r.id));assert.deepEqual(wasm.rows.map(r=>r.id),requests.map(r=>r.id));
  for(let i=0;i<requests.length;i++){const a=native.rows[i],b=wasm.rows[i];assert.deepEqual(a.specification,b.specification);report.rows.push({id:a.id,...parity(a.result,b.result,policy)});save();}
 }else{
  let transport;
  if(backend==='wasm'){
   guard();emit({phase:'module-initialization-before',module:f.artifacts.module,wasm:f.artifacts.wasm});
   transport=await(await import(pathToFileURL(f.artifacts.module.path))).default({wasmBinary:fs.readFileSync(f.artifacts.wasm.path),print:()=>{},printErr:s=>process.stderr.write(String(s)+'\n')});emit({phase:'module-initialization-returned'});guard();
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
    const command=[f.artifacts.native.path,...argv];guard();emit({phase:'native-process-before',argv:command,cwd:f.repo});let p;
    try{p=spawnSync(command[0],command.slice(1),{cwd:f.repo,encoding:'utf8',timeout:policy.native_transport_timeout_ms,maxBuffer:policy.native_transport_max_buffer});}
    catch(e){emit({phase:'native-process-exception',error:{name:e.name,message:e.message,stack:e.stack}});throw e;}
    emit({phase:'native-process-returned',argv:command,status:p.status,signal:p.signal,stdout:p.stdout,stderr:p.stderr,error:p.error?{name:p.error.name,message:p.error.message,code:p.error.code}:null});guard();assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');const result=JSON.parse(p.stdout);assert.equal(p.status,name==='atlas_describe'||result.ok?0:1);return p.stdout;
   }};
  }
  const bound={ccall(...args){guard();let error=null;try{return transport.ccall(...args);}catch(e){error=e;throw e;}finally{try{guard();}catch(e){emit({phase:'post-call-binding-failure',error:String(e),primary:error?String(error):null});if(!error)throw e;}}}};
  const engine=journalEngine(bound,emit);
  for(const row of requests){
   const entry={id:row.id,specification:structuredClone(row.specification)};report.rows.push(entry);save();const document=read(row.document.path);assert.deepEqual(document.specification,row.specification);const result=runScopedLaboratory(engine,row.specification,catalogue);entry.result=result;save();assert.equal(result.ok,true);assert.equal(result.points.length,row.kind==='named-original702'?read(row.document.path).result.points.length:101);assert.deepEqual(result.loading.controls_bits,row.specification.loading.controls_bits);assert.deepEqual(result.integration_settings,row.specification.integration_settings);
   entry.replay=runScopedLaboratory(engine,row.specification,catalogue);save();assert.deepEqual(withoutElapsed(result),withoutElapsed(entry.replay));entry.exact_replay=true;
   if(row.id==='igs97-edited-initial'||row.kind==='named-original702'){
    const reference=read(row[backend+'_reference'].path),physical=reference.result??reference;
    entry.original702_comparison=parity(result,normalized702(physical),policy);entry.reference_scope='original frozen1e-10 physical/exactother; reference catalogue key normalized only';
   }else if(backend==='wasm'){
    assert.deepEqual(withoutElapsed(result),withoutElapsed(read(row.wasm_reference.path).result));entry.live640_samebackend_exact=true;
   }
   entry.passed=true;save();
  }
 }
 assert.equal(report.rows.length,12);report.status='passed';save();
}catch(e){primary=e;report.status='failed';report.error={name:e.name,message:e.message,stack:e.stack};save();emit({phase:'supplement-exception',error:report.error});throw e;}
finally{try{guard(true);report.post_bindings_unchanged=true;save();}catch(e){report.status='failed';report.post_binding_error=String(e);save();if(!primary)throw e;}emit({phase:'supplement-final',status:report.status});}
