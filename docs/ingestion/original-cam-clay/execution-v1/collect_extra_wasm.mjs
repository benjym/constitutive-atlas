import{readFileSync,writeFileSync}from'node:fs';import{resolve,dirname,join}from'node:path';import{pathToFileURL}from'node:url';import{createHash}from'node:crypto';
const[modulePath,base]=process.argv.slice(2),m=await(await import(pathToFileURL(resolve(modulePath)))).default();
const read=f=>JSON.parse(readFileSync(join(base,f))),sha=f=>createHash('sha256').update(readFileSync(join(base,f))).digest('hex'),csv=a=>a.map(x=>Object.is(x,-0)?'-0':String(x)).join(','),core=read('requests.json');
function call(name,types,args){let stdout=m.ccall(name,'string',types,args);return{args,returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''};}
const types=Array(5).fill('string'),s=read('supplement-requests.json');
const invoke=(c,linear=false)=>call(linear?'atlas_linearize_with_settings':'atlas_integrate_with_settings',types,[core.model,csv(core.parameters),csv(c.initial),csv(c.de),core.settings]);
writeFileSync(join(base,'wasm-supplement-raw.json'),JSON.stringify({backend:'wasm',request_sha256:sha('supplement-requests.json'),cases:s.cases.map(c=>invoke(c)),tangents:s.tangents.map(c=>invoke(c,true))},null,2)+'\n');
const p=read('public-requests.json'),r=p.reference_pressure;
writeFileSync(join(base,'wasm-public-raw.json'),JSON.stringify({backend:'wasm',request_sha256:sha('public-requests.json'),cases:p.cases.map(c=>({name:c.name,...call('atlas_run_with_settings',['string','string','string','number','number','number','number','string'],[core.model,csv(c.parameters),csv(c.initial),c.protocol,c.target,c.steps,c.cycles,c.settings])})),reference_pressure:call('atlas_integrate_with_settings',types,[core.model,csv(r.parameters),csv(r.initial),csv(r.de),r.settings])},null,2)+'\n');
const t=read('transaction-requests.json');
const calls=t.cases.map(c=>({name:c.name,...call('atlas_integrate_with_settings',types,[core.model,csv(core.parameters),csv(c.initial),csv(c.de),c.settings])}));
writeFileSync(join(base,'wasm-transaction-raw.json'),JSON.stringify({backend:'wasm',request_sha256:sha('transaction-requests.json'),cases:calls},null,2)+'\n');
console.log('Saved Wasm supplemental, public control and partial-transaction requests');
