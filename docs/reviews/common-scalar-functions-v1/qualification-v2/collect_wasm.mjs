import {readFileSync,writeFileSync,existsSync} from 'node:fs';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {resolve} from 'node:path';import {createHash} from 'node:crypto';
const [file,out]=process.argv.slice(2);assert.ok(!existsSync(out));const here=new URL('.',import.meta.url),requests=JSON.parse(readFileSync(new URL('requests.json',here))).cases;
const module=await(await import(pathToFileURL(resolve(file)))).default();const rows=[];
for(const c of requests){const a=Buffer.from(c.a_bits,'hex').readDoubleBE(),b=Buffer.from(c.b_bits,'hex').readDoubleBE(),raw=module.ccall('atlas_scalar_functions_probe','string',['number','number','number','number'],[c.kind,a,b,c.seeds]);rows.push({id:c.id,raw,response:JSON.parse(raw)});writeFileSync(out,JSON.stringify({backend:'wasm',js_sha256:createHash('sha256').update(readFileSync(file)).digest('hex'),rows},null,2)+'\n');}
console.log(rows.length+'Wasm scalar observations retained');
