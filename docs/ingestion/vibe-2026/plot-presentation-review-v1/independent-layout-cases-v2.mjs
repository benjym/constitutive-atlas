import assert from 'node:assert/strict';
import {formatTickLabels,tickLeftMargin,layoutHorizontalTickLabels} from '../../../../web/plot-labels.mjs';
const cases=[[1,1+Number.EPSILON,1+2*Number.EPSILON,1+3*Number.EPSILON,1+4*Number.EPSILON],[5110.12,5110.09,5110.06,5110.03,5110],[.72500004,.72500002,.725,.72499998,.72499996],[0,250,500,750,1000],[Number.MIN_VALUE,2*Number.MIN_VALUE,3*Number.MIN_VALUE,4*Number.MIN_VALUE,5*Number.MIN_VALUE],[-Number.MAX_VALUE,0,Number.MAX_VALUE],[.725,.725,.725,.725,.725]];
let checks=0,minVisible=Infinity;
for(const values of cases){
  const labels=formatTickLabels(values);
  for(const left of [62,100,171,192,tickLeftMargin(labels)]){
    const positions=labels.map((_,i)=>left+i*(454-left)/(labels.length-1)),saved=JSON.stringify({labels,positions});
    const layout=layoutHorizontalTickLabels(labels,positions);
    assert.equal(JSON.stringify({labels,positions}),saved);
    assert.deepEqual(layoutHorizontalTickLabels(labels,positions),layout);
    const ranges=[];
    for(let i=0;i<layout.length;i++){
      const item=layout[i];assert.ok(item.text===''||item.text===labels[i]);
      if(!item.text)continue;
      const width=item.text.length*7,start=positions[i]-(item.anchor==='start'?0:item.anchor==='end'?width:width/2);
      assert.ok(start>=12&&start+width<=468);
      ranges.push([start,start+width]);
    }
    ranges.sort((a,b)=>a[0]-b[0]);
    assert.ok(ranges.length>0);
    for(let i=1;i<ranges.length;i++)assert.ok(ranges[i][0]>=ranges[i-1][1]+8);
    minVisible=Math.min(minVisible,ranges.length);checks++;
  }
}
assert.deepEqual(layoutHorizontalTickLabels([],[]),[]);
assert.equal(layoutHorizontalTickLabels(['123'],[62])[0].text,'123');
for(const pair of [[['x'],[]],[[1],[62]],[['x'],[NaN]],[['x'],new Array(1)],[new Array(1),[62]]])assert.throws(()=>layoutHorizontalTickLabels(...pair),TypeError);
console.log(JSON.stringify({status:'pass',layout_cases:checks,min_visible_labels:minVisible,checks:['original clipping witness bounded','nonoverlapping displayed labels','unchanged text values and positions','determinism','empty/singleton/invalid inputs'],compiled_calls:0}));
