// Gate the dedicated Pages-relative package against independent scalar references.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8'));
const hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=read('engine/identity.json'),approval=read('power-creep-approval.json');
assert.equal(approval.status,'approved');assert.equal(approval.deployment_authorized,true);
assert.equal(identity.model_sha256,approval.definition.sha256);
assert.equal(hash('engine/'+identity.model+'.json'),identity.model_sha256);
assert.equal(hash('engine/power-creep.js'),identity.module_sha256);assert.equal(hash('engine/power-creep.wasm'),identity.wasm_sha256);
assert.equal(read('engine/models.json').sha256,identity.catalogue_hash);
const page=readFileSync(join(dir,'power-creep.html'),'utf8');
assert.ok(page.includes("'./engine/identity.json'")&&page.includes("'./engine/power-creep.js'"));
assert.ok(!page.includes("'/engine/"),'Root-relative runtime URL breaks Pages prefix');
assert.ok(page.includes('Approved scope')&&page.includes('Threshold switching is outside'));
const engine=await(await import(pathToFileURL(join(dir,'engine/power-creep.js')))).default();
for(const creep of [false,true]){
 const wire=[10,20,...Array.from({length:6},()=>[+creep,0,0]).flat()].join(',');
 const args=[identity.model,'20000000,12000000,1000000,0.002,1,0.001,3,1','1200000,900000,900000,0,0,0','0,0,0,0,0,0','0,0,0,0,0,0',wire,creep?'creep':'relaxation',0,1e-9,1e-12,1e-12,.1,200000,1e-10,40];
 const result=JSON.parse(engine.ccall('atlas_run_schedule','string',[...Array(7).fill('string'),...Array(8).fill('number')],args));
 assert.equal(result.ok,true,result.message);assert.equal(result.catalogue_hash,identity.catalogue_hash);
 const end=result.points.at(-1);assert.equal(end.time,10);
 if(creep){assert.ok(Math.abs(end.state[0]-1200000)<15);const f=.002*.3+.001*.3**3;assert.ok(Math.abs(end.strain[0]-10*f)<1e-10);}
 else {const a=3*12e6*.002/1e6,b=3*12e6*.001/1e18,q0=300000,e=Math.exp(-a*10),q=q0*e/Math.sqrt(1+b/a*q0*q0*(1-e*e));assert.ok(Math.abs(end.observables[7]-q)<15);assert.ok(Math.abs(end.strain[0])<1e-10);}
}
console.log('Power-creep package: identity, Pages-relative paths, analytical creep and relaxation passed');
