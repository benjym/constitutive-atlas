import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
const here='docs/ingestion/duncan-chang-1970/integration-v1/portable-controls-v1';
assert.ok(!existsSync(here+'/power-probes.json'));
const requests=JSON.parse(readFileSync(here+'/../common-residual-v1/power-v3/requests.json')).cases;
const saved=JSON.parse(readFileSync(here+'/../common-residual-v1/power-v3/results.json')).results;
const results=[];
for(let i=0;i<requests.length;i++){
 const c=requests[i];assert.equal(c.id,saved[i].id);
 const args=['--mode','evaluate','--model',c.model,'--parameters',c.parameters.join(','),'--current',c.current.join(','),'--initial',c.previous.join(','),'--strain',c.strain.join(',')];
 const n=spawnSync('/private/tmp/atlas-duncan-portable-controls-v1/native/atlas_solver',args,{encoding:'utf8',timeout:30000});assert.equal(n.status,0,n.stdout+n.stderr);
 const response=JSON.parse(n.stdout),expected=saved[i].wasm.response;
 results.push({id:c.id,args,raw:n.stdout,response,expected,exact:JSON.stringify(response)===JSON.stringify(expected)});
 writeFileSync(here+'/power-probes.json',JSON.stringify({scope:'Diagnostic candidate full response versus saved identical-input baselineWasm; exact equality required for every36probes',results},null,2)+'\n');
}
assert.ok(results.every(r=>r.exact),'Candidate power probes differ from saved Wasm');
console.log('36candidate power probe full responses exactly match savedbaselineWasm');
