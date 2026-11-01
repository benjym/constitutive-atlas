import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const read=p=>readFileSync(new URL(p,import.meta.url),'utf8'),prior=read('./app-prior.js'),proposed=read('./app-proposed.js');
function extract(source){const text=source.match(/function axisRange\(values\)\{\n[\s\S]*?\n\}/)[0];return vm.runInNewContext(text+';axisRange;');}
const before=extract(prior),after=extract(proposed),range=(fn,x)=>Array.from(fn(x));
test('empty, zero and positive/negative constants retain exact existing padding',()=>{
 for(const values of [[],[0],[0,0],[48,48],[-24,-24],[.000001,.000001],[-10000,-10000]])assert.deepEqual(range(after,values),range(before,values));assert.deepEqual(range(after,[]),[0,1]);assert.deepEqual(range(after,[0,0]),[-.001,.001]);
});
test('actual-scale roundoff variation gets stable constant padding without modifying input values',()=>{
 for(const values of [[48,48+1e-14,48-1e-14],[-24,-24-1e-14,-24+1e-14],[0,Number.EPSILON,-Number.EPSILON]]){
  const saved=[...values],r=range(after,values),lo=Math.min(...values),hi=Math.max(...values),pad=Math.max(Math.abs(lo)*.05,.001);assert.deepEqual(r,[lo-pad,hi+pad]);assert.deepEqual(values,saved);assert(r[0]<=lo&&r[1]>=hi);const drawnSpread=211*(hi-lo)/(r[1]-r[0]);assert(drawnSpread<1e-8);assert(range(before,values)[1]-range(before,values)[0]<r[1]-r[0]);
 }
});
test('resolvable physical spans and normal time axes remain byte-for-byte equivalent results',()=>{
 for(const values of [[48,48+1e-12],[-24,-23.999999],[-1,1],[0,1e-10],[0,1,2,8],[3,4,11],[1000000000,1000000001],[1e-6,2e-6]])assert.deepEqual(range(after,values),range(before,values),values.join(','));
});
test('threshold boundary selects constant padding only at declared binary64 scale',()=>{
 const tolerance=64*Number.EPSILON;for(const span of [tolerance/2,tolerance]){const r=range(after,[0,span]);assert.deepEqual(r,[-.001,span+.001]);}const span=2*tolerance;assert.deepEqual(range(after,[0,span]),range(before,[0,span]));
});
test('whole source proposal changes only the near-constant condition; chart data flow stays exact',()=>{
 const needle='if(lo===hi){const pad=Math.max(Math.abs(lo)*.05,1e-3);',replacement='if(hi-lo<=64*Number.EPSILON*Math.max(1,Math.abs(lo),Math.abs(hi))){const pad=Math.max(Math.abs(lo)*.05,1e-3);';assert.equal(prior.replace(needle,replacement),proposed);const begin=prior.indexOf('function chart('),end=prior.indexOf('\nfunction renderCharts(',begin);assert(begin>=0&&end>begin);const nextBegin=proposed.indexOf('function chart('),nextEnd=proposed.indexOf('\nfunction renderCharts(',nextBegin);assert.equal(prior.slice(begin,end),proposed.slice(nextBegin,nextEnd));
});
