// Metadata-only companion: frozen bounded material worker does not allow atlas_describe.
import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {pathToFileURL} from 'node:url';
const request=JSON.parse(fs.readFileSync(0,'utf8'));
assert.equal(request.name,'atlas_describe');assert.deepEqual(request.types,[]);assert.deepEqual(request.args,[]);
const hash=b=>createHash('sha256').update(b).digest('hex');
const loader=fs.readFileSync(request.loader),wasm=fs.readFileSync(request.wasm);
assert.equal(hash(loader),request.loader_sha256);assert.equal(hash(wasm),request.wasm_sha256);
const create=(await import(pathToFileURL(request.loader))).default,module=await create({wasmBinary:wasm});
const stdout=module.ccall('atlas_describe','string',[],[]);assert.equal(typeof stdout,'string');JSON.parse(stdout);process.stdout.write(stdout);
