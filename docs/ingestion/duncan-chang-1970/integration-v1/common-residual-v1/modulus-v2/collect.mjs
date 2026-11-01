import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const here='docs/ingestion/duncan-chang-1970/integration-v1/common-residual-v1/modulus-v2';
assert.ok(!existsSync(here+'/results.json'));
for(const [p,h] of Object.entries(JSON.parse(readFileSync(here+'/freeze.json')).files))assert.equal(createHash('sha256').update(readFileSync(p)).digest('hex'),h,p);
const wasm=await(await import(pathToFileURL('/private/tmp/atlas-duncan-integration-v1/wasm/atlas.js'))).default();
const requests=JSON.parse(readFileSync(here+'/requests.json')),results=[];
for(const c of requests.cases){
 const args=[c.model,c.parameters.join(','),c.current.join(','),c.previous.join(','),c.strain.join(',')];
 const command=['--mode','evaluate','--model',args[0],'--parameters',args[1],'--current',args[2],'--initial',args[3],'--strain',args[4]];
 const row={id:c.id,args};
 for(const [backend,path] of [['baseline','/private/tmp/atlas-duncan-integration-v1/native/atlas_solver'],['no_contraction','/private/tmp/atlas-duncan-contraction-v1/native/atlas_solver']]){
  const n=spawnSync(path,command,{encoding:'utf8',timeout:30000});assert.ok([0,1].includes(n.status),n.stderr);row[backend]={exit_status:n.status,raw:n.stdout,response:JSON.parse(n.stdout)};
 }
 const raw=wasm.ccall('atlas_evaluate','string',['string','string','string','string','string'],args);row.wasm={raw,response:JSON.parse(raw)};
 results.push(row);
 writeFileSync(here+'/results.json',JSON.stringify({scope:requests.scope,results},null,2)+'\n');
}
const summaries={};
for(const b of ['baseline','no_contraction']){
 const diffs=[],rejections=[];
 for(const r of results){const n=r[b].response,w=r.wasm.response;if(n.ok!==w.ok)rejections.push(r.id);else if(n.ok)for(let i=0;i<n.values.length;i++)if(n.values[i]!==w.values[i])diffs.push({id:r.id,component:i,native:n.values[i],wasm:w.values[i],difference:n.values[i]-w.values[i]});}
 summaries[b]={domain_disagreements:rejections,component_differences:diffs};
}
writeFileSync(here+'/summary.json',JSON.stringify({cases:results.length,summaries},null,2)+'\n');
console.log(Object.fromEntries(Object.entries(summaries).map(([b,v])=>[b,{domain_disagreements:v.domain_disagreements.length,component_differences:v.component_differences.length,first:v.component_differences[0]}])));
