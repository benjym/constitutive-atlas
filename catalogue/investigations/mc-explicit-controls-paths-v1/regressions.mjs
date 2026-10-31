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
const newer=await(await import(pathToFileURL(resolve(wasmdir,'atlas-preview.js')))).default();
const older=await(await import(pathToFileURL(resolve(oldwasmdir,'atlas.js')))).default();
const catalogue=JSON.parse(readFileSync(resolve(oldwasmdir,'generated/models.json'),'utf8'));
const expected=['barodesy-clay-2017','barodesy-sand','drucker-prager','hypoplastic-clay-2005','hypoplastic-clay-2013','hypoplastic-sand-igs97','hypoplastic-sand-vw96','linear-elastic','modified-cam-clay'];assert.deepEqual(catalogue.models.map(x=>x.id).sort(),expected);
const next=JSON.parse(readFileSync(resolve(wasmdir,'generated/models.json'),'utf8'));assert.equal(next.models.length,10);
for(const model of catalogue.models)assert.deepEqual(next.models.find(x=>x.id===model.id),model);
const records=[];let count=0;
const physical=r=>{const {elapsed_ms,catalogue_hash,...rest}=r;return rest;};
for(const model of catalogue.models)for(const protocol of [0,1,2,3,4]){
 const initial=model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]).join(','),target=protocol===3?10000:.002,steps=64,cycles=protocol===3?1:0;
 for(const backend of ['native','wasm']){
  const args=[model.id,'',initial,protocol,target,steps,cycles,''];
  function call(old){if(backend==='wasm')return(old?older:newer).ccall('atlas_run_with_settings','string',['string','string','string','number','number','number','number','string'],args);
   const r=spawnSync(old?oldnative:native,['--model',model.id,'--initial',initial,'--protocol',String(protocol),'--target',String(target),'--steps',String(steps),'--cycles',String(cycles),'--integration-settings',''],{encoding:'utf8',timeout:30000});assert.equal(r.status,0,r.stdout+r.stderr);return r.stdout;}
  const oldRaw=call(true),newRaw=call(false);records.push({model:model.id,protocol,backend,old_raw:oldRaw,new_raw:newRaw});writeFileSync(outfile,JSON.stringify({baselineBindings,records})+'\n');
  const old=JSON.parse(oldRaw),fresh=JSON.parse(newRaw);assert.equal(old.ok,true);assert.equal(fresh.ok,true);assert.equal(old.catalogue_hash,catalogue.sha256);assert.equal(fresh.catalogue_hash,next.sha256);assert.deepEqual(physical(fresh),physical(old));count++;
 }
}
assert.equal(count,90);writeFileSync(outfile,JSON.stringify({passed:true,backend_runs:count,baselineBindings,records})+'\n');console.log('90 valid legacy runs unchanged; only catalogue identity and elapsed time excluded.');
