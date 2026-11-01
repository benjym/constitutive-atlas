// Same line protocol and existing C ABI; one persistent module per process.
import {createInterface} from 'node:readline';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const module=await(await import(pathToFileURL(resolve(process.argv[2])))).default({print:x=>process.stderr.write(x+'\n'),printErr:x=>process.stderr.write(x+'\n')});
for await(const line of createInterface({input:process.stdin,crlfDelay:Infinity})) {
 const f=line.split('\t');
 if(line==='D')process.stdout.write(module.ccall('atlas_describe','string',[],[])+'\n');
 else {
  if(f.length!==6||f[0]!=='I')throw Error('invalid line transport');
  process.stdout.write(module.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),f.slice(1))+'\n');
 }
}
