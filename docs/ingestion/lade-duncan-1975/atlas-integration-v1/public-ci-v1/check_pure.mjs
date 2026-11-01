// Pure syntax/import and policy/code-binding proof. Never invokes run or a worker.
import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {spawnSync} from 'node:child_process';import {createHash} from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../../..'),checks=[];
const hash=b=>createHash('sha256').update(b).digest('hex');
const test=(name,fn)=>{try{fn();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,error:String(error)});}};
for(const name of ['tools/test_implicit_path_public_presets.mjs',path.relative(root,path.join(here,'describe-worker.mjs')),path.relative(root,fileURLToPath(import.meta.url))])test('syntax '+name,()=>{const p=spawnSync(process.execPath,['--check',path.join(root,name)],{encoding:'utf8',timeout:10000});assert.equal(p.status,0,p.stderr);});
const module=await import('../../../../../tools/test_implicit_path_public_presets.mjs');
test('import exports functions without requiring artifacts',()=>{assert.equal(typeof module.run,'function');assert.equal(typeof module.sourceErrors,'function');});
const reference={axial_stress:100,radial_strain:-.002,wp:2};
test('source-error equations and 1Pa work floor',()=>{assert.deepEqual(module.sourceErrors({points:[{state:[101,0,0,0,0,0,0,2.02],strain:[0,-.0019]}]},reference),{relative_axial_stress:.01,absolute_radial_strain:Math.abs(-.0019+.002),relative_work_using_1Pa_floor:Math.abs(2.02-2)/2});assert.equal(module.sourceErrors({points:[{state:[100,0,0,0,0,0,0,.25],strain:[0,-.002]}]},{...reference,wp:0}).relative_work_using_1Pa_floor,.25);});
const policy=JSON.parse(fs.readFileSync(path.join(here,'POLICY.json'),'utf8'));
for(const [name,expected] of Object.entries(policy.files))test('frozen dependency '+name,()=>assert.equal(hash(fs.readFileSync(path.join(root,name))),expected));
const output={scope:'pure syntax/module import/error algebra and static pins; no artifact/module/Wasm/material calls',passed:checks.every(x=>x.passed),checks};fs.writeFileSync(path.join(here,'pure-results.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));process.exitCode=output.passed?0:1;
