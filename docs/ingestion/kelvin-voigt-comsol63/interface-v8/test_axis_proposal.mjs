import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const read=p=>readFileSync(new URL(p,import.meta.url),'utf8'),prior=read('./app-prior.js'),proposed=read('./app-proposed.js'),originalSource=read('../interface-v7/app-prior.js');
function extract(source){const text=source.match(/function axisRange\(values[^\n]*\{\n[\s\S]*?\n\}/)[0];return vm.runInNewContext(text+';axisRange;');}
const original=extract(originalSource),after=extract(proposed),range=(fn,values,opt)=>Array.from(fn(values,opt));
test('all x domains retain exact original behavior including review large ±origin short-time counterexamples',()=>{
 for(const values of [[],[0],[48,48],[-24,-24],[0,Number.EPSILON],[48,48+1e-14],[1e9,1e9+1e-6],[-1e9,-1e9+1e-6],[3,11],[0,1e-10],[-1,1]])assert.deepEqual(range(after,values),range(original,values),JSON.stringify(values));
 for(const values of [[1e9,1e9+1e-6],[-1e9,-1e9+1e-6]]){const [lo,hi]=range(after,values);assert(hi-lo<2e-6);assert((values[1]-values[0])/(hi-lo)>.5,'time separation remains visible');}
});
test('y-only opt-in retains exact constants and uses stable existing padding for roundoff spans',()=>{
 for(const values of [[],[0],[48,48],[-24,-24],[.000001,.000001]])assert.deepEqual(range(after,values,true),range(original,values));
 for(const values of [[48,48+1e-14,48-1e-14],[-24,-24-1e-14],[0,Number.EPSILON,-Number.EPSILON]]){const before=[...values],lo=Math.min(...values),hi=Math.max(...values),pad=Math.max(Math.abs(lo)*.05,.001);assert.deepEqual(range(after,values,true),[lo-pad,hi+pad]);assert.deepEqual(values,before);}
});
test('normal y spans and declared threshold boundaries preserve intended distinction',()=>{
 for(const values of [[48,48+1e-12],[-24,-23.999999],[0,1e-10],[-1,1],[1e-6,2e-6]])assert.deepEqual(range(after,values,true),range(original,values));
 const threshold=64*Number.EPSILON;assert.deepEqual(range(after,[0,threshold],true),[-.001,threshold+.001]);assert.deepEqual(range(after,[0,2*threshold],true),range(original,[0,2*threshold]));
});
test('actual chart opts only y into padding; data arrays and all other chart source remain unchanged',()=>{
 const getChart=source=>source.slice(source.indexOf('function chart('),source.indexOf('\nfunction renderCharts(',source.indexOf('function chart(')));
 const oldChart=getChart(originalSource),newChart=getChart(proposed);assert.equal(oldChart.replace('[ymin,ymax]=axisRange(all.map(p=>p[1]));','[ymin,ymax]=axisRange(all.map(p=>p[1]),true);'),newChart);
 const opts=[],nodes=[];class Node{constructor(name,attrs){this.name=name;this.attrs=attrs;}append(...x){nodes.push(...x);}replaceChildren(){}}
 const svg=new Node('svg'),predicted=[[1e9,48],[1e9+1e-6,48+1e-14]],saved=structuredClone(predicted);
 const context=vm.createContext({predicted,$:()=>svg,svgNode:(name,attrs)=>new Node(name,attrs),numberLabel:String,axisRange:(values,flag)=>{opts.push(flag);return after(values,flag);}});vm.runInContext(newChart+';chart("test","seconds","kPa",predicted);',context);
 assert.deepEqual(opts,[undefined,true]);assert.deepEqual(predicted,saved);const line=nodes.find(n=>n.name==='polyline'),points=line.attrs.points.split(' ').map(s=>s.split(',').map(Number));assert(points[1][0]-points[0][0]>200);assert(Math.abs(points[1][1]-points[0][1])<1e-8);
});
