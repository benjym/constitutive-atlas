import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {laboratoryPresentation,laboratoryPoreView} from '../web/laboratory-view.mjs';
import {runLaboratoryRequest} from '../web/laboratory-worker.mjs';
import {laboratoryExample} from '../web/state-contract.mjs';
import {comparisonSeries} from '../web/experiments.mjs';
const {catalogue,rows}=JSON.parse(readFileSync(0,'utf8')),app=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
const render=app.slice(app.indexOf('function renderCharts(){'),app.indexOf('function catalogueCards(){'));
const labels=app.slice(app.indexOf('function updateScopeLabels(){'),app.indexOf('function populate('));
for(const row of rows){
 const s=row.request,r=row.response,m=catalogue.models.find(m=>m.id===s.model),p=laboratoryPresentation(m),calls=[];
 assert.deepEqual(runLaboratoryRequest({ccall(name){calls.push(name);return JSON.stringify(name==='atlas_describe'?catalogue:r);}},s,catalogue),r);
 assert.deepEqual(calls,['atlas_describe','atlas_run_scope_with_settings']);
 assert.equal(p.scope,s.stress_scope);assert.match(p.radialLabel,new RegExp(s.stress_scope));assert.match(p.axes.path.xLabel,new RegExp(s.stress_scope));
 if(p.scope==='total'){assert.ok(p.protocols.every(s=>!/[uU]ndrained|[dD]rained/.test(s)));assert.equal(p.axes.path.xLabel.includes('′'),false);}
 const pore=laboratoryPoreView(r,m,s.protocol),reconstructed=r.pore_pressure.availability==='reconstructed';
 assert.equal(pore.points.length,reconstructed?r.points.length:0);assert.match(pore.caption,reconstructed?/Reconstructed/:/Unavailable/);
 const elements=new Map(),charts=[];
 const get=id=>{if(!elements.has(id))elements.set(id,{value:'',checked:false,dataset:{},attributes:{},setAttribute(k,v){this.attributes[k]=v;},closest(){return {querySelector(){return {};}};}});return elements.get(id);};
 get('protocol').value=String(s.protocol);get('cycles').value='0';get('protocol').options=[0,1,2,3,4].map(value=>({value}));
 const ranges=new Map();const document={querySelector(key){if(!ranges.has(key))ranges.set(key,{setAttribute(k,v){this[k]=v;}});return ranges.get(key);}};
 vm.runInNewContext(labels+';updateScopeLabels();',{model:()=>m,laboratoryPresentation,$:get,document});
 assert.equal(get('confinement-label').textContent,p.radialLabel);assert.equal(get('path-title').textContent,p.pathTitle);assert.equal(get('path-chart').attributes['aria-label'],p.pathAria);assert.equal(ranges.get('[data-for="confinement"]')['aria-label'],p.radialLabel+' slider');
 vm.runInNewContext(render+';renderCharts();',{model:()=>m,laboratoryPresentation,laboratoryPoreView,$:get,lastSpec:s,currentResult:r,experiment:null,describeExperiment(){},comparisonSeries,chart(...args){charts.push(args);}});
 const poreChart=charts.find(c=>c[0]==='pore-chart');assert.deepEqual(poreChart[3],pore.points);assert.equal(get('pore-caption').textContent,pore.caption);
 assert.equal(charts.find(c=>c[0]==='path-chart')[1],p.axes.path.xLabel);
 const example=laboratoryExample(m);assert.deepEqual(example.initial,m.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]));
}
const total=rows.find(r=>r.request.stress_scope==='total'),m=catalogue.models.find(m=>m.id===total.request.model),legacy={...total.request};delete legacy.response_contract;delete legacy.stress_scope;let called=false;
assert.throws(()=>runLaboratoryRequest({ccall(){called=true;}},legacy,catalogue));assert.equal(called,false);
const wrong=structuredClone(total.response);wrong.points[1].u=0;assert.throws(()=>laboratoryPoreView(wrong,m,total.request.protocol));
const effective=rows.find(r=>r.label==='scoped-elastic-2'),em=catalogue.models.find(m=>m.id===effective.request.model),old=structuredClone(effective.response);delete old.api_version;delete old.stress;delete old.pore_pressure;
assert.equal(laboratoryPoreView(old,em,2).points.length,old.points.length);old.points[1].u=null;assert.throws(()=>laboratoryPoreView(old,em,2));
assert.throws(()=>laboratoryPoreView(old,m,2));
assert.ok(laboratoryPoreView(null,m,2).caption.includes('Unavailable'));
process.stdout.write(JSON.stringify({model_protocol_cases:rows.length,actual_render_handler:true,actual_label_handler:true,legacy_total_preflight:true}));
