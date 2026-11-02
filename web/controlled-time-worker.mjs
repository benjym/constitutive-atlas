import {ControlledTimeEngine,PROFILE,sha,strictJSON,canonical} from './controlled-time-engine.mjs';
let loaded;
async function load(){
 if(loaded)return loaded;
 const base=new URL('./engine-controlled-time/',import.meta.url),response=await fetch(new URL('identity.json',base));if(!response.ok)throw Error('Physical-time package unavailable.');const identity=strictJSON(await response.text());
 if(identity.profile!==PROFILE||!identity.files||typeof identity.model!=='string')throw Error('Invalid package identity.');
 async function asset(name){if(!/^[A-Za-z0-9_.-]+$/.test(name)||!/^[a-f0-9]{64}$/.test(identity.files[name]??''))throw Error('Unbound package asset.');const r=await fetch(new URL(name,base));if(!r.ok)throw Error('Missing package asset: '+name);const bytes=await r.arrayBuffer();if(await sha(bytes)!==identity.files[name])throw Error('Changed package asset: '+name);return bytes;}
 const names=['model.json','catalogue.json','engine.mjs','engine.wasm'],bytes=await Promise.all(names.map(asset)),decode=i=>strictJSON(new TextDecoder().decode(bytes[i]));
 const definition=decode(0),catalogue=decode(1);if(definition.id!==identity.model||catalogue.models.length!==1||catalogue.models[0].id!==identity.model||catalogue.models[0].model_sha256!==identity.model_sha256||catalogue.catalogue_sha256!==identity.catalogue_sha256)throw Error('Package model/catalogue mismatch.');
 const url=URL.createObjectURL(new Blob([bytes[2]],{type:'text/javascript'}));
 try{const {default:create}=await import(url),module=await create({wasmBinary:new Uint8Array(bytes[3]),print:()=>{},printErr:()=>{}});loaded={engine:await ControlledTimeEngine.create(module,bytes[1],definition),identity};return loaded;}finally{URL.revokeObjectURL(url);}
}
self.onmessage=async({data})=>{
 try{const {engine,identity}=await load();if(data.model!==identity.model)throw Error('Wrong model request.');if(data.identity&&canonical(data.identity)!==canonical(identity))throw Error('Page/worker package mismatch.');const result=engine.run(data.request);self.postMessage({id:data.id,result,identity});}
 catch(error){self.postMessage({id:data.id,error:error.message});}
};
