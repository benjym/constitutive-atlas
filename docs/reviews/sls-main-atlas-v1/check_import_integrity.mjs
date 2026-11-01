// Pure transport assessment: read retained scientific capture; execute no Wasm.
import fs from 'node:fs';
import {defaults,request,importRun,modelId,modelSha256} from '../../../web/sls-atlas-contract.mjs';
const rows=JSON.parse(fs.readFileSync(new URL('../../ingestion/sls-comsol63/execution-v1/wasm-raw.json',import.meta.url)));
const result=JSON.parse(rows.find(x=>x.id==='relax-schedule').calls[0].stdout);
const identity={model:modelId,model_sha256:modelSha256,catalogue_hash:result.catalogue_hash};
const data={kind:'atlas-sls-laboratory-v1',controls:structuredClone(defaults),provenance:identity,request:{function:'atlas_run_schedule',args:request(defaults,identity)},result};
importRun(JSON.stringify(data),identity);
data.result.points.at(-1).observables[0]+=1000000;
let rejected=false;try{importRun(JSON.stringify(data),identity);}catch{rejected=true;}
console.log(JSON.stringify({gate:'Altered saved stress must reject for result-integrity replay claim',rejected},null,2));
if(!rejected)process.exitCode=1;
