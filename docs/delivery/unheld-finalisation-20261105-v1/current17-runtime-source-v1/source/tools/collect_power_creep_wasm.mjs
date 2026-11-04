// All calls share one Wasm instance, including failures, recovery and replay.
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const [studyPath, modulePath, destination] = process.argv.slice(2);
if (!studyPath || !modulePath || !destination) throw Error('study, module, destination required');
const study = JSON.parse(await readFile(studyPath, 'utf8'));
const absoluteModule = resolve(modulePath);
const create = (await import(pathToFileURL(absoluteModule))).default;
const wasm = await create();
await mkdir(destination, {recursive:true});
const moduleSha = createHash('sha256').update(await readFile(absoluteModule)).digest('hex');
const wasmSha = createHash('sha256').update(await readFile(absoluteModule.replace(/\.js$/,'.wasm'))).digest('hex');
for (const request of study.requests) {
  const output = wasm.ccall(request.function, 'string', request.types, request.args);
  const data = JSON.parse(output);
  await writeFile(resolve(destination, request.id+'.stdout'), output);
  await writeFile(resolve(destination, request.id+'.stderr'), '');
  await writeFile(resolve(destination, request.id+'.process.json'), JSON.stringify({
    returncode:data.ok ? 0 : 1, role:'same-instance Wasm ccall; status derived from response',
    function:request.function, args:request.args, module_sha256:moduleSha, wasm_sha256:wasmSha
  }, null, 2)+'\n');
}
console.log(`Retained ${study.requests.length} same-instance Wasm responses.`);
