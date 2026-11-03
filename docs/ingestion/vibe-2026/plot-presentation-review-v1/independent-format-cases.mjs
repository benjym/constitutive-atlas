// Independent pure floating-point corner cases; no DOM or compiled material.
import assert from 'node:assert/strict';
import {formatTickLabels,tickLeftMargin} from '../../../../web/plot-labels.mjs';
const buffer=new ArrayBuffer(8),view=new DataView(buffer);
function next(value,direction){
  if(value===0)return direction>0?Number.MIN_VALUE:-Number.MIN_VALUE;
  view.setFloat64(0,value);let bits=view.getBigUint64(0);
  bits+=(value>0)===(direction>0)?1n:-1n;
  view.setBigUint64(0,bits);return view.getFloat64(0);
}
const cases=[];
for(const start of [Number.MAX_VALUE,-Number.MAX_VALUE,Number.MIN_VALUE,-Number.MIN_VALUE,1,-1,1e-300,-1e-300,1e300,-1e300,.725,5110]){
  const direction=start===Number.MAX_VALUE||start===-Number.MIN_VALUE?-1:1;
  const values=[start];for(let i=0;i<4;i++){const value=next(values.at(-1),direction);if(Number.isFinite(value))values.push(value);}
  cases.push(values);
}
for(let exponent=-320;exponent<=300;exponent+=10){
  const base=10**exponent;
  for(const sign of [-1,1])cases.push([1,2,3,4,5].map(i=>sign*base*i));
}
for(const values of cases){
  const retained=values.slice(),labels=formatTickLabels(values),parsed=labels.map(Number);
  assert.deepEqual(values,retained);
  assert.equal(new Set(labels).size,new Set(values).size);
  assert.ok(parsed.every(Number.isFinite));
  // Each label must identify its own coordinate more closely than any other
  // coordinate on the same axis, including adjacent representable extremes.
  for(let i=0;i<values.length;i++)for(let j=0;j<values.length;j++)if(i!==j&&values[i]!==values[j]){
    assert.ok(Math.abs(parsed[i]-values[i])<Math.abs(parsed[i]-values[j]));
  }
  assert.ok(tickLeftMargin(labels)<454);
}
console.log(JSON.stringify({status:'pass',independent_cases:cases.length,finite_tick_values:cases.reduce((n,a)=>n+a.length,0),checks:['distinct labels','input preservation','finite parsed labels','nearest-coordinate identification','positive chart width'],compiled_calls:0}));
