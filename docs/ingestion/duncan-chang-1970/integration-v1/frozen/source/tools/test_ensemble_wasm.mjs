// Serial execution only. Acceptance tolerances are frozen in POLICY.md.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {makeStudy,defaultConfigurations,exportStudy,importStudy,stable} from '../web/ensemble.mjs';
import {replayRecorded} from '../web/recorded-worker.mjs';
const options={};for(let i=2;i<process.argv.length;i+=2){assert.ok(['--wasm','--experiment','--output'].includes(process.argv[i]));options[process.argv[i]]=process.argv[i+1];}
assert.ok(options['--wasm']&&options['--experiment']&&options['--output']);assert.ok(!existsSync(options['--output']),'Preserve previous reports. Choose a new output path.');
const wasm=resolve(options['--wasm']),catalogue=JSON.parse(readFileSync(join(dirname(wasm),'generated/models.json'))),record=JSON.parse(readFileSync(options['--experiment']));
const createAtlas=(await import(pathToFileURL(wasm))).default,engine=await createAtlas();
assert.equal(stable(JSON.parse(engine.ccall('atlas_describe','string',[],[]))),stable(catalogue));
const study=makeStudy(record,catalogue,defaultConfigurations(catalogue)),checks=[];
let passed=true;
for(const job of study.jobs){
 if(job.status==='rejected')continue;
 try{job.result=replayRecorded(engine,job.specification,catalogue);job.status=job.result.ok?'completed':'stopped';job.message=job.result.message||'';}
 catch(error){job.status='error';job.message=String(error);}
 if(job.model==='linear-elastic'){
  try{
   assert.equal(job.status,'completed');assert.equal(job.result.points.length,95);
   let maxStress=0,maxStrain=0;const {E,nu}=job.parameters;
   for(let i=0;i<95;i++){
    const r=record.rows[i],p=job.result.points[i],dr=r.radial_effective_stress-103720,ea=r.axial_strain;
    const stress=103720+E*ea+2*nu*dr,volume=(1-2*nu)*ea+2*(1+nu)*(1-2*nu)*dr/E;
    const actualVolume=p.strain.slice(0,3).reduce((a,b)=>a+b,0);maxStress=Math.max(maxStress,Math.abs(p.state[0]-stress));maxStrain=Math.max(maxStrain,Math.abs(actualVolume-volume));
    assert.ok(Math.abs(p.state[0]-stress)<=.05+1e-7*Math.abs(stress),'Independent axial stress mismatch at '+i);
    assert.ok(Math.abs(actualVolume-volume)<=1e-9+1e-7*Math.abs(volume),'Independent volume mismatch at '+i);
   }
   checks.push({id:job.id,status:'passed',max_stress_error_Pa:maxStress,max_volume_strain_error:maxStrain});
  }catch(error){passed=false;checks.push({id:job.id,status:'failed',error:String(error)});}
 }
}
let roundtrip;try{const document=exportStudy(study,catalogue,record),replay=importStudy(JSON.stringify(document),catalogue,record);assert.equal(replay.jobs.length,15);assert.ok(replay.jobs.every(j=>j.status==='queued'&&j.result===null));roundtrip='passed';}catch(error){passed=false;roundtrip=String(error);}
const hash=path=>createHash('sha256').update(readFileSync(path)).digest('hex');
writeFileSync(options['--output'],JSON.stringify({status:passed?'passed':'failed',module_sha256:hash(wasm),wasm_sha256:hash(wasm.replace(/\.js$/,'.wasm')),experiment_sha256:hash(options['--experiment']),checks,roundtrip,study},null,2)+'\n');
console.log(JSON.stringify({status:passed?'passed':'failed',checks,outcomes:study.jobs.map(j=>({id:j.id,status:j.status,message:j.message}))},null,2));if(!passed)process.exitCode=1;
