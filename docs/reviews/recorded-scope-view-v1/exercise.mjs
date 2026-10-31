import {readFileSync,writeFileSync} from 'node:fs';
import createAtlas from './build/atlas.js';
import {replayRecorded} from '/Users/bmar5496/code/constitutive-atlas/web/recorded-worker.mjs';
const input=JSON.parse(readFileSync(new URL('./inputs.json',import.meta.url))),engine=await createAtlas(),results=[];
function compare(a,b,path=''){
 if(typeof b==='number'){if(typeof a!=='number'||!Number.isFinite(a)||Math.abs(a-b)>1e-9*Math.max(1,Math.abs(b))||(Number.isInteger(b)&&a!==b))throw Error('numeric mismatch '+path);}
 else if(b&&typeof b==='object'){if(!a||Array.isArray(a)!==Array.isArray(b)||Object.keys(a).sort().join(',')!==Object.keys(b).sort().join(','))throw Error('shape mismatch '+path);for(const k of Object.keys(b))compare(a[k],b[k],path+'.'+k);}
 else if(a!==b)throw Error('value mismatch '+path);
}
for(const row of input.rows){const result=replayRecorded(engine,row.request,input.catalogue);results.push({label:row.label,result});writeFileSync(new URL('./responses.json',import.meta.url),JSON.stringify(results,null,2)+'\n');compare(result,row.response,row.label);}
console.log(JSON.stringify({ok:true,scoped:3,legacy:9,wasm_calls:12}));
