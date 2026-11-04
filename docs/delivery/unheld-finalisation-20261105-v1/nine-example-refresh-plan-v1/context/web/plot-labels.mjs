// Shared chart presentation only: finite tick values retain their numeric range.
export function formatTickLabels(values){
  if(!Array.isArray(values)||Array.from(values).some(value=>typeof value!=='number'||!Number.isFinite(value)))throw new TypeError('Finite numeric ticks required');
  if(!values.length)return [];
  const unique=[...new Set(values)].sort((a,b)=>a-b);
  let spacing=Infinity;
  for(let i=1;i<unique.length;i++)spacing=Math.min(spacing,unique[i]-unique[i-1]);
  const finiteSpacing=Number.isFinite(spacing)?spacing:0;
  // Suppress roundoff at a mathematically zero tick, relative to this axis;
  // genuine small-valued axes retain their own scale rather than becoming zero.
  const ticks=values.map(value=>Math.abs(value)<finiteSpacing*1e-12?0:value);
  for(let precision=1;precision<=17;precision++){
    const labels=ticks.map(value=>{
      const rounded=Number(value.toPrecision(precision)),plain=rounded.toString();
      if(!Number.isFinite(rounded))return plain;
      const [mantissa,exponent]=rounded.toExponential(precision-1).split('e');
      const scientific=Number(mantissa).toString()+'e'+Number(exponent);
      return plain.length<=6?plain:(scientific.length<plain.length?scientific:plain);
    });
    if(new Set(labels).size!==unique.length)continue;
    if(labels.every((label,i)=>Number.isFinite(Number(label))&&Math.abs(Number(label)-values[i])<=finiteSpacing*.05))return labels;
  }
  // Seventeen significant digits round-trip every finite JavaScript number.
  return ticks.map(value=>value.toString());
}

export function tickLeftMargin(labels){
  if(!Array.isArray(labels)||Array.from(labels).some(label=>typeof label!=='string'))throw new TypeError('Text tick labels required');
  return Math.max(62,24+labels.reduce((longest,label)=>Math.max(longest,label.length),0)*7);
}

// Keep long horizontal labels inside the SVG and show only a nonoverlapping
// subset. Grid lines, tick positions and data coordinates are unchanged.
export function layoutHorizontalTickLabels(labels,positions){
  if(!Array.isArray(labels)||!Array.isArray(positions)||labels.length!==positions.length||Array.from(labels).some(label=>typeof label!=='string')||Array.from(positions).some(x=>typeof x!=='number'||!Number.isFinite(x)))throw new TypeError('Text labels and finite positions required');
  const result=labels.map((text,i)=>({text:'',anchor:i===0?'start':i===labels.length-1?'end':'middle'})),kept=[];
  const order=labels.length>1?[0,labels.length-1,...labels.slice(1,-1).map((_,i)=>i+1)]:labels.map((_,i)=>i);
  for(const i of order){
    const width=labels[i].length*7,anchor=result[i].anchor;
    const left=positions[i]-(anchor==='end'?width:anchor==='middle'?width/2:0),right=left+width;
    if(left<12||right>468||kept.some(range=>left<range[1]+8&&right>range[0]-8))continue;
    result[i].text=labels[i];kept.push([left,right]);
  }
  return result;
}
