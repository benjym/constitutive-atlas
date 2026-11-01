import {createBoundedModule} from './wasm-bounded-v1/runner.mjs';
// Additional sequential backend qualification; literal request parity remains separate.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..');
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8')),hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const build=path.join(root,'.local/lade-outer-predictor-v1/wasm-build');
const module=createBoundedModule(build,path.join(root,'.local/lade-outer-predictor-v1/wasm-bounded-chains'));
const rawdir=path.join(root,'.local/lade-outer-predictor-v1/wasm-chain-requests');fs.mkdirSync(rawdir,{recursive:true});
const model=read('model.json'),native=read('native-domain-results.json'),requests=[],checks=[];
const get=(cmd,key)=>cmd[cmd.indexOf(key)+1],nums=(cmd,key)=>get(cmd,key).split(',').map(Number),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function check(name,passed,detail){checks.push({name,passed:!!passed,detail});}
function call(command){
 const args=['--model','--parameters','--initial','--strain','--integration-settings'].map(k=>get(command,k));
 const raw=module.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],args),r=JSON.parse(raw),dest=path.join(rawdir,`${requests.length}.json`);fs.writeFileSync(dest,raw);
 requests.push({command,raw_path:path.relative(root,dest),raw_sha256:hash(raw)});return r;
}
let previousNative=null,previousWasm=null,previousSignature=null;
for(let i=0;i<native.requests.length;i++){
 const row=native.requests[i],n=JSON.parse(fs.readFileSync(path.join(root,row.raw_path),'utf8')),command=[...row.command],original=nums(command,'--initial');
 const signature=[get(command,'--parameters'),get(command,'--strain')];
 const continuation=previousNative?.ok&&same(previousNative.state,original)&&same(previousSignature,signature);
 if(continuation&&previousWasm?.ok)command[command.indexOf('--initial')+1]=previousWasm.state.join(',');
 const parent=nums(command,'--initial'),r=call(command);check(`chain_${i}_status`,r.ok===n.ok);
 const de=nums(command,'--strain');
 if(de.every(x=>x===0)&&r.ok)check(`chain_${i}_hold`,same(r.state,parent));
 if(!r.ok){
   check(`chain_${i}_rollback`,same(r.state,parent));
   const params=Object.fromEntries(Object.keys(model.parameters).map((k,j)=>[k,nums(command,'--parameters')[j]]));
   const mean=(parent[0]+parent[1]+parent[2])/3,B=parent.slice(0,6).map(x=>x/mean),hydro=Math.max(...parent.slice(0,3))-Math.min(...parent.slice(0,3))<=mean*1e-12&&Math.max(...parent.slice(3,6).map(Math.abs))<=mean*1e-12,ratio=hydro?1:.9;
   const ec=(mean/params.pa)**(1-params.n)/((1-params.n)*params.Kur*ratio**params.n),valid=B.map(x=>-.001*ec*x);
   const direct=[...command];direct[direct.indexOf('--strain')+1]=valid.join(',');const retry=[...direct];retry[retry.indexOf('--initial')+1]=r.state.join(',');
   const a=call(direct),b=call(retry);check(`chain_${i}_recovery`,a.ok&&b.ok&&same(a.state,b.state));
 }
 previousNative=n;previousWasm=r;previousSignature=signature;
 if(i%25===0)console.log(`chain domain ${i}/${native.requests.length}`);
}
const report={id:'lade1975-wasm-self-chain-v1',requests,checks,passed:checks.every(x=>x.passed),bindings:Object.fromEntries(['model.json','POLICY.json','SUPPLEMENT_POLICY.json','native-domain-results.json','check_wasm_chains.mjs'].map(n=>[n,hash(fs.readFileSync(path.join(here,n)))])),wasm_sha256:hash(fs.readFileSync(path.join(build,'lade-domain.wasm')))};
fs.writeFileSync(path.join(here,'wasm-chain-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,requests:requests.length,checks:checks.length,failures:checks.filter(x=>!x.passed)},null,2));process.exitCode=report.passed?0:1;
