import {validateControls,request,verifyResult,verifyReplay,exportRun,importRun} from './maxwell-atlas-contract.mjs';
// Lifecycle shared by the visible panel and deterministic worker-race tests.
export function createMaxwellRunner({createWorker=()=>new Worker(new URL('./maxwell-atlas-worker.mjs',import.meta.url),{type:'module'}),notify=()=>{},setTimer=setTimeout,clearTimer=clearTimeout,timeout=120000}={}) {
  let generation=0,worker=null,timer=null,last=null;
  const stop=()=>{worker?.terminate();worker=null;if(timer!==null)clearTimer(timer);timer=null;};
  function cancel(message='Inputs changed. Run to update results.') {generation++;stop();last=null;notify({state:'idle',message});}
  function run(input,{expected=null}={}) {
    cancel();const id=generation;let controls;
    try { controls=validateControls(input); } catch(error) {notify({state:'error',message:'Invalid input: '+error.message});return;}
    try {worker=createWorker();}catch(error){notify({state:'error',message:'Worker unavailable: '+error.message});return;}
    const current=worker;
    const fail=error=>{if(id!==generation||worker!==current)return;stop();last=null;notify({state:'error',message:'Run failed: '+error});};
    current.onerror=event=>fail(event.message||'Worker error.');
    current.onmessage=({data})=>{
      if(id!==generation||worker!==current||data?.id!==id)return;
      if(data.error){fail(data.error);return;}
      try {
        verifyResult(data.result,data.identity,controls);
        if(JSON.stringify(data.args)!==JSON.stringify(request(controls,data.identity)))throw Error('Worker request differs from explicit controls.');
        if(expected!==null){const imported=importRun(JSON.stringify(expected),data.identity);verifyReplay(data.result,imported.result);}
        const saved=exportRun(controls,data.result,data.identity);stop();last=saved;notify({state:'complete',message:'Physical-time history complete.',run:structuredClone(saved)});
      }catch(error){fail(error.message);}
    };
    notify({state:'running',message:'Running physical-time history…'});
    timer=setTimer(()=>fail('Time limit exceeded; review duration and inputs.'),timeout);
    try {current.postMessage({id,controls});}catch(error){fail(error.message);}
  }
  return {run,cancel,get generation(){return generation;},get last(){return last===null?null:structuredClone(last);}};
}
