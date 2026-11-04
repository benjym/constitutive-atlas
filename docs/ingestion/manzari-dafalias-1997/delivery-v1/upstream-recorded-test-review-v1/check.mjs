import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {validateRecordedRun} from '../../../../../web/recorded.mjs';
const root=new URL('../../../../../',import.meta.url),out=new URL('./',import.meta.url),hash=b=>createHash('sha256').update(b).digest('hex'),read=p=>readFileSync(new URL(p,root)),json=p=>JSON.parse(read(p));
const paths=['catalogue/investigations/recorded-replay-api-v1/responses.json.gz','catalogue/investigations/recorded-restarts-v1/responses.json.gz','protocols/recorded-dp-restart-run.json'];
const retained=JSON.parse(gunzipSync(read(paths[0]))),restarts=JSON.parse(gunzipSync(read(paths[1]))),example=json(paths[2]);
const actual=read('tools/test_recorded.mjs').toString();
const start=actual.indexOf('   const s=structuredClone(historical);'),end=actual.indexOf('   const {controls,knots}=recordedWire(s)',start);assert.ok(start>=0&&end>start);
const prepare=new Function('historical','frozen','assert','validateRecordedRun',actual.slice(start,end)+'return s;');
const corpus=[...retained,...restarts,{request:example}],original=structuredClone(corpus);assert.equal(corpus.length,46);assert.equal(retained.length+restarts.length,45);
let supplied=0,preserved=0;
for(const {request,response}of corpus){const s=prepare(request,response,assert,validateRecordedRun);assert.notEqual(s,request);if(Object.hasOwn(request,'initial')){assert.deepEqual(s,request);assert.notEqual(s.initial,request.initial);preserved++;}else{assert.deepEqual(s,{...request,initial:response.initial});assert.notEqual(s.initial,response.initial);supplied++;}}
assert.deepEqual(corpus,original);
const request=retained.find(x=>!Object.hasOwn(x.request,'initial')).request;
for(const frozen of [undefined,{}, {initial:[]},{initial:[NaN]},{initial:[Infinity]}])assert.throws(()=>prepare(request,frozen,assert,validateRecordedRun));
const report={identity:'recorded-explicit-state-source-review-v1',source_only:true,compiled_calls:0,passed:true,corpus_count:corpus.length,historical_count:45,example_count:1,explicit_initial_supplied:supplied,existing_initial_preserved:preserved,malformed_frozen_state_refusals:5,original_inputs_unchanged:true,source_sha256:hash(read('tools/test_recorded.mjs')),frozen_files:Object.fromEntries(paths.map(p=>[p,hash(read(p))]))};
writeFileSync(new URL('pure-checks.json',out),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
