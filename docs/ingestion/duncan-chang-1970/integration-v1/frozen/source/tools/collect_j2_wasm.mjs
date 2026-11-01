// Raw calls, two repeats per request, one module including invalid/recovery calls.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [modulePath,casesPath,outputPath]=process.argv.slice(2);
if(!outputPath)throw Error('usage: node tools/collect_j2_wasm.mjs MODULE REFERENCES OUTPUT');
const create=(await import(pathToFileURL(resolve(modulePath)))).default;
const wasm=await create();
const cases=JSON.parse(readFileSync(casesPath,'utf8')).cases;
const rows=[];
for(const test of cases){
 const calls=[];
 for(let repeat=0;repeat<2;repeat++){
  const stdout=wasm.ccall(test.call,'string',test.types,test.args);
  calls.push({returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''});
 }
 rows.push({id:test.id,calls});
 writeFileSync(outputPath,JSON.stringify(rows,null,2)+'\n');
}
console.log(`Saved ${rows.length*2} raw calls from one J2 Wasm module.`);
