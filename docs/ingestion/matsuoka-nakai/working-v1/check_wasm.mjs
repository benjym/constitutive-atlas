import fs from 'node:fs';
import zlib from 'node:zlib';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const {default:create}=await import(pathToFileURL(path.resolve(process.argv[2])));
const runtime=await create();
const filename=path.join(here,'native-responses.jsonl');
const source=(fs.existsSync(filename)?fs.readFileSync(filename,'utf8'):zlib.gunzipSync(fs.readFileSync(filename+'.gz')).toString('utf8')).trim().split('\n').map(JSON.parse);
const outdir=path.resolve(process.argv[3]||'/private/tmp/nh2004-wasm-replay');
fs.mkdirSync(outdir,{recursive:true});
const raw=fs.openSync(path.join(outdir,'wasm-responses.jsonl'),'w');
const failures=[];let compared=0;
for(let i=0;i<source.length;i++){
 const {request,response:expected}=source[i];
 const actual=JSON.parse(runtime.ccall('atlas_integrate_with_settings','string',Array(5).fill('string'),request));
 fs.writeSync(raw,JSON.stringify({request,response:actual})+'\n');
 if(actual.ok!==expected.ok||actual.message!==expected.message)failures.push({row:i,reason:'status/message'});
 for(const key of ['model','initial','strain','parameters'])if(JSON.stringify(actual[key])!==JSON.stringify(expected[key]))failures.push({row:i,reason:key});
 if(actual.state.length!==expected.state.length)failures.push({row:i,reason:'state length'});
 for(let j=0;j<actual.state.length;j++){
  const a=actual.state[j],b=expected.state[j];
  if(!Number.isFinite(a)||Math.abs(a-b)>1e-8*Math.max(1,Math.abs(b)))failures.push({row:i,component:j,actual:a,expected:b});
  compared++;
 }
 if(!actual.ok && JSON.stringify(actual.state)!==JSON.stringify(expected.state))failures.push({row:i,reason:'rollback exactness'});
}
fs.closeSync(raw);
const fixtures=JSON.parse(fs.readFileSync(path.join(here,'residual-fixtures.json')));
for(const f of fixtures){
 const actual=JSON.parse(runtime.ccall('atlas_evaluate','string',Array(5).fill('string'),['nakai-hinokio-2004-clay-appendix-v-be','',f.current.join(','),f.parent.join(','),f.de.join(',')]));
 if(!actual.ok){failures.push({fixture:f.branch,reason:'evaluation failed'});continue;}
 for(let j=0;j<actual.values.length;j++)if(!Number.isFinite(actual.values[j])||Math.abs(actual.values[j])/(j<6?98000:1)>2e-8)failures.push({fixture:f.branch,component:j,value:actual.values[j]});
}
const report={status:failures.length?'failed':'pass',native_wasm_pairs:source.length,state_components:compared,source_residual_fixtures:fixtures.length,failures};
fs.writeFileSync(path.join(outdir,'wasm-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
process.exitCode=failures.length?1:0;
