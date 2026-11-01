import {readFileSync}from 'node:fs';
import createAtlas from '/private/tmp/atlas-gis2024-mixed-catalogue-v1/wasm/atlas.js';
import {runScopedLaboratory}from '../../../web/laboratory-scope.mjs';
import {normalizeSettings}from '../../../web/numerics.mjs';
import {createLoading}from '../../../web/loading.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const catalogue=read('../gis2024-mixed-catalogue-v1/generated-eleven/models.json'),model=read('../gis2024-v03-research-freeze-v1/model.json');
const s={response_contract:'stress-scope-0.1',stress_scope:'effective',model:model.id,parameters:Object.values(model.parameters).map(p=>p.default),initial:model.state.flatMap(f=>f.shape==='sym'?f.initial:[f.initial]),protocol:1,target:.01,steps:100,cycles:0,integration_settings:normalizeSettings()};s.loading=createLoading(s);
const engine=await createAtlas();const result=runScopedLaboratory(engine,s,catalogue);console.log(JSON.stringify({specification:s,result},null,2));if(!result.ok)process.exitCode=1;
