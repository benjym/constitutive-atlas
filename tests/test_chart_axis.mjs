import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const path=process.env.ATLAS_CHART_APP||new URL('../web/app.js',import.meta.url),source=readFileSync(path,'utf8');
const rangeSource=source.match(/function axisRange\(values[^\n]*\{\n[\s\S]*?\n\}/)[0],axisRange=vm.runInNewContext(rangeSource+';axisRange;');
const range=(values,flag)=>Array.from(axisRange(values,flag));
function ordinaryRange(values){if(!values.length)return [0,1];const lo=Math.min(...values),hi=Math.max(...values),pad=lo===hi?Math.max(Math.abs(lo)*.05,.001):(hi-lo)*.07;return [lo-pad,hi+pad];}
test('chart axes retain empty zero ±constant and normal-span domains',()=>{
 for(const values of [[],[0],[0,0],[48,48],[-24,-24],[1e-6,1e-6],[-1,1],[48,48+1e-12],[0,1e-10],[1e-6,2e-6],[3,11]]){assert.deepEqual(range(values),ordinaryRange(values));assert.deepEqual(range(values,true),ordinaryRange(values));}
});
test('near-constant roundoff uses stable padding only with explicit y opt-in',()=>{
 for(const values of [[48,48+1e-14,48-1e-14],[-24,-24-1e-14],[0,Number.EPSILON,-Number.EPSILON]]){const saved=[...values],lo=Math.min(...values),hi=Math.max(...values),pad=Math.max(Math.abs(lo)*.05,.001);assert.deepEqual(range(values,true),[lo-pad,hi+pad]);assert.deepEqual(range(values),ordinaryRange(values));assert.deepEqual(values,saved);}
 const threshold=64*Number.EPSILON;assert.deepEqual(range([0,threshold],true),[-.001,threshold+.001]);assert.deepEqual(range([0,2*threshold],true),ordinaryRange([0,2*threshold]));
});
test('representable short physical-time spans at positive and negative large origins retain original x scale',()=>{
 for(const values of [[1e9,1e9+1e-6],[-1e9,-1e9+1e-6]]){assert.deepEqual(range(values),ordinaryRange(values));const [lo,hi]=range(values);assert(hi-lo<2e-6);assert((values[1]-values[0])/(hi-lo)>.5);}
});
test('actual shared chart opts only y into stable padding and keeps original input data',()=>{
 const begin=source.indexOf('function chart('),end=source.indexOf('\nfunction renderCharts(',begin);assert(begin>=0&&end>begin);const chartSource=source.slice(begin,end);
 for(const origin of [1e9,-1e9]){
  const opts=[],nodes=[];class Node{constructor(name,attrs){this.name=name;this.attrs=attrs;}append(...x){nodes.push(...x);}replaceChildren(){}}
  const svg=new Node('svg'),predicted=[[origin,48],[origin+1e-6,48+1e-14]],saved=structuredClone(predicted);
  const context=vm.createContext({predicted,$:()=>svg,svgNode:(name,attrs)=>new Node(name,attrs),numberLabel:String,axisRange:(values,flag)=>{opts.push(flag);return axisRange(values,flag);}});vm.runInContext(chartSource+';chart("test","seconds","kPa",predicted);',context);
  assert.deepEqual(opts,[undefined,true]);assert.deepEqual(predicted,saved);const line=nodes.find(n=>n.name==='polyline'),points=line.attrs.points.split(' ').map(s=>s.split(',').map(Number));assert(points[1][0]-points[0][0]>200);assert(Math.abs(points[1][1]-points[0][1])<1e-8);
 }
});
