// Bounded diagnostics only. No default, tolerance, model or gate is changed.
import {readFileSync}from 'node:fs';
import createAtlas from '/private/tmp/atlas-gis2024-mixed-catalogue-v1/wasm/atlas.js';
import {runScopedLaboratory}from '../../../web/laboratory-scope.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const original=JSON.parse(read('./default-check-process.json').stdout),catalogue=read('../gis2024-mixed-catalogue-v1/generated-eleven/models.json'),engine=await createAtlas();
const results=[];
for(const depth of [14,20])for(const amount of [1.25e-6,1e-4]){
 const s=structuredClone(original.specification),settings=s.integration_settings;settings.max_depth=depth;
 const strain=[amount,-.2*amount,-.2*amount,0,0,0];const wire=[settings.residual_tolerance,settings.rate_tolerance,settings.max_iterations,settings.max_depth,settings.max_substeps,settings.max_backtracks].join(',');
 const args=[s.model,s.parameters.join(','),s.initial.join(','),strain.join(','),wire];const raw=engine.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],args);
 results.push({kind:'first_outer_trial_increment',depth,amount,args,raw,response:JSON.parse(raw)});
}
const s=structuredClone(original.specification);s.integration_settings.max_depth=20;
results.push({kind:'full_run_depth20_diagnostic_only',specification:s,response:runScopedLaboratory(engine,s,catalogue)});
console.log(JSON.stringify({scope:'Distinct diagnostics; original failed default is unchanged. Results are not a new qualified browser default.',results},null,2));
