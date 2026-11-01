function axisRange(values){
  if(!values.length)return [0,1];let lo=Infinity,hi=-Infinity;for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}if(lo===hi){const pad=Math.max(Math.abs(lo)*.05,1e-3);lo-=pad;hi+=pad;}else{const pad=(hi-lo)*.07;lo-=pad;hi+=pad;}return [lo,hi];
}
function numberLabel(v){if(Math.abs(v)<1e-10)return '0';return Number(v.toPrecision(3)).toString();}
function svgNode(name,attributes,text){const n=document.createElementNS('http://www.w3.org/2000/svg',name);for(const[k,v]of Object.entries(attributes))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function chart(id,xLabel,yLabel,predicted,measured=[],emptyMessage){
  const svg=$(id);svg.replaceChildren();svg.append(svgNode('title',{},yLabel+' versus '+xLabel));
  const left=62,top=27,w=392,h=211,all=[...predicted,...measured].filter(a=>a.every(Number.isFinite));
  const [xmin,xmax]=axisRange(all.map(p=>p[0])),[ymin,ymax]=axisRange(all.map(p=>p[1]));
  const x=v=>left+(v-xmin)/(xmax-xmin)*w,y=v=>top+h-(v-ymin)/(ymax-ymin)*h;
  for(let i=0;i<=4;i++){
    const yy=top+i*h/4,xx=left+i*w/4;
    svg.append(svgNode('line',{x1:left,y1:yy,x2:left+w,y2:yy,stroke:'#e6e9df','stroke-dasharray':'3 4'}),svgNode('text',{x:left-10,y:yy+4,'text-anchor':'end'},numberLabel(ymax-i*(ymax-ymin)/4)),svgNode('text',{x:xx,y:top+h+19,'text-anchor':'middle'},numberLabel(xmin+i*(xmax-xmin)/4)));
  }
  svg.append(svgNode('text',{x:left+w/2,y:282,'text-anchor':'middle',class:'axis-label'},xLabel.length>56?xLabel.slice(0,53)+'…':xLabel),svgNode('text',{x:12,y:top-12,class:'axis-label'},yLabel.length>60?yLabel.slice(0,57)+'…':yLabel));
  if(!all.length)svg.append(svgNode('text',{x:left+w/2,y:top+h/2,'text-anchor':'middle'},(emptyMessage||(id==='source-chart'?'No paired observations for these channels':'Preparing response…'))));
  if(predicted.length)svg.append(svgNode('polyline',{points:predicted.map(([a,b])=>`${x(a)},${y(b)}`).join(' '),fill:'none',stroke:'#bc643e','stroke-width':2,'stroke-linejoin':'round'}));
  const stride=Math.max(1,Math.ceil(measured.length/350));measured.filter((_,i)=>i%stride===0).forEach(([a,b])=>svg.append(svgNode('circle',{cx:x(a),cy:y(b),r:2,fill:'#547a95',opacity:.6,class:'experiment-point'})));
  if(predicted.length){
    const marker=svgNode('circle',{r:4,fill:'#bc643e',stroke:'#fff','stroke-width':2,visibility:'hidden'}),label=svgNode('text',{x:left+8,y:top+12,visibility:'hidden'});svg.append(marker,label);
    svg.onpointermove=e=>{const box=svg.getBoundingClientRect(),px=(e.clientX-box.left)/box.width*480;let nearest=predicted[0];for(const pt of predicted)if(Math.abs(x(pt[0])-px)<Math.abs(x(nearest[0])-px))nearest=pt;marker.setAttribute('cx',x(nearest[0]));marker.setAttribute('cy',y(nearest[1]));marker.setAttribute('visibility','visible');label.textContent=`${numberLabel(nearest[0])}, ${numberLabel(nearest[1])}`;label.setAttribute('visibility','visible');};
    svg.onpointerleave=()=>{marker.setAttribute('visibility','hidden');label.setAttribute('visibility','hidden');};
  }
}
