import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const [modulePath,requestPath,outputPath]=process.argv.slice(2);
const bytes=readFileSync(requestPath),req=JSON.parse(bytes);
const wasm=await (await import(pathToFileURL(resolve(modulePath)))).default();
const csv=a=>a.map(x=>Object.is(x,-0)?'-0':String(x)).join(',');
function call(z,de,p=req.parameters){
 const args=[req.model,csv(p),csv(z),csv(de),req.settings];
 const stdout=wasm.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),args);
 return {args,returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''};
}
const cases=req.cases.map(c=>({id:c.id,calls:[call(c.initial,c.de),call(c.initial,c.de)]}));
const negatives=req.negatives.map(c=>({id:c.id,bad:call(c.initial,c.de,c.parameters),recovery:call(req.recovery.initial,req.recovery.de)}));
const paths=[];
for(const p of req.paths){
 let z=p.initial;const calls=[];
 for(let i=0;i<p.count;i++){
  const r=call(z,p.increment);calls.push({initial:z,call:r});const out=JSON.parse(r.stdout);if(!out.ok)break;z=out.state;
 }
 const mid=Math.floor(calls.length/2);let restart=mid?JSON.parse(calls[mid-1].call.stdout).state:p.initial;const replay=[];
 for(let i=mid;i<p.count;i++){
  const r=call(restart,p.increment);replay.push(r);const out=JSON.parse(r.stdout);if(!out.ok)break;restart=out.state;
 }
 paths.push({id:p.id,calls,restart:replay});
}
writeFileSync(outputPath,JSON.stringify({backend:'wasm',module_sha256:createHash('sha256').update(readFileSync(modulePath)).digest('hex'),requests_sha256:createHash('sha256').update(bytes).digest('hex'),cases,negatives,paths},null,2)+'\n');
console.log(`Saved ${cases.length} finite cases, ${negatives.length} rejection/recovery pairs and ${paths.length} propagated paths.`);
