// Opaque scheduled C-ABI collector; does not assess numerical acceptance.
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const [study,build,out]=process.argv.slice(2);
const create=(await import(pathToFileURL(join(build,'terracotta-study.js')))).default;
const engine=await create();
const rows=[];
for(const row of JSON.parse(readFileSync(join(study,'requests.json'))).records){
 const r=row.request,s={relative_tolerance:1e-6,absolute_scale_fraction:1e-9,minimum_step:1e-12,maximum_step:1e6,maximum_substeps:20000,nonlinear_tolerance:1e-10,maximum_iterations:40,...r.solver};
 const csv=a=>a.join(',');
 const wire=r.segments.flatMap(p=>[p.duration,p.samples,...p.controls.flatMap(c=>[+(c.quantity==='stress'),{hold:0,rate:1,target:2}[c.kind],c.value??0])]);
 const args=[r.model,csv(r.parameters),csv(r.initial),csv(r.initial_strain),csv(r.initial_strain_rate),csv(wire),r.segments.map(p=>p.id).join(','),r.start_time,s.relative_tolerance,s.absolute_scale_fraction,s.minimum_step,s.maximum_step,s.maximum_substeps,s.nonlinear_tolerance,s.maximum_iterations];
 try{rows.push({...row,raw:engine.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],args),wire:args});}
 catch(error){rows.push({...row,collector_error:String(error),wire:args});}
 writeFileSync(join(out,'journal.json'),JSON.stringify(rows,null,2)+'\n');
}
console.log(`Collected ${rows.length} complete schedule responses in one persistent Wasm module.`);
