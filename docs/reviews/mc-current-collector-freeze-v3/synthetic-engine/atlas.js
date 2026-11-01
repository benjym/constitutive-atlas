// Manufactured transport test double; no Wasm or constitutive equations.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=n=>JSON.parse(readFileSync(new URL('../'+n,import.meta.url),'utf8'));
const cat=read('catalogue.json'),requests=read('requests.json'),bad=read('rejection-requests.json').cases,frames=read('manufactured-frames.json').frames;
const args=q=>[q.model,q.parameters,q.initial,q.protocol,...(q.mode==='run-controls'?[q.controls_bits_csv,q.integration_settings]:[q.target,q.steps,q.cycles,q.integration_settings])];
export default async()=>({ccall(name,type,types,values){
 assert.equal(type,'string');assert.deepEqual(types,values.map(x=>typeof x==='number'?'number':'string'));
 if(name==='atlas_describe'){assert.deepEqual(values,[]);return readFileSync(new URL('../catalogue.json',import.meta.url),'utf8');}
 const controls=name==='atlas_run_controls_scope_with_settings';assert(controls||name==='atlas_run_scope_with_settings');
 const sameCsv=(a,b)=>typeof a==='string'&&typeof b==='string'&&a.split(',').length===b.split(',').length&&a.split(',').every((v,i)=>Object.is(Number(v),Number(b.split(',')[i])));
 const match=q=>q.mode===(controls?'run-controls':'run')&&args(q).every((v,i)=>[1,2,controls?5:7].includes(i)?sameCsv(v,values[i]):Object.is(v,values[i]));
 const invalid=bad.find(match);if(invalid)return JSON.stringify({ok:false,message:'manufactured rejection',points:[]});
 const index=requests.findIndex(match);assert(index>=0,'unrecognised synthetic call');return JSON.stringify(frames[index].result);
}});
