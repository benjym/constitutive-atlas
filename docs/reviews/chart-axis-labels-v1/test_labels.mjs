import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('./',import.meta.url);
const src=fs.readFileSync(new URL('candidate-chart.js',root),'utf8');
const prior=fs.readFileSync(new URL('prior-chart.js',root),'utf8');
const candidate=vm.runInNewContext(src+';numberLabel');
const old=vm.runInNewContext(prior+';numberLabel');
assert.equal(old(-1e-12),'0'); // Existing loss of sign/value retained as witness.
let cases=0,maxLength=0;
for(let exponent=-300;exponent<=300;exponent+=3){
 for(const factor of [-9.99,-1.23,-1,1,1.23,9.99]){
  const value=factor*10**exponent,label=candidate(value);
  assert.notEqual(Number(label),0);assert.equal(Math.sign(Number(label)),Math.sign(value));
  assert.ok(Math.abs(Number(label)/value-1)<0.005,{value,label});
  maxLength=Math.max(maxLength,label.length);assert.ok(label.length<=10,{value,label});cases++;
 }
}
assert.equal(candidate(0),'0');assert.equal(candidate(-0),'0');
assert.equal(candidate(-1e-12),'-1e-12');
assert.equal(candidate(0.00123),'0.00123');
assert.equal(candidate(100),'100');
const samples=JSON.parse(fs.readFileSync(new URL('saved-points.json',root)));
for(const pts of Object.values(samples))for(const p of pts)for(const v of [p.time,p.state[0]/1000,p.strain[0]*100,p.strain_rate[0]]){
 if(v!==null&&v!==0)assert.notEqual(Number(candidate(v)),0);
}
console.log(JSON.stringify({passed:true,signed_exponent_cases:cases,maximum_label_characters:maxLength,prior_tiny_value_loss_reproduced:true,saved_output_value_labels_checked:true}));
