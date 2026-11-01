// Required bounded public-preset regression. Importing this module executes no artifacts.
import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
import * as c from '../web/implicit-path-contract.mjs';
import {createBoundedModule,boundedCall} from '../docs/ingestion/lade-duncan-1975/fused-linear-v1/wasm-bounded-v1/runner.mjs';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const PACKET='docs/ingestion/lade-duncan-1975/atlas-integration-v1/public-ci-v1/';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const read=name=>c.parseRunJSON(fs.readFileSync(name,'utf8'));
const save=(name,value)=>fs.writeFileSync(name,c.stringifyRun(value)+'\n');
export function sourceErrors(result,reference){
 const point=result.points.at(-1);
 return {relative_axial_stress:Math.abs(point.state[0]-reference.axial_stress)/reference.axial_stress,absolute_radial_strain:Math.abs(point.strain[1]-reference.radial_strain),relative_work_using_1Pa_floor:Math.abs(point.state[7]-reference.wp)/Math.max(1,Math.abs(reference.wp))};
}
export function run(buildPath,outputPath,identityPath){
 const build=path.resolve(buildPath),output=path.resolve(outputPath),raw=output+'.raw',statusPath=output+'.status.json';
 for(const name of [output,raw,statusPath])assert(!fs.existsSync(name),'Refusing to overwrite retained evidence: '+name);
 fs.mkdirSync(path.dirname(output),{recursive:true});fs.mkdirSync(raw);
 const report={kind:'implicit-path-public-presets-v1',status:'running',scope:'two actual bounded public presets and complete recomputed replay; no scientific admission or actual-browser approval',rows:[],calls:[],inputs:{}};
 const persist=()=>{save(output,report);save(statusPath,{status:report.status,phase:report.phase??null,error:report.error??null,completed_rows:report.rows.length,completed_calls:report.calls.filter(x=>x.status==='passed').length});};
 const phase=name=>{report.phase=name;persist();};
 persist();
 try{
  phase('verify prospective inputs');
  const policyPath=path.join(ROOT,PACKET,'POLICY.json'),policy=read(policyPath);report.inputs[PACKET+'POLICY.json']=sha(fs.readFileSync(policyPath));
  assert.equal(policy.kind,'implicit-path-public-preset-policy-v1');assert(c.equal(policy.presets,['dense','loose']));assert.equal(policy.timeout_ms,120000);
  for(const [name,expected] of Object.entries(policy.files)){assert(!path.isAbsolute(name)&&!name.split('/').includes('..'),'Unsafe policy input');const bytes=fs.readFileSync(path.join(ROOT,name));assert.equal(sha(bytes),expected,'Frozen public preset dependency changed: '+name);report.inputs[name]=expected;}
  const identity=read(path.resolve(identityPath));c.identityCheck(identity);
  const catPath=fs.existsSync(path.join(build,'generated/models.json'))?path.join(build,'generated/models.json'):path.join(build,'models.json');
  const catalogueBytes=fs.readFileSync(catPath),catalogue=c.parseRunJSON(catalogueBytes.toString('utf8'));
  assert.equal(catalogue.sha256,identity.catalogue_hash);assert.equal(sha(catalogueBytes),identity.catalogue_file_sha256);
  assert(c.equal(catalogue.models.map(m=>m.id),policy.catalogue_ids),'Full four-model catalogue differs');
  const definitionPath=path.join(ROOT,policy.definition),definition=fs.readFileSync(definitionPath);assert.equal(sha(definition),c.modelSha256);assert(c.equal(catalogue.models[0],c.parseRunJSON(definition.toString('utf8'))));
  const loader=path.join(build,'lade-domain.mjs'),wasm=path.join(build,'lade-domain.wasm');
  assert.equal(sha(fs.readFileSync(loader)),identity.module_sha256);assert.equal(sha(fs.readFileSync(wasm)),identity.wasm_sha256);
  report.binding={identity,identity_file_sha256:sha(fs.readFileSync(path.resolve(identityPath))),catalogue_file_sha256:sha(catalogueBytes),build};persist();
  const references=read(path.join(ROOT,policy.references)),bounds=read(path.join(ROOT,policy.triaxial_policy)).native_final_reference_bounds;
  assert(c.equal(bounds,policy.source_final_bounds),'Source acceptance bounds changed');
  const selections=policy.presets.map(name=>{const matches=references.cases.filter(x=>x.set===name&&x.reference.axial_strain===policy.target);assert.equal(matches.length,1,'Missing or duplicate source reference');assert.equal(matches[0].passed,true);return {name,reference:matches[0].reference};});
  phase('atlas_describe');
  const metadataDir=path.join(raw,'metadata');fs.mkdirSync(metadataDir);
  const metadata={name:'atlas_describe',result:'string',types:[],args:[],loader,wasm,loader_sha256:identity.module_sha256,wasm_sha256:identity.wasm_sha256};
  const record={request:metadata,state:'running',timeout_ms:120000};save(path.join(metadataDir,'manifest.json'),{records:[record]});
  const observed=boundedCall(path.join(ROOT,PACKET,'describe-worker.mjs'),metadata);
  for(const kind of ['stdout','stderr']){const dest=path.join(metadataDir,'0.'+kind);fs.writeFileSync(dest,observed[kind]);record[kind]={path:dest,sha256:sha(observed[kind])};}
  Object.assign(record,{state:'finished',status:observed.status,signal:observed.signal,error:observed.error,elapsed_ms:observed.elapsed_ms});save(path.join(metadataDir,'manifest.json'),{records:[record]});
  assert(!observed.error&&!observed.signal&&observed.status===0&&observed.elapsed_ms<120000,'Metadata worker failed/expired; inspect raw metadata manifest');
  assert(c.equal(c.parseRunJSON(observed.stdout.toString('utf8')),catalogue),'Embedded full atlas_describe catalogue differs');
  report.calls.push({name:'metadata',phase:'describe',status:'passed',raw_manifest:path.join(metadataDir,'manifest.json')});persist();
  const engine=createBoundedModule(build,path.join(raw,'material'));
  for(const {name,reference} of selections){
   const controls=c.preset(name);assert.equal(controls.protocol,1);assert.equal(controls.target,policy.target);assert.equal(controls.steps,policy.steps);assert.equal(controls.cycles,0);assert(c.equal(controls.settings,c.settings));
   const row={name,controls,reference,phases:[]};report.rows.push(row);persist();let replay=null;
   for(const kind of ['first','replay']){
    phase(name+':'+kind);const current=kind==='first'?controls:replay.controls,args=c.request(current,identity),call={name,phase:kind,function:c.api,args,status:'running',raw_manifest:path.join(raw,'material','manifest.json')};report.calls.push(call);persist();
    const stdout=engine.ccall(c.api,'string',c.types,args),result=c.parseRunJSON(stdout);call.stdout_sha256=sha(Buffer.from(stdout));
    c.verifyResult(result,identity,current);assert.equal(result.ok,true,name+': '+result.message);
    const errors=sourceErrors(result,reference);assert(Object.entries(bounds).every(([key,bound])=>Number.isFinite(errors[key])&&errors[key]<=bound),'Source final-reference bound failed: '+c.stringifyRun(errors));
    row.phases.push({phase:kind,args,result,source_errors:errors});
    if(kind==='first'){const exported=c.exportRun(current,result,identity),text=c.stringifyRun(exported);row.export_path=path.join(raw,name+'-run.json');fs.writeFileSync(row.export_path,text+'\n');replay=c.importRun(text,identity);assert(c.equal(replay.controls,controls));}
    else c.verifyReplay(result,replay.result);
    call.status='passed';persist();
   }
  }
  assert(c.equal(report.rows.map(r=>r.name),['dense','loose']));assert.equal(report.calls.length,5);assert(report.rows.every(r=>r.phases.length===2));
  report.status='passed';phase('complete');console.log('PASS: Dense/Loose400 public presets, original source bounds and complete recomputed replay.');return report;
 }catch(error){report.status='failed';report.error={name:error.name,message:error.message,stack:error.stack};for(const call of report.calls)if(call.status==='running')call.status='failed';persist();throw error;}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2);if(args.length!==3)throw Error('usage: node tools/test_implicit_path_public_presets.mjs BUILD OUTPUT IDENTITY');run(...args);
}
