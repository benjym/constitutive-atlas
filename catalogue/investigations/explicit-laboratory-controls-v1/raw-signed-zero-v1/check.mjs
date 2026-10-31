import assert from 'node:assert/strict';
import {writeFileSync,readFileSync,existsSync,mkdtempSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const [native,wasmdir,outfile]=process.argv.slice(2);assert.ok(!existsSync(outfile));
const bits=x=>{const b=Buffer.alloc(8);b.writeDoubleBE(x);return b.toString('hex');};
const values=[-0,Number.MIN_VALUE,-Number.MIN_VALUE,0],expected=values.map(bits),wire=expected.join(',');
const dir=mkdtempSync('/private/tmp/atlas-raw-zero-');writeFileSync(resolve(dir,'controls.csv'),wire);
const initial='100000,100000,100000,0,0,0,0.7';
const n=spawnSync(native,['--mode','run-controls','--model','linear-elastic','--initial',initial,'--protocol','0','--laboratory-controls-file',resolve(dir,'controls.csv')],{encoding:'utf8',timeout:30000});
const engine=await(await import(pathToFileURL(resolve(wasmdir,'atlas.js')))).default();
const w=engine.ccall('atlas_run_controls_with_settings','string',['string','string','string','number','string','string'],['linear-elastic','',initial,0,wire,'']);
// Raw response strings are preserved before assertions and before JSON reserialization.
writeFileSync(outfile,JSON.stringify({wire,expected,native:{returncode:n.status,raw:n.stdout,stderr:n.stderr},wasm:{raw:w}})+'\n');
assert.equal(n.status,0,n.stderr);
for(const raw of [n.stdout,w]){const r=JSON.parse(raw);assert.equal(r.ok,true,r.message);assert.deepEqual(r.loading.controls_bits,expected);assert.deepEqual(r.loading.controls.map(bits),expected);assert.deepEqual(r.points.map(p=>bits(p.control)),expected);}
console.log('Both raw responses preserve signed zero and subnormal controls exactly.');
