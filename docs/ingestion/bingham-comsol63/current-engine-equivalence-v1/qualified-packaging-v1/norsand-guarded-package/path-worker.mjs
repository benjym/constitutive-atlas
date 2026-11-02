import {createPathEngine} from './path-engine.mjs';
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
async function checked(url,hash){const response=await fetch(url);if(!response.ok)throw Error('Path asset unavailable: '+url);const bytes=await response.arrayBuffer();if(await sha(bytes)!==hash)throw Error('Path asset identity mismatch: '+url);return bytes;}
self.onmessage=async({data:{id,model,request}})=>{
 try{
  const base='./engine-path/',response=await fetch(base+'identity.json');if(!response.ok)throw Error('Controlled-path identity unavailable.');
  const identity=await response.json();if(identity.profile!=='controlled-path-ode-v1'||identity.model!==model)throw Error('Unexpected controlled-path identity.');
  const assets={};
  for(const [name,hash]of Object.entries(identity.files)){
   if(!/^[a-zA-Z0-9._-]+$/.test(name))throw Error('Unsafe path asset name.');
   assets[name]=await checked(base+name,hash);
  }
  for(const [name,hash]of Object.entries(identity.components)){
   if(!/^[a-zA-Z0-9._-]+\.mjs$/.test(name))throw Error('Unsafe component name.');await checked('./'+name,hash);
  }
  const decode=name=>JSON.parse(new TextDecoder().decode(assets[name]));
  const catalogue=decode('catalogue.json'),definition=decode('model.json'),approval=decode('approval.json'),review=decode('review.json');
  if(definition.id!==model||identity.files['model.json']!==identity.definition_sha256||approval.model_id!==model||approval.definition.sha256!==identity.definition_sha256||approval.review.sha256!==identity.files['review.json']||approval.definition.path!==review.model.path||approval.status!=='approved'||review.status!=='accepted'||review.model.sha256!==identity.definition_sha256||review.model.id!==model)throw Error('Model/review/approval identity disagreement.');
  const module=await(await import(base+'engine.mjs')).default({wasmBinary:assets['engine.wasm']});
  const engine=createPathEngine(module,catalogue),result=engine.run(model,request);
  self.postMessage({id,result,identity});
 }catch(error){self.postMessage({id,error:error.message});}
};
