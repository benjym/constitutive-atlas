// Opaque collection only: the frozen Python assessor owns source/numerical gates.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,resolve,extname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
assert.equal(process.argv.length,5,'protocol, build receipt and fresh output required');
const [protocolPath,buildPath,output]=process.argv.slice(2).map(p=>resolve(p));
const suffix=extname(output);
const rawPath=(suffix?output.slice(0,-suffix.length):output)+'.transport.json';
assert.ok(output!==rawPath&&!existsSync(output)&&!existsSync(rawPath),'fresh output/raw required');
const held=new Map();
const bytes=p=>{p=resolve(p);if(!held.has(p))held.set(p,readFileSync(p));return held.get(p);};
const sha=p=>createHash('sha256').update(bytes(p)).digest('hex');
const check=()=>{for(const [p,b] of held)assert.ok(readFileSync(p).equals(b),'input changed during collection: '+p);};
const protocol=JSON.parse(bytes(protocolPath)),build=JSON.parse(bytes(buildPath));
assert.equal(protocol.version,'research-instantaneous-rate-protocol-0.2');
assert.equal(build.backend,'wasm');assert.equal(build.protocol_sha256,sha(protocolPath));
assert.equal(build.all_commands_succeeded,true);
assert.deepEqual(Object.keys(build.artifacts).sort(),['loader','wasm']);
for(const [name,pin] of Object.entries(protocol.files))assert.equal(sha(resolve(root,name)),pin,'source pin: '+name);
for(const artifact of Object.values(build.artifacts)){
 assert.equal(typeof artifact.path,'string');assert.equal(sha(artifact.path),artifact.sha256,'artifact pin');
}
// Validate the exact generic schema/model/CSV contract before importing a loader.
// Node also holds every pinned byte for a lifetime check after collection.
const validation=spawnSync(process.env.ATLAS_PYTHON||'python3',['-B','-c',
 "from tools.research_rate_observations_v2 import checked_protocol,build_receipt; import sys; checked_protocol(sys.argv[1]); build_receipt(sys.argv[2],sys.argv[1],'wasm',True)",
 protocolPath,buildPath],{cwd:root,encoding:'utf8',timeout:60000});
assert.equal(validation.status,0,'pre-execution validation: '+(validation.stderr||validation.error||''));
const collectorHash=sha(fileURLToPath(import.meta.url));check();
mkdirSync(dirname(output),{recursive:true});
const journal=[];
const receipt={version:'research-instantaneous-rate-observation-0.2',backend:'wasm',
 protocol_sha256:sha(protocolPath),build_receipt_sha256:sha(buildPath),build_receipt:build,
 collector_sha256:collectorHash,completed:false,stdout:[],stderr:[]};
const save=()=>{
 writeFileSync(rawPath,JSON.stringify(journal)+'\n');
 receipt.transport_sha256=createHash('sha256').update(readFileSync(rawPath)).digest('hex');
 writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
};
save();
try{
 const factory=(await import(pathToFileURL(resolve(build.artifacts.loader.path)).href)).default;
 assert.equal(typeof factory,'function','modular loader factory');
 const module=await factory({wasmBinary:bytes(build.artifacts.wasm.path),
  print:text=>{receipt.stdout.push(String(text));},printErr:text=>{receipt.stderr.push(String(text));}});
 const call=(name,types,args)=>{
  const row={name,types,args};
  try{row.raw=module.ccall(name,'string',types,args);}
  catch(error){row.raw=null;row.exception=String(error);journal.push(row);save();throw error;}
  journal.push(row);save();assert.equal(typeof row.raw,'string','opaque string response');
 };
 call('atlas_describe',[],[]);
 for(const request of protocol.cases)call('atlas_research_rate',['string','string','string','string'],request.args);
 check();receipt.completed=true;save();
}catch(error){receipt.error=String(error);save();throw error;}
console.log('Retained descriptor and '+protocol.cases.length+' opaque rate responses; assessment remains separate.');
