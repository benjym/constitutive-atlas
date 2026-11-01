#!/usr/bin/env node
// Persistent generic C ABI transport. Shared Python orchestrator owns identical requests.
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
const args=process.argv.slice(2),get=k=>{let i=args.indexOf(k);return i<0?null:args[i+1];};
if(!get('--engine'))throw Error('--engine required');
if(!args.includes('--worker')){
 if(!get('--output'))throw Error('--output required');
 const cmd=['-B',path.join(path.dirname(fileURLToPath(import.meta.url)),'run_native.py'),'--wasm-engine',path.resolve(get('--engine')),'--output',get('--output')];
 for(let i=0;i<args.length;i++)if(args[i]==='--case')cmd.push('--case',args[i+1]);
 const child=spawn('python3',cmd,{stdio:'inherit'});child.on('exit',code=>process.exit(code??1));
}else{
 const factory=(await import(pathToFileURL(path.resolve(get('--engine'))).href)).default;
 const engine=await factory({print:x=>process.stderr.write(String(x)+'\n'),printErr:x=>process.stderr.write(String(x)+'\n')});
 const csv=v=>v.join(',');
 process.stdout.write(JSON.stringify({ready:true})+'\n');
 for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})){
  try{
   const r=JSON.parse(line),common=[r.model,csv(r.parameters),csv(r.initial)];let fn,types,values;
   if(r.mode==='integrate'||r.mode==='linearize'){
    fn=r.mode==='integrate'?'atlas_integrate_with_settings':'atlas_linearize_with_settings';types=Array(5).fill('string');values=[...common,csv(r.strain),csv(r.settings)];
   }else if(r.mode==='run-controls'){
    fn='atlas_run_controls_scope_with_settings';types=['string','string','string','number','string','string'];values=[...common,r.protocol,r.controls_bits.join(','),csv(r.settings)];
   }else if(r.mode==='run'){
    fn='atlas_run_scope_with_settings';types=['string','string','string','number','number','number','number','string'];values=[...common,r.protocol,r.target,r.steps,0,csv(r.settings)];
   }else throw Error('unsupported generic request '+r.mode);
   const raw=engine.ccall(fn,'string',types,values);process.stdout.write(JSON.stringify({raw})+'\n');
  }catch(e){process.stdout.write(JSON.stringify({raw:'',error:String(e.stack||e)})+'\n');}
 }
}
