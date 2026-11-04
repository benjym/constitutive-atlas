// Actual endpoint propagation/restart through one Wasm module.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [modulePath,pathsPath,outputPath]=process.argv.slice(2);
const create=(await import(pathToFileURL(resolve(modulePath)))).default;
const wasm=await create();const paths=JSON.parse(readFileSync(pathsPath,'utf8'));
const out=[];
for(const spec of paths){
 const repeats=[];
 for(let rep=0;rep<2;rep++){
  let z=spec.initial;const rows=[];
  for(const de of spec.increments){
   const args=[spec.model,spec.parameters.join(','),z.join(','),de.join(','),spec.integration_settings];
   const data=JSON.parse(wasm.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),args));
   rows.push(data);if(!data.ok)break;z=data.state;
  }
  repeats.push(rows);
 }
 out.push({id:spec.id,repeats});writeFileSync(outputPath,JSON.stringify(out,null,2)+'\n');
}
