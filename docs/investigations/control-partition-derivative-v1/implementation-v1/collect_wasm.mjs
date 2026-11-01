// Standalone helper fixture only; coordinator executes after review/build.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const [modulePath]=process.argv.slice(2);
const factory=(await import(pathToFileURL(path.resolve(modulePath)))).default;
const engine=await factory({print:x=>process.stderr.write(String(x)+'\n'),printErr:x=>process.stderr.write(String(x)+'\n')});
for(let repeat=0;repeat<2;repeat++){
 const stdout=engine.ccall('atlas_control_partition_fixture','string',[],[]);
 let returncode=1,parse_error;try{returncode=JSON.parse(stdout).passed?0:1;}catch(e){parse_error=String(e);}
 process.stdout.write(JSON.stringify({repeat,returncode,stdout,stderr:'',parse_error})+'\n');
}
