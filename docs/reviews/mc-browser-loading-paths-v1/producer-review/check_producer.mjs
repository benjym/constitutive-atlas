import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createLoading,controlBits,controlFromBits} from '../../../../catalogue/investigations/browser-loading-provenance-v1/web/loading.mjs';
const root=new URL('../',import.meta.url);
const input=JSON.parse(readFileSync(new URL('source-input.json',root),'utf8')),requests=JSON.parse(readFileSync(new URL('requests.json',root),'utf8'));
let controls=0,deltas=0;
for(const req of requests){
 const expected=input.paths.find(p=>p.id===req.id);assert.ok(expected);const l=createLoading(req);assert.deepEqual(l.controls_bits,expected.controls_bits);controls+=l.controls_bits.length;
 for(let i=1;i<l.controls_bits.length;i++){assert.equal(controlBits(controlFromBits(l.controls_bits[i])-controlFromBits(l.controls_bits[i-1])),expected.control_delta_bits[i-1]);deltas++;}
}
const report={passed:true,requests:requests.length,exact_controls:controls,exact_deltas:deltas,compiled_calls:0,scope:'producer identity/input binding only; material and browser integration separate'};
writeFileSync(new URL('./producer-binding.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
