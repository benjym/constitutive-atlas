import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateScopedRecordedRun,validateScopedRecordedModel,scopedRecordedWire} from '../web/recorded-scope.mjs';
import {runRecorded} from '../web/recorded.mjs';
const cases=JSON.parse(readFileSync(0,'utf8')),results=[];
for(const entry of cases){
 const before=JSON.stringify(entry);let result;
 try{
  assert.equal(validateScopedRecordedRun(entry.request),entry.request);
  assert.equal(validateScopedRecordedModel(entry.request,entry.model),entry.request);
  result={accepted:true,wire:scopedRecordedWire(entry.request,entry.model)};
 }catch(error){result={accepted:false};}
 assert.equal(JSON.stringify(entry),before,'codec mutated input');
 assert.equal(result.accepted,entry.accepted,entry.name);
 let calls=0;assert.throws(()=>runRecorded({ccall(){calls++;throw Error('engine should not be called');}},entry.request));assert.equal(calls,0,'legacy engine fallback');
 results.push(result);
}
process.stdout.write(JSON.stringify(results));
