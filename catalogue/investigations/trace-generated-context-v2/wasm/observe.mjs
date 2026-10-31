import fs from 'node:fs';
import create from './atlas-trace-context.js';
const m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-trace-context.wasm',import.meta.url))});
console.log(m.ccall('atlas_trace_context','string',[],[]));
