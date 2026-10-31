import fs from 'node:fs';
import create from './atlas-expression.js';
const m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-expression.wasm',import.meta.url))});
console.log(m.ccall('atlas_expression','string',[],[]));
