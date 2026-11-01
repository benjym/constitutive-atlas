import assert from 'node:assert/strict';import {readFileSync,writeFileSync,existsSync} from 'node:fs';import {spawnSync} from 'node:child_process';
const here='docs/ingestion/duncan-chang-1970/integration-v1/portable-controls-v1';assert.ok(!existsSync(here+'/control-probes.json'));
const ref=JSON.parse(readFileSync(here+'/control-reference.json')),s=ref.specification;
const args=['--mode','run','--model',s.model,'--parameters',s.parameters.join(','),'--initial',s.initial.join(','),'--protocol',String(s.protocol),'--target',String(s.target),'--steps',String(s.steps),'--cycles',String(s.cycles),'--integration-settings','2e-10,0.000001,45,14,20000,11'];
const n=spawnSync('/private/tmp/atlas-duncan-portable-controls-v1/native/atlas_solver',args,{encoding:'utf8',timeout:30000});const response=JSON.parse(n.stdout);
writeFileSync(here+'/control-probes.json',JSON.stringify({args,exit_status:n.status,raw:n.stdout,response,expected_controls:ref.controls},null,2)+'\n');
assert.equal(n.status,0,n.stderr);assert.equal(response.ok,true);assert.equal(response.points.length,65);assert.deepEqual(response.points.map(p=>p.control),ref.controls);console.log('All65cyclic controls exactlymatch savedWasm; candidateordinaryrun succeeds');
