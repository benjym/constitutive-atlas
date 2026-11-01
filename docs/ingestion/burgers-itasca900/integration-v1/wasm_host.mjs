// Persistent shared-module transport. No constitutive equations or special kernels.
import {createInterface} from 'node:readline';
import {pathToFileURL} from 'node:url';
const create=(await import(pathToFileURL(process.argv[2]))).default;
const module=await create();
const lines=createInterface({input:process.stdin,crlfDelay:Infinity});
for await(const line of lines){
  const q=JSON.parse(line);
  const types=q.args.map(x=>typeof x==='string'?'string':'number');
  const response=JSON.parse(module.ccall(q.function,'string',types,q.args));
  process.stdout.write(JSON.stringify(response)+'\n');
}
