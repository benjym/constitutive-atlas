import createAtlas from './atlas.js';
import {replayRecorded} from './recorded-worker.mjs';
import {runLaboratory} from './numerics.mjs';
let engine;
self.onmessage = async ({data}) => {
  try {
    engine ??= await createAtlas();
    const result = data.kind==='recorded'?replayRecorded(engine,data.specification,data.catalogue):runLaboratory(engine,data,data.catalogue_hash);
    self.postMessage({id:data.id,result});
  } catch (error) { self.postMessage({id:data.id,error:String(error)}); }
};
