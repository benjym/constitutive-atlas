// Execute identical frozen independent-reference requests in one actual common Wasm instance.
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
const [build,reference,out]=process.argv.slice(2);if(!out)throw Error('build reference output required');
const cases=JSON.parse(fs.readFileSync(reference)).cases;const create=(await import(pathToFileURL(path.resolve(build,'orthotropic.js')))).default;
const api=await create({locateFile:x=>path.resolve(build,x)});const rows=[],states=new Map();
for(const c of cases){const w=structuredClone(c.call);if(c.previous)w.args[2]=states.get(c.previous).join(',');const response=JSON.parse(api.ccall(w.function,'string',w.types,w.args));rows.push({id:c.id,call:w,response});if(response.ok)states.set(c.id,response.state);fs.writeFileSync(out,JSON.stringify(rows,null,2)+'\n');}
console.log(JSON.stringify({cases:rows.length,output:out}));
