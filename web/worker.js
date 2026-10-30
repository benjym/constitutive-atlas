import createAtlas from './atlas.js';
let engine;
self.onmessage = async ({data}) => {
  try {
    engine ??= await createAtlas();
    const result = JSON.parse(engine.ccall('atlas_run', 'string',
      ['string','string','string','number','number','number','number'],
      [data.model, data.parameters.join(','), data.initial.join(','), data.protocol, data.target, data.steps, data.cycles]));
    self.postMessage({id:data.id,result});
  } catch (error) { self.postMessage({id:data.id,error:String(error)}); }
};
