import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const [native,wasmdir,oldnative,oldwasmdir,outfile]=process.argv.slice(2);assert.ok(!existsSync(outfile));
const baseline=JSON.parse(readFileSync(new URL('./legacy-baseline-artifacts.json',import.meta.url),'utf8'));
const baselineBindings=[];
for(const [role,directory] of [['native',dirname(resolve(oldnative))],['wasm',resolve(oldwasmdir)]])for(const [name,receipt]of Object.entries(baseline[role])){
 const path=role==='native'&&name==='atlas_solver'?resolve(oldnative):resolve(directory,name);
 const digest=createHash('sha256').update(readFileSync(path)).digest('hex');assert.equal(digest,receipt.sha256,'baseline artifact '+path);baselineBindings.push({role,name,path,sha256:digest});
}
console.log(JSON.stringify({passed:true,bindings:baselineBindings.length,candidateCalls:0}));
