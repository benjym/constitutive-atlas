import fs from 'node:fs';
import create from './atlas-solver-rollback.js';
const m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-solver-rollback.wasm',import.meta.url))});
console.log(m.ccall('atlas_solver_rollback','string',[],[]));
