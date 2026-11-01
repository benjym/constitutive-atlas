import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const here='docs/ingestion/duncan-chang-1970/integration-v1/math-trace-v1';
assert.ok(!existsSync(here+'/results.json'));
const wasm=await(await import(pathToFileURL('/private/tmp/atlas-duncan-integration-v1/wasm/atlas.js'))).default();
const requests=JSON.parse(readFileSync(here+'/requests.json')),results=[];
for(const c of requests.cases){
 const csv=x=>x.join(',');const args=[c.model,csv(c.parameters),csv(c.current),csv(c.previous),csv(c.strain)];
 const command=['--mode','evaluate','--model',args[0],'--parameters',args[1],'--current',args[2],'--initial',args[3],'--strain',args[4]];
 const n=spawnSync('/private/tmp/atlas-duncan-contraction-v1/native/atlas_solver',command,{encoding:'utf8'});assert.equal(n.status,0,n.stdout+n.stderr);
 const w=wasm.ccall('atlas_evaluate','string',['string','string','string','string','string'],args);
 const native=JSON.parse(n.stdout),browser=JSON.parse(w);assert.equal(native.ok,true);assert.equal(browser.ok,true);
 results.push({id:c.id,args,native_raw:n.stdout,wasm_raw:w,isolated_shear_native:native.values[3],isolated_shear_wasm:browser.values[3],difference:native.values[3]-browser.values[3]});
 writeFileSync(here+'/results.json',JSON.stringify({scope:requests.scope,results},null,2)+'\n');
}
console.log(results.map(x=>({id:x.id,difference:x.difference})));
