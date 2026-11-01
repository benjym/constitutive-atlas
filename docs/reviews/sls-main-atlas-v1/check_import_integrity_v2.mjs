// Pure revised replay assessment: saved independently qualified result stands in for fresh same-engine response.
import fs from 'node:fs';
import {defaults,request,importRun,verifyReplay,modelId,modelSha256} from '../../../web/sls-atlas-contract.mjs';
const rows=JSON.parse(fs.readFileSync(new URL('../../ingestion/sls-comsol63/execution-v1/wasm-raw.json',import.meta.url)));
const actual=JSON.parse(rows.find(x=>x.id==='relax-schedule').calls[0].stdout);
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:actual.catalogue_hash};
const data={kind:'atlas-sls-laboratory-v1',controls:structuredClone(defaults),provenance:identity,request:{function:'atlas_run_schedule',args:request(defaults,identity)},result:structuredClone(actual)};
const pristine=importRun(JSON.stringify(data),identity,{withResult:true});verifyReplay(actual,pristine.result);
const results=[];
for(const [label,mutate]of [['finite-stress',d=>d.result.points.at(-1).observables[0]+=1000000],['finite-branch',d=>d.result.points.at(-1).state[9]+=1000000],['finite-strain',d=>{d.result.points.at(-1).state[0]+=.001;d.result.points.at(-1).strain[0]+=.001;}],['rate',d=>d.result.points.at(-1).strain_rate[0]+=.001]]){
 const changed=structuredClone(data);mutate(changed);let rejected=false;
 try{const imported=importRun(JSON.stringify(changed),identity,{withResult:true});verifyReplay(actual,imported.result);}catch{rejected=true;}
 if(!rejected)throw Error(label+' was accepted');results.push({label,rejected});
}
console.log(JSON.stringify({passed:true,pristineReplay:true,results},null,2));
