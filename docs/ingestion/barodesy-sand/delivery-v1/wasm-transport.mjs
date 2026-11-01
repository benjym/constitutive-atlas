// Persistent production C ABI transport. No constitutive mathematics.
import {createInterface} from 'node:readline';
import {pathToFileURL} from 'node:url';
const loader = (await import(pathToFileURL(process.argv[2]))).default;
const engine = await loader();
for await (const line of createInterface({input:process.stdin})) {
  try {
    const q = JSON.parse(line);
    let fn, types, args;
    if(q.mode==='describe') {fn='atlas_describe'; types=[]; args=[];}
    else if(q.mode==='evaluate') {
      fn='atlas_evaluate'; types=Array(5).fill('string');
      args=[q.model,q.parameters,q.initial,q.initial,q.strain];
    } else if(q.mode==='integrate') {
      fn='atlas_integrate_with_settings'; types=Array(5).fill('string');
      args=[q.model,q.parameters,q.initial,q.strain,q.settings];
    } else if(q.mode==='run') {
      fn='atlas_run_with_settings';types=['string','string','string','number','number','number','number','string'];
      args=[q.model,q.parameters,q.initial,q.protocol,q.target,q.steps,q.cycles,q.settings];
    } else throw new Error('Unknown request mode');
    process.stdout.write(JSON.stringify({raw:engine.ccall(fn,'string',types,args)})+'\n');
  } catch(error) {process.stdout.write(JSON.stringify({transport_error:String(error)})+'\n');}
}
