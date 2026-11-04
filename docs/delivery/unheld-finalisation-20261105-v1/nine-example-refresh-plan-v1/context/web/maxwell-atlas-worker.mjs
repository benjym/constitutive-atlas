import {runMaxwellSchedule} from './maxwell-atlas-engine.mjs';
self.onmessage=async({data})=>{
  const id=data?.id;
  try { self.postMessage({id,...await runMaxwellSchedule(data.controls)}); }
  catch(error) { self.postMessage({id,error:error.message}); }
};
