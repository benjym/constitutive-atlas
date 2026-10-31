import fs from 'node:fs';import {pathToFileURL} from 'node:url';
const [dir,build]=process.argv.slice(2);const r=JSON.parse(fs.readFileSync(dir+'/request.json'));
const create=(await import(pathToFileURL(build+'/atlas-barodesy-preview.js'))).default;
const m=await create({wasmBinary:fs.readFileSync(build+'/atlas-barodesy-preview.wasm')});
process.stdout.write(m.ccall('atlas_run','string',['string','string','string','number','number','number','number'],[r.model,r.parameters,r.initial,r.protocol,r.target,r.steps,r.cycles]));
