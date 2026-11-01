import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {encodeArgs,decodeRequest} from './transport.mjs';
import {boundedCall} from './runner.mjs';
let checks=0;function check(v){assert(v);checks++;}
for(const number of [-0,0,1,-1,Number.MIN_VALUE,Number.MAX_VALUE,Infinity,-Infinity,NaN]){const args=['id','p','z',number,number,number,number,'settings'],types=['string','string','string','number','number','number','number','string'];const r=JSON.parse(JSON.stringify({name:'atlas_run_scope_with_settings',result:'string',types,encoded_args:encodeArgs(types,args)}));const decoded=decodeRequest(r);check(decoded.every((v,i)=>Object.is(v,args[i])));}
for(const mutate of [r=>r.name='system',r=>r.result='number',r=>r.types[0]='number',r=>r.encoded_args[0]=1,r=>r.encoded_args.pop(),r=>r.encoded_args.push('extra')]){const r={name:'atlas_integrate',result:'string',types:['string','string','string','string'],encoded_args:['id','p','z','de']};mutate(r);assert.throws(()=>decodeRequest(r));checks++;}
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'lade-wasm-runner-'));try{
 const worker=path.join(dir,'synthetic.mjs');fs.writeFileSync(worker,"import fs from 'node:fs';const r=JSON.parse(fs.readFileSync(0,'utf8'));if(r.mode==='hang'){process.stderr.write('started');setInterval(()=>{},1000);}else if(r.mode==='bad'){process.stderr.write('failure');process.exit(3);}else if(r.mode==='large'){process.stdout.write('x'.repeat(100000));}else{process.stdout.write(JSON.stringify(r));}");
 let r=boundedCall(worker,{mode:'echo',value:'-0'},{timeout:2000});check(r.status===0&&!r.error&&JSON.parse(r.stdout).value==='-0');r=boundedCall(worker,{mode:'bad'},{timeout:2000});check(r.status===3&&r.stderr.toString()==='failure');r=boundedCall(worker,{mode:'hang'},{timeout:200});check(r.error?.code==='ETIMEDOUT'&&r.signal==='SIGKILL');r=boundedCall(worker,{mode:'large'},{timeout:2000,maxBuffer:1024});check(!!r.error&&r.stdout.length>0);
}finally{fs.rmSync(dir,{recursive:true});}
console.log(JSON.stringify({checks,passed:true,scope:'synthetic transport/watchdog only; no Wasm material execution'}));
