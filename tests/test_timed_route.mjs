import test from 'node:test';
import assert from 'node:assert/strict';
import {timedLaboratoryRoute} from '../web/timed-route.mjs';
test('only explicit published timed routes are exposed',()=>{
 assert.equal(timedLaboratoryRoute({timed_laboratory:'retired.html'}),null);
 assert.equal(timedLaboratoryRoute({public_timed_laboratory:true,timed_laboratory:'power-creep.html'}),'power-creep.html');
 for(const route of ['../escape.html','/escape.html','https://x.test/a.html','a.html?x','a.html#x',''])assert.throws(()=>timedLaboratoryRoute({public_timed_laboratory:true,timed_laboratory:route}),/Unsafe/);
});
