import test from 'node:test';
import assert from 'node:assert/strict';
import {ensembleFigure,createEnsemblePlot,plotlyAsset,plotlyVersion} from '../web/ensemble-plots.mjs';
const record={rows:[{axial_strain:0,q:0,volumetric_strain:0},{axial_strain:.02,q:250000,volumetric_strain:-.003}]};
const job=(id,change=null)=>({id,model:'test',label:change?'E = 2':'Baseline',change,result:{points:[{strain:[.01,-.002,-.002,0,0,0],state:[250000,100000,100000,0,0,0]},{strain:[.02,-.003,-.003,0,0,0],state:[300000,100000,100000,0,0,0]}]}});
const styles={test:{name:'A <model> & B',color:'#256d64'}};
test('physical channels, all observations and run identity survive Plotly mapping',()=>{
 const jobs=[job('baseline'),job('variation',{parameter:'E',value:2}),{...job('queued'),result:null}],before=JSON.stringify({record,jobs,styles});
 const stress=ensembleFigure(record,jobs,'stress','baseline',styles,3),volume=ensembleFigure(record,jobs,'volume','baseline',styles,3);
 assert.deepEqual(stress.data[0].x,[0,2]);assert.deepEqual(stress.data[0].y,[0,250]);assert.deepEqual(volume.data[0].y,[0,-.3]);
 assert.equal(stress.data.length,3);assert.equal(stress.data.at(-1).meta.jobId,'baseline');
 const baseline=stress.data.find(t=>t.meta.jobId==='baseline');assert.deepEqual(baseline.x,[1,2]);assert.deepEqual(baseline.y,[150,200]);
 assert.deepEqual(volume.data.find(t=>t.meta.jobId==='baseline').y,[.6,1.4000000000000001]);
 assert.match(baseline.uid,/^run-[a-f0-9]+$/);assert.equal(baseline.meta.jobId,'baseline');assert.equal(baseline.name,'A &lt;model&gt; &amp; B · Baseline');assert.equal(baseline.line.color,styles.test.color);assert.equal(baseline.line.width,3);assert.equal(baseline.line.simplify,false);
 assert.equal(stress.data.find(t=>t.meta.jobId==='variation').line.dash,'dash');assert.equal(stress.data[0].line.dash,'dot');assert.equal(stress.data[0].meta.jobId,null);
 assert.equal(stress.layout.uirevision,3);assert.equal(stress.config.scrollZoom,false);assert.equal(stress.config.displaylogo,false);assert.equal(stress.layout.showlegend,false);
 assert.match(stress.data[0].hovertemplate,/kPa/);assert.match(volume.data[0].hovertemplate,/Volumetric/);
 assert.equal(JSON.stringify({record,jobs,styles}),before);assert.throws(()=>ensembleFigure(record,jobs,'pore',null,styles,1),/channel/);
 assert.equal(plotlyVersion,'4.1.1');assert.equal(plotlyAsset,'vendor/plotly-basic-4.1.1.min.js');
});
test('stable trace IDs and view revision preserve interaction identity through selection changes',()=>{
 const jobs=[job('model:baseline'),job('model:E:1.0')],a=ensembleFigure(record,jobs,'stress','model:baseline',styles,1),b=ensembleFigure(record,jobs,'stress','model:E:1.0',styles,1),fresh=ensembleFigure(record,jobs,'stress','model:E:1.0',styles,2);
 assert.equal(a.layout.uirevision,b.layout.uirevision);assert.notEqual(b.layout.uirevision,fresh.layout.uirevision);
 assert.deepEqual(a.data.map(t=>t.uid).sort(),b.data.map(t=>t.uid).sort());assert.ok(a.data.slice(1).every(t=>/^run-[a-f0-9]+$/.test(t.uid)));assert.equal(new Set(a.data.map(t=>t.uid)).size,3);
 assert.deepEqual(ensembleFigure(record,[],'stress',null,styles,1).data.map(t=>t.uid),['measurements']);
});
test('async rendering coalesces updates, never overlaps Plotly calls and purges after disposal',async()=>{
 const frames=[],observers=[],calls=[],completions=[];let purged=0,active=0,max=0,loaded=0,click;
 const old={requestAnimationFrame:globalThis.requestAnimationFrame,cancelAnimationFrame:globalThis.cancelAnimationFrame,ResizeObserver:globalThis.ResizeObserver};
 globalThis.requestAnimationFrame=fn=>(frames.push(fn),frames.length);globalThis.cancelAnimationFrame=()=>{};
 globalThis.ResizeObserver=class{constructor(fn){observers.push(fn);}observe(){}disconnect(){}};
 const element={clientWidth:500,dataset:{},on:(name,fn)=>{assert.equal(name,'plotly_click');click=fn;}};
 const selected=[],api={react:async(el,data,layout)=>{active++;max=Math.max(max,active);calls.push({data,layout});await new Promise(r=>completions.push(r));active--;},purge:()=>purged++};
 const chart=createEnsemblePlot(element,{channel:'stress',onSelect:id=>selected.push(id),onError:error=>assert.fail(error),load:async()=>{loaded++;return api;}});
 try{
  chart.update(record,[job('a')],'a',styles,1);chart.update(record,[job('b')],'b',styles,1);assert.equal(loaded,0);
  const drawing=frames.shift()();await Promise.resolve();assert.equal(calls.length,1);assert.equal(calls[0].data.at(-1).meta.jobId,'b');
  chart.update(record,[job('c')],'c',styles,2);completions.shift()();await new Promise(r=>setTimeout(r,0));assert.equal(calls.length,2);assert.equal(calls[1].data.at(-1).meta.jobId,'c');assert.equal(max,1);assert.equal(loaded,1);
  completions.shift()();await drawing;assert.equal(element.dataset.ready,'true');
  click({points:[{data:{meta:{jobId:null}}}]});click({points:[{data:{meta:{jobId:'c'}}}]});assert.deepEqual(selected,['c']);
  element.clientWidth=320;observers[0]();const resizing=frames.shift()();await Promise.resolve();assert.equal(calls.at(-1).layout.width,320);
  chart.dispose();completions.shift()();await resizing;assert.equal(purged,1);
 }finally{Object.assign(globalThis,old);}
});
