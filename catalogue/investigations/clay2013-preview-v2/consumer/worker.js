import createAtlas from './atlas.js';
import {runRecorded} from './recorded.mjs';
import {runLaboratory} from './numerics.mjs';
let engine;
self.onmessage = async ({data}) => {
  try {
    engine ??= await createAtlas();
    const result = data.kind==='recorded'?runRecorded(engine,data.specification):runLaboratory(engine,data);
    self.postMessage({id:data.id,result});
  } catch (error) { self.postMessage({id:data.id,error:String(error)}); }
};
