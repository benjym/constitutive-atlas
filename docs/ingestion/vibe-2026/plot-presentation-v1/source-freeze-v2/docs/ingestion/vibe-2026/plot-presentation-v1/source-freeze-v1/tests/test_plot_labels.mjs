import test from 'node:test';
import assert from 'node:assert/strict';
import {formatTickLabels,tickLeftMargin} from '../web/plot-labels.mjs';

function assess(values){
  const before=values.slice(),labels=formatTickLabels(values);
  assert.deepEqual(values,before,'formatting must not modify coordinates');
  assert.equal(labels.length,values.length);
  assert.equal(new Set(labels).size,new Set(values).size,'every distinct tick needs its own label');
  const sorted=[...new Set(values)].sort((a,b)=>a-b);
  let spacing=Infinity;for(let i=1;i<sorted.length;i++)spacing=Math.min(spacing,sorted[i]-sorted[i-1]);
  const tolerance=Number.isFinite(spacing)?spacing*.05:0;
  labels.forEach((label,i)=>{assert.ok(Number.isFinite(Number(label)));assert.ok(Math.abs(Number(label)-values[i])<=tolerance,`${label} must represent its tick within 5% of spacing`);});
  const left=tickLeftMargin(labels);
  assert.ok(left>=62&&454-left>200,'retain useful width in the 480-unit chart');
  // Conservative seven-unit glyph estimate, with ten-unit tick gap. Scaling
  // to a 315px mobile chart preserves this positive clearance from the SVG edge.
  labels.forEach(label=>assert.ok((left-10-label.length*7)*315/480>0));
  return labels;
}

test('small stress changes at a large offset remain distinct',()=>{
  const values=[5110.12,5110.09,5110.06,5110.03,5110];
  assert.equal(new Set(values.map(v=>Number(v.toPrecision(3)).toString())).size,1,'original three-digit failure witness');
  assert.equal(new Set(assess(values)).size,5);
});
test('small void-ratio changes retain enough decimals',()=>{
  const values=[.72500004,.72500002,.725,.72499998,.72499996];
  assert.equal(new Set(values.map(v=>Number(v.toPrecision(3)).toString())).size,1);
  assert.equal(new Set(assess(values)).size,5);
});
test('seconds, signs and ordinary scales remain readable',()=>{
  assert.deepEqual(assess([0,250,500,750,1000]),['0','250','500','750','1000']);
  assess([-2,-1,0,1,2]);assess([-5110,-5110.03,-5110.06,-5110.09,-5110.12]);
});
test('small absolute quantities do not collapse to zero',()=>{
  const labels=assess([1e-14,2e-14,3e-14,4e-14,5e-14]);
  assert.ok(labels.every(s=>s!=='0'));
});
test('roundoff at a zero tick is range relative',()=>{
  const labels=assess([-2,-1,1e-16,1,2]);assert.equal(labels[2],'0');
});
test('scientific notation keeps extreme scale labels compact',()=>{
  assert.equal(assess([1e20,2e20,3e20,4e20,5e20])[0],'1e20');
  assess([1e-200,2e-200,3e-200,4e-200,5e-200]);
  assess([Number.MIN_VALUE,2*Number.MIN_VALUE,3*Number.MIN_VALUE,4*Number.MIN_VALUE,5*Number.MIN_VALUE]);
  assess([-Number.MAX_VALUE,0,Number.MAX_VALUE]);
});
test('adjacent representable large-offset values round trip distinctly',()=>{
  assess([1,1+Number.EPSILON,1+2*Number.EPSILON,1+3*Number.EPSILON,1+4*Number.EPSILON]);
  assess([1e12,1e12+.000244140625,1e12+.00048828125]);
});
test('empty, constant, duplicate and signed-zero ticks are deterministic',()=>{
  assert.deepEqual(formatTickLabels([]),[]);assert.equal(tickLeftMargin([]),62);
  assert.deepEqual(formatTickLabels([.725,.725]),['0.725','0.725']);
  assert.deepEqual(formatTickLabels([-0,0]),['0','0']);
  assert.deepEqual(formatTickLabels([1,2,1]),['1','2','1']);
});
test('invalid and sparse inputs fail explicitly',()=>{
  for(const value of [null,{},[NaN],[Infinity],[-Infinity],['1'],[true],new Array(2)])assert.throws(()=>formatTickLabels(value),TypeError);
  for(const value of [null,{},[1],new Array(2)])assert.throws(()=>tickLeftMargin(value),TypeError);
});
