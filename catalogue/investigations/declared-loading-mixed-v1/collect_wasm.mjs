import fs from 'node:fs';import {pathToFileURL}from'node:url';import path from'node:path';
const [engineFile,requestFile]=process.argv.slice(2),create=(await import(pathToFileURL(path.resolve(engineFile)))).default;
const engine=await create({wasmBinary:fs.readFileSync(engineFile.replace(/\.js$/,'.wasm'))});
const requests=JSON.parse(fs.readFileSync(requestFile));
const descriptor=JSON.parse(engine.ccall('atlas_describe','string',[],[]));
const rows=requests.map(r=>({id:r.id,result:JSON.parse(engine.ccall('atlas_run_controls_scope_with_settings','string',['string','string','string','number','string','string'],r.wasm_arguments))}));
process.stdout.write(JSON.stringify({descriptor,rows})+'\n');
