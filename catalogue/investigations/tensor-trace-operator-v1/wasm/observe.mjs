import fs from 'node:fs';
import create from './atlas-trace.js';
const m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-trace.wasm',import.meta.url))});
console.log(m.ccall('atlas_trace_selftest','string',[],[]));
