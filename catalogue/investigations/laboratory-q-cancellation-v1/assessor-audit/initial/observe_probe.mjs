import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
const [role,build,outfile]=process.argv.slice(2);assert.ok(['native','wasm'].includes(role));assert.ok(!existsSync(outfile));
const cases=JSON.parse(readFileSync(new URL('./reference/inputs.json',import.meta.url),'utf8')).cases;
const module=role==='wasm'?await(await import(pathToFileURL(resolve(build,'q-probe.js')))).default():null;
const rows=[];
for(const c of cases){
 const wire=c.input_bits.join(',');let raw;
 if(role==='wasm')raw=module.ccall('atlas_q_probe','string',['string'],[wire]);
 else{const p=spawnSync(resolve(build,'atlas_q_probe'),[wire],{encoding:'utf8',timeout:30000});raw=p.stdout;assert.equal(p.status,0,p.stderr);}
 rows.push({id:c.id,wire,raw});writeFileSync(outfile,JSON.stringify(rows,null,2)+'\n');
}
assert.equal(rows.length,35);console.log(role+' 35 probe outputs retained');
