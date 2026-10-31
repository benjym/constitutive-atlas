import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [build,out]=process.argv.slice(2);
const create=(await import(pathToFileURL(build+'/control-trace.js'))).default;
const m=await create({wasmBinary:fs.readFileSync(build+'/control-trace.wasm')});
const raw=m.ccall('atlas_trace','string',[],[]);
fs.writeFileSync(out,raw+'\n');
