import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {loadControlScope,validateControlScope,unsupportedReason} from '../tools/laboratory_control_scope.mjs';
const catalogue={models:readdirSync(new URL('../models/',import.meta.url)).filter(f=>f.endsWith('.json')).map(f=>JSON.parse(readFileSync(new URL('../models/'+f,import.meta.url))))};
test('exact support declarations retain monotonic S-CLAY1 and exclude unsupported controls explicitly',()=>{
 const policy=loadControlScope(catalogue);
 for(const protocol of [1,2])assert.equal(unsupportedReason(policy,{model:'s-clay1',protocol,cycles:0}),'');
 for(const protocol of [0,3,4])assert.match(unsupportedReason(policy,{model:'s-clay1',protocol,cycles:0}),/outside/);
 assert.match(unsupportedReason(policy,{model:'s-clay1',protocol:1,cycles:1}),/Cyclic/);
 assert.equal(unsupportedReason(policy,{model:'linear-elastic',protocol:3,cycles:1}),'');
 assert.match(unsupportedReason(policy,{model:'original-cam-clay-sw-electronic-log-recovery-v1',protocol:3,cycles:1}),/unsupported/);
});
test('changed definitions and missing compiled models cannot inherit a support exception',()=>{
 const policy=loadControlScope(catalogue);
 assert.throws(()=>validateControlScope(policy,catalogue,()=> '0'.repeat(64)),/Stale/);
 assert.throws(()=>validateControlScope(policy,{models:catalogue.models.filter(m=>m.id!=='s-clay1')},()=> '0'.repeat(64)),/Unknown/);
});
