import {resultSeries} from './ensemble.mjs';

export const plotlyAsset='vendor/plotly-basic-4.1.1.min.js';
export const plotlyVersion='4.1.1';
let library;
function loadPlotly(){
 library??=new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src=new URL('./'+plotlyAsset,import.meta.url).href;script.async=true;
  script.onload=()=>window.Plotly?.version===plotlyVersion?resolve(window.Plotly):reject(Error('Plotly version differs from the packaged charts.'));
  script.onerror=()=>reject(Error('Charts could not load. Reload the page to try again.'));
  document.head.append(script);
 });
 return library;
}
const escape=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
export function ensembleFigure(record,jobs,channel,selected,styles,viewRevision){
 if(!['stress','volume'].includes(channel))throw Error('Unknown ensemble plot channel.');
 const stress=channel==='stress',value=stress?'q: %{y:.3f} kPa':'Volumetric strain: %{y:.3f}%',hovertemplate='Axial strain: %{x:.3f}%<br>'+value+'<extra>%{fullData.name}</extra>';
 const measured=record.rows.map(r=>[r.axial_strain*100,stress?r.q/1000:r.volumetric_strain*100]);
 const trace=(points,attributes)=>({type:'scatter',mode:'lines',x:points.map(p=>p[0]),y:points.map(p=>p[1]),hovertemplate,connectgaps:false,...attributes});
 const data=[trace(measured,{uid:'measurements',name:'Measurements',meta:{jobId:null},line:{color:'#59605c',width:2,dash:'dot',simplify:false}})];
 // Draw the selected curve last, retaining stable trace IDs as runs arrive.
 for(const job of [...jobs].sort((a,b)=>Number(a.id===selected)-Number(b.id===selected))){
  const points=resultSeries(job,channel);if(!points.length)continue;
  const active=job.id===selected,style=styles[job.model];
  data.push(trace(points,{uid:job.id,name:escape((style?.name||job.model)+' · '+job.label),meta:{jobId:job.id},line:{color:style?.color||'#375595',width:active?3:job.change?1.3:2,dash:job.change?'dash':'solid',simplify:false},opacity:active?1:job.change?.45:.8}));
 }
 return {data,layout:{autosize:true,height:360,margin:{l:66,r:16,t:40,b:58},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{family:'Arial, sans-serif',size:12,color:'#59605c'},showlegend:false,hovermode:'closest',dragmode:'zoom',clickmode:'event',uirevision:viewRevision,xaxis:{title:{text:'Axial strain (%)',standoff:12},autorange:true,zeroline:false,gridcolor:'#e2e6dc',automargin:true},yaxis:{title:{text:stress?'Deviator stress q (kPa)':'Volumetric strain (%)',standoff:10},autorange:true,zerolinecolor:'#c6cec1',gridcolor:'#e2e6dc',automargin:true}},config:{displaylogo:false,displayModeBar:true,responsive:false,scrollZoom:false,modeBarButtonsToRemove:['select2d','lasso2d','sendChartToCloud'],toImageButtonOptions:{format:'png',filename:'opara-txcd100-'+channel,scale:2}}};
}

// Coalesce fast queue notifications and serialize Plotly updates. An old render
// may finish, but the newest figure is always drawn next. No engine is involved.
export function createEnsemblePlot(element,{channel,onSelect,onError,load=loadPlotly}){
 let latest=null,pending=false,running=false,frame=null,disposed=false,Plotly=null,bound=false,failed=false;
 const clicked=event=>{const id=event.points?.find(p=>p.data?.meta?.jobId)?.data.meta.jobId;if(id)onSelect(id);};
 async function draw(){
  frame=null;if(disposed||running||failed||!pending||!element.clientWidth)return;
  running=true;
  try{
   Plotly??=await load();
   while(pending&&!disposed&&element.clientWidth){
    pending=false;const figure=ensembleFigure(...latest);figure.layout.width=element.clientWidth;
    await Plotly.react(element,figure.data,figure.layout,figure.config);
    if(!bound&&!disposed){element.on('plotly_click',clicked);bound=true;}
    if(!disposed)element.dataset.ready='true';
   }
  }catch(error){if(!disposed){failed=true;onError(error);}}
  finally{running=false;if(disposed&&Plotly)Plotly.purge(element);}
 }
 function schedule(){pending=true;if(!running&&frame===null&&!disposed&&!failed)frame=requestAnimationFrame(draw);}
 const observer=new ResizeObserver(()=>{if(latest&&element.clientWidth)schedule();});observer.observe(element);
 return {
  update(record,jobs,selected,styles,viewRevision){latest=[record,jobs,channel,selected,styles,viewRevision];schedule();},
  dispose(){disposed=true;observer.disconnect();if(frame!==null)cancelAnimationFrame(frame);if(Plotly&&!running)Plotly.purge(element);}
 };
}
