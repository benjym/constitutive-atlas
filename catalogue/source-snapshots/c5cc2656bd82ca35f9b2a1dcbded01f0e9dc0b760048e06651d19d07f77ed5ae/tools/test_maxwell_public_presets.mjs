// Exercise the actual public control/transport contract against reviewed Wasm.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {modelId,modelSha256,presetNames,preset,request,types,verifyResult,exportRun,importRun,verifyReplay} from '../web/maxwell-atlas-contract.mjs';

const [buildPath,outputPath]=process.argv.slice(2);
if(!buildPath||!outputPath)throw Error('usage: node tools/test_maxwell_public_presets.mjs BUILD OUTPUT');
const build=resolve(buildPath);
const catalogue=JSON.parse(readFileSync(resolve(build,'generated/models.json'),'utf8'));
const module=(await import(pathToFileURL(resolve(build,'maxwell.js')))).default;
const engine=await module();
assert.deepEqual(JSON.parse(engine.ccall('atlas_describe','string',[],[])),catalogue);
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:catalogue.sha256,release_revision:'qualified-engine-ci-regression'};
const rows=[];
for(const name of presetNames){
 const controls=preset(name),args=request(controls,identity);
 const result=JSON.parse(engine.ccall('atlas_run_schedule','string',types,args));
 verifyResult(result,identity,controls);
 const saved=exportRun(controls,result,identity);
 const replay=importRun(JSON.stringify(saved),identity);
 const second=JSON.parse(engine.ccall('atlas_run_schedule','string',types,request(replay.controls,identity)));
 verifyResult(second,identity,replay.controls);
 verifyReplay(second,replay.result);
 rows.push({name,controls,args,result,replayed_result:second});
 writeFileSync(outputPath,JSON.stringify(rows,null,2)+'\n');
}
assert.equal(rows.length,4);
console.log('PASS: four actual public presets, complete result validation and exact recomputed replay.');
