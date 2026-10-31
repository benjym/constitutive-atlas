import fs from 'node:fs';
import create from './atlas-expression-context.js';
const m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-expression-context.wasm',import.meta.url))});
console.log(m.ccall('atlas_expression_context','string',[],[]));
