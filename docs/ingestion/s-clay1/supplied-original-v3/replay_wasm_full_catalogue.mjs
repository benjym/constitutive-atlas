import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const here=path.dirname(new URL(import.meta.url).pathname),root=path.resolve(here,'../../../..');
const build=path.join(root,'.local/sclay1-sixteen/wasm');
const factory=(await import(pathToFileURL(path.join(build,'atlas.js')))).default;
const mod=await factory({wasmBinary:fs.readFileSync(path.join(build,'atlas.wasm'))});
const out=path.join(here,'integration-v1/wasm-replay');fs.mkdirSync(out);
const inputs=[];
for(const f of ['native-v1/calls.jsonl','native-v2/calls.jsonl'])for(const l of fs.readFileSync(path.join(here,f),'utf8').trim().split('\n'))inputs.push(JSON.parse(l));
inputs.push(...JSON.parse(fs.readFileSync(path.join(here,'native-interpreter-calls.json'))));
const log=fs.openSync(path.join(out,'calls.jsonl'),'wx');let calls=0,worst=0,comparisons=0;
function difference(a,b,scale){const d=Math.abs(a-b)/scale;if(!Number.isFinite(d)||d>2e-8)throw Error(`parity ${d}>2e-8 atcall${calls}`);worst=Math.max(worst,d);comparisons++;}
function state(a,b){if(a.length!==b.length)throw Error('layout');for(let i=0;i<a.length;i++)difference(a[i],b[i],i<6||i===13?20000:1);}
try{
 const describe=JSON.parse(mod.ccall('atlas_describe','string',[],[]));const native=JSON.parse(fs.readFileSync(path.join(here,'native-description.json')));if(JSON.stringify(describe.models.find(x=>x.id==='s-clay1'))!==JSON.stringify(native.models.find(x=>x.id==='s-clay1')))throw Error('metadata');
 for(const input of inputs){
  calls++;const args={};for(let i=1;i<input.argv.length;i+=2)args[input.argv[i]]=input.argv[i+1];
  const id=args['--model'],params=args['--parameters']??'',z=args['--initial'],mode=args['--mode'];let actual;
  if(mode==='integrate'){
   const setting=args['--integration-settings'];actual=JSON.parse(setting===undefined?mod.ccall('atlas_integrate','string',['string','string','string','string'],[id,params,z,args['--strain']]):mod.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],[id,params,z,args['--strain'],setting]));
  }else if(mode==='evaluate')actual=JSON.parse(mod.ccall('atlas_evaluate','string',['string','string','string','string','string'],[id,params,args['--current'],z,args['--strain']]));
  else if(mode==='run')actual=JSON.parse(mod.ccall('atlas_run','string',['string','string','string','number','number','number','number'],[id,params,z,Number(args['--protocol']),Number(args['--target']),Number(args['--steps']),Number(args['--cycles']??0)]));
  else throw Error('unhandledmode');
  fs.writeSync(log,JSON.stringify({call:calls,argv:input.argv,actual})+'\n');
  const expected=JSON.parse(input.stdout);if(actual.ok!==expected.ok)throw Error('outcome mismatch');
  if(actual.state&&expected.state)state(actual.state,expected.state);
  if(actual.values)state(actual.values,expected.values);
  if(actual.points){if(actual.points.length!==expected.points.length)throw Error('points');for(let i=0;i<actual.points.length;i++){const a=actual.points[i],b=expected.points[i];state(a.state,b.state);for(const key of ['p','q','q_signed','u'])if(typeof a[key]==='number')difference(a[key],b[key],20000);}}
 }
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({ok:true,calls,comparisons,maximum_scaled_difference:worst,wasm_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(build,'atlas.wasm'))).digest('hex'),scope:'Exact native requests, reference refinement/analytical/covariance/rollback/default/invalid/regression and50interpreterresiduals replayed through actualWasm'},null,2)+'\n');
}catch(e){fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({ok:false,calls,comparisons,maximum_scaled_difference:worst,error:e.stack},null,2)+'\n');throw e;}finally{fs.closeSync(log);}
