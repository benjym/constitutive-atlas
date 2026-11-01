// Same frozen flat C ABI requests as native; no material-specific JS.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
const [moduleFile,wasmFile,requestFile,outputFile]=process.argv.slice(2);
const createModule=(await import(pathToFileURL(path.resolve(moduleFile)))).default;
const module=await createModule({wasmBinary:fs.readFileSync(wasmFile)});
const requests=JSON.parse(fs.readFileSync(requestFile,'utf8'));const rows=[];
for(const req of requests.requests){
 const allocated=[];
 const allocate=values=>{const p=module._malloc(Math.max(8,8*values.length));if(!p)throw Error('allocation failed');allocated.push(p);module.HEAPF64.set(values.map(Number),p/8);return p;};
 const read=(p,n)=>Array.from(module.HEAPF64.subarray(p/8,p/8+n));
 const ns=req.state.length,np=req.parameters.length,nc=req.current_controls.length,no=req.observable_count;
 const values=[req.state,req.parameters,req.current_controls,req.start_controls,req.end_controls,req.settings].map(v=>v.map(Number));
 const [state,params,current,start,end,settings]=values.map(allocate);
 const output=allocate(Array(ns).fill(-1234567)),coordinate=allocate([-7654321]),obs=allocate(Array(no).fill(-1234567));
 const status=module._path_advance(req.model,state,ns,Number(req.coordinate),params,np,current,nc,Number(req.progress),start,end,settings,req.settings.length,output,coordinate,obs,no);
 const same=(a,b)=>a.length===b.length&&a.every((x,i)=>Object.is(x,b[i])||x===b[i]);
 for(const [i,p] of [state,params,current,start,end,settings].entries())if(!same(read(p,values[i].length),values[i]))throw Error(`input mutation ${req.id}`);
 const out=read(output,ns),co=read(coordinate,1)[0],ob=read(obs,no);
 if(status===0&&(!same(out,Array(ns).fill(-1234567))||co!==-7654321||!same(ob,Array(no).fill(-1234567))))throw Error(`failed output mutation ${req.id}`);
 rows.push({id:req.id,status,state:out,coordinate:co,observables:ob});
 for(const p of allocated)module._free(p);
}
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
fs.writeFileSync(outputFile,JSON.stringify({module_sha256:sha(moduleFile),wasm_sha256:sha(wasmFile),request_sha256:sha(requestFile),rows},null,2)+'\n');
