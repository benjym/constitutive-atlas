import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runScopedRecorded,verifyScopedRecordedResponse} from '../web/recorded-scope-execution.mjs';
const payload=JSON.parse(readFileSync(0,'utf8')),results=[];
for(const row of payload.rows){
 const before=JSON.stringify(row);let accepted=true;
 try{verifyScopedRecordedResponse(row.response,row.request,payload.catalogue);}catch{accepted=false;}
 assert.equal(accepted,row.accepted,row.label);
 if(accepted){
  const calls=[];const engine={ccall(name,type,types,args){calls.push({name,args});if(name==='atlas_describe')return JSON.stringify(payload.catalogue);return JSON.stringify(row.response);}};
  assert.deepEqual(runScopedRecorded(engine,row.request,payload.catalogue),row.response);
  assert.deepEqual(calls.map(c=>c.name),['atlas_describe',row.request.restart_settings?'atlas_replay_recorded_scope_with_restarts':'atlas_replay_recorded_scope']);
  assert.equal(calls[1].args.at(-1),row.request.stress_scope);
 }
 assert.equal(JSON.stringify(row),before);results.push(accepted);
}
const good=payload.rows.find(r=>r.accepted);let calls=[];
assert.throws(()=>runScopedRecorded({ccall(name){calls.push(name);if(name==='atlas_describe')return JSON.stringify(payload.catalogue);throw Error('missing scoped export');}},good.request,payload.catalogue));
assert.deepEqual(calls,['atlas_describe',good.request.restart_settings?'atlas_replay_recorded_scope_with_restarts':'atlas_replay_recorded_scope']);
const mismatch=structuredClone(good.request);mismatch.stress_scope=mismatch.stress_scope==='total'?'effective':'total';calls=[];
assert.throws(()=>runScopedRecorded({ccall(name){calls.push(name);}},mismatch,payload.catalogue));assert.deepEqual(calls,[]);
const changed=structuredClone(payload.catalogue);changed.sha256='0'.repeat(64);calls=[];
assert.throws(()=>runScopedRecorded({ccall(name){calls.push(name);return JSON.stringify(changed);}},good.request,payload.catalogue));assert.deepEqual(calls,['atlas_describe']);
process.stdout.write(JSON.stringify(results));
