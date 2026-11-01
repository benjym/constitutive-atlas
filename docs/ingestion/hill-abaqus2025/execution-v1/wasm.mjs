import fs from 'node:fs';import {pathToFileURL} from 'node:url';import path from 'node:path';
const base=path.dirname(new URL(import.meta.url).pathname),refs=JSON.parse(fs.readFileSync(path.join(base,'references.json'))),engine=await(await import(pathToFileURL(process.argv[2]))).default();
const raw=[];
for(const c of refs.cases){const runs=[];for(let repeat=0;repeat<2;repeat++){let z=c.initial;const rows=[];for(const de of c.increments){const row=JSON.parse(engine.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),[refs.model,c.parameters.join(','),z.join(','),de.join(','),refs.settings]));rows.push(row);if(!row.ok)break;z=row.state;}runs.push(rows);}raw.push({id:c.id,runs});fs.writeFileSync(path.join(base,'wasm-raw.json'),JSON.stringify(raw,null,2)+'\n');}
const native=JSON.parse(fs.readFileSync(path.join(base,'native-raw.json')));let stress=0,gamma=0;
for(let i=0;i<raw.length;i++)for(let j=0;j<raw[i].runs[0].length;j++)for(let k=0;k<7;k++){const e=Math.abs(raw[i].runs[0][j].state[k]-native[i].runs[0][j].state[k]);if(e>(k<6?1e-7:1e-12))throw Error('Parity failed');if(k<6)stress=Math.max(stress,e);else gamma=Math.max(gamma,e);}
fs.writeFileSync(path.join(base,'parity.json'),JSON.stringify({passed:true,max_stress_error_Pa:stress,max_multiplier_error:gamma},null,2)+'\n');
