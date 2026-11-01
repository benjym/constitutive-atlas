import createAtlas from './atlas.js';
import {replayRecorded} from './recorded-worker.mjs';
import {stable} from './ensemble.mjs';
let engine;
self.onmessage=async({data})=>{
 try{
  engine??=await createAtlas();
  if(stable(JSON.parse(engine.ccall('atlas_describe','string',[],[])))!==stable(data.catalogue))throw Error('Compiled engine and catalogue differ.');
  self.postMessage({id:data.id,result:replayRecorded(engine,data.specification,data.catalogue)});
 }catch(error){self.postMessage({id:data.id,error:String(error.message||error)});}
};
