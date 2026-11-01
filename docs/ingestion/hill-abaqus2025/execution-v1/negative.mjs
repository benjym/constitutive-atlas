import fs from 'node:fs';import {pathToFileURL} from 'node:url';import {execFileSync} from 'node:child_process';import assert from 'node:assert/strict';import path from 'node:path';
const b=path.dirname(new URL(import.meta.url).pathname),engine=await(await import(pathToFileURL(process.argv[2]))).default(),spec=JSON.parse(fs.readFileSync(path.join(b,'negative-requests.json'))),settings='1e-11,1e-6,60,0,1,20',model='hill-abaqus2025-perfect-be';
const csv=x=>x.join(','),request=c=>[model,csv(c.parameters),csv(c.initial),csv(c.strain),settings],call=c=>JSON.parse(engine.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),request(c)));
const ref=JSON.parse(fs.readFileSync(path.join(b,'references.json'))).cases[2],good={parameters:ref.parameters,initial:ref.initial,strain:ref.increments[0]},before=call(good),rows=[];
assert.equal(before.ok,true);
for(const c of spec.cases){let native;try{native=JSON.parse(execFileSync(process.argv[3],['--mode','integrate','--model',model,'--parameters',csv(c.parameters),'--initial',csv(c.initial),'--strain',csv(c.strain),'--integration-settings',settings],{encoding:'utf8'}));}catch(e){native=JSON.parse(e.stdout);}
 const wasm=call(c);assert.equal(native.ok,false);assert.equal(wasm.ok,false);assert.deepEqual(native.state,c.initial);assert.deepEqual(wasm.state,c.initial);const recovered=call(good);assert.deepEqual(recovered,before);rows.push({id:c.id,native,wasm,recovered});}
fs.writeFileSync(path.join(b,'negative-results.json'),JSON.stringify({passed:true,rows},null,2)+'\n');
