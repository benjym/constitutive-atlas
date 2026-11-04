// Actual copied Wasm, all12 state +6 stress against frozen independent references.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const dir=resolve(process.argv[2]||'web/dist'),root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(readFileSync(join(dir,p),'utf8')),hash=p=>createHash('sha256').update(readFileSync(join(dir,p))).digest('hex');
const identity=read('engine-sls/identity.json'),approval=read('sls-approval.json'),review=read('sls-agent-review.json');
assert.equal(approval.status,'approved');assert.equal(review.status,'accepted');
assert.equal(identity.model_sha256,approval.definition.sha256);
for(const [file,key] of [['engine-sls/'+identity.model+'.json','model_sha256'],['engine-sls/sls.js','module_sha256'],['engine-sls/sls.wasm','wasm_sha256'],['sls-approval.json','approval_sha256'],['sls-agent-review.json','review_sha256']])assert.equal(hash(file),identity[key]);
assert.equal(read('engine-sls/models.json').sha256,identity.catalogue_hash);
for(const [file,expected] of Object.entries(read('engine-sls/package-manifest.json')))assert.equal(hash(file),expected);
const page=readFileSync(join(dir,'sls.html'),'utf8');assert.ok(page.includes("'./engine-sls/sls.js'"));assert.ok(!page.includes("'/engine"));assert.ok(page.includes('Experimental overlays unavailable'));
const engine=await(await import(pathToFileURL(join(dir,'engine-sls/sls.js')))).default();
const cases=JSON.parse(readFileSync(join(root,'docs/ingestion/sls-comsol63/execution-v1/cases.json'))).cases;
let comparisons=0;
for(const id of ['relax-schedule','creep-schedule']){
 const c=cases.find(c=>c.id===id),r=JSON.parse(engine.ccall(c.call,'string',c.types,c.args));
 assert.equal(r.ok,true,r.message);assert.equal(r.catalogue_hash,identity.catalogue_hash);assert.equal(r.points.length,c.references.length+1);
 for(let i=0;i<r.points.length;i++){const p=r.points[i],ref=c.references.find(ref=>ref.time===p.time);assert.equal(p.time,ref.time);assert.equal(p.state.length,12);assert.equal(p.observables.length,6);
 for(let j=0;j<12;j++){assert.ok(Math.abs(p.state[j]-ref.state[j])<=(j<6?3e-8:1),`${id}: state ${i}/${j}`);comparisons++;}
 for(let j=0;j<6;j++){assert.ok(Math.abs(p.observables[j]-ref.stress[j])<=1,`${id}: stress ${i}/${j}`);comparisons++;}}
 const replay=JSON.parse(engine.ccall(c.call,'string',c.types,c.args));assert.deepEqual(replay,r);
}
console.log(JSON.stringify({ok:true,cases:2,fullStateAndStressComparisons:comparisons,identity,exactReplay:true},null,2));
