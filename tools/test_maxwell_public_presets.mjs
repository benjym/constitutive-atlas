// Exercise the actual public control/transport contract against reviewed Wasm.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {modelId,modelSha256,presetNames,preset,request,types,verifyResult,exportRun,importRun,verifyReplay} from '../web/maxwell-atlas-contract.mjs';

const [buildPath,outputPath,identityPath]=process.argv.slice(2);
if(!buildPath||!outputPath||!identityPath)throw Error('usage: node tools/test_maxwell_public_presets.mjs BUILD OUTPUT IDENTITY');
const build=resolve(buildPath);
const catalogue=JSON.parse(readFileSync(resolve(build,'generated/models.json'),'utf8'));
const module=(await import(pathToFileURL(resolve(build,'maxwell.js')))).default;
const engine=await module();
const observations=[];
const capture=(name,phase,fn,args,types)=>{
 const stdout=engine.ccall(fn,'string',types,args);
 observations.push({name,phase,function:fn,args,stdout});
 writeFileSync(outputPath+'.raw.json',JSON.stringify(observations,null,2)+'\n');
 return JSON.parse(stdout);
};
assert.deepEqual(capture('metadata','describe','atlas_describe',[],[]),catalogue);
const identity=JSON.parse(readFileSync(identityPath,'utf8'));
assert.equal(identity.model,modelId);
assert.equal(identity.model_sha256,modelSha256);
assert.equal(identity.catalogue_hash,catalogue.sha256);
const rows=[];
for(const name of presetNames){
 const controls=preset(name),args=request(controls,identity);
 const result=capture(name,'first','atlas_run_schedule',args,types);
 verifyResult(result,identity,controls);
 const saved=exportRun(controls,result,identity);
 const replay=importRun(JSON.stringify(saved),identity);
 const second=capture(name,'replay','atlas_run_schedule',request(replay.controls,identity),types);
 verifyResult(second,identity,replay.controls);
 verifyReplay(second,replay.result);
 rows.push({name,controls,args,result,replayed_result:second});
 writeFileSync(outputPath,JSON.stringify(rows,null,2)+'\n');
}
assert.equal(rows.length,4);
console.log('PASS: four actual public presets, complete result validation and exact recomputed replay.');
