import assert from 'node:assert/strict';
import test from 'node:test';
import {parseRecordedJSON as parse} from '../web/recorded.mjs';
test('reject duplicate decoded names at every depth',()=>{
 for(const text of ['{"a":1,"a":2}','{"a":1,"\\u0061":2}','[{"x":null,"x":false}]','{"outer":{"k":0,"k":1}}','{"__proto__":0,"__proto__":1}','{"a\\\\b":0,"a\\u005cb":1}'])assert.throws(()=>parse(text),/duplicate/i,text);
});
test('reject nonfinite numbers including unused fields',()=>{
 for(const text of ['1e999','-1e999','{"unused":1e999}','[0,{"x":-2E309}]'])assert.throws(()=>parse(text),/finite/i,text);
});
test('preserve exact integer transport policy',()=>{
 for(const text of ['9007199254740993','-9007199254740993','{"n":9007199254740995}'])assert.throws(()=>parse(text),/exactly representable/);
 for(const text of ['9007199254740992','9007199254740994','-9007199254740994','1e20','9007199254740993.0'])assert.deepEqual(parse(text),JSON.parse(text));
});
test('native values, escapes, signed zero and finite extremes survive',()=>{
 const cases=['null','true','false','[]','{}','-0','-0.0','-0e0','5e-324','-5e-324','1.7976931348623157e308','1e-999','{"a":0,"child":{"a":1},"arr":[{"a":2},{"a":3}]}','{"__proto__":{"safe":true},"constructor":3}','{"a,b:{}[]": "1e999 \\" \\\\"}'];
 for(const text of cases)assert.deepEqual(parse(text),JSON.parse(text),text);
 assert(Object.is(parse('-0'),-0));assert(Object.is(parse('-1e-999'),-0));
 const text=JSON.stringify({text:'Unicode 😃 and newline\n and quote " and slash \\',array:[0,null,false,{x:1}]});assert.deepEqual(parse(text),JSON.parse(text));
});
test('malformed JSON remains rejected',()=>{
 for(const text of ['','01','+1','NaN','Infinity','{"a":1,}','[1,]','{"a" 1}','"bad\nstring"','{}{}'])assert.throws(()=>parse(text));
});
