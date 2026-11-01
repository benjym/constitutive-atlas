import {validateControls,request,verifyResult,verifyReplay,exportRun,importRun,stringifyRun,equal} from './implicit-path-contract.mjs';
// Lifecycle shared by the visible panel and deterministic worker-race tests.
export function createImplicitPathRunner({createWorker=()=>new Worker(new URL('./implicit-path-worker.mjs',import.meta.url),{type:'module'}),notify=()=>{},setTimer=setTimeout,clearTimer=clearTimeout,timeout=120000,now=()=>performance.now()}={}) {
  let generation=0,worker=null,timer=null,last=null;
  const stop=()=>{worker?.terminate();worker=null;if(timer!==null)clearTimer(timer);timer=null;};
  function cancel(message='Inputs changed. Run to update results.') {generation++;stop();last=null;notify({state:'idle',message});}
  function run(input,{expected=null}={}) {
    cancel();const id=generation;let controls;
    try { controls=validateControls(input); } catch(error) {notify({state:'error',message:'Invalid input: '+error.message});return;}
    const started=now();
    try {worker=createWorker();}catch(error){notify({state:'error',message:'Worker unavailable: '+error.message});return;}
    const current=worker;
    const fail=error=>{if(id!==generation||worker!==current)return;stop();last=null;notify({state:'error',message:'Run failed: '+error});};
    current.onerror=event=>fail(event.message||'Worker error.');
    current.onmessage=({data})=>{
      if(id!==generation||worker!==current||data?.id!==id)return;
      if(now()-started>=timeout){fail('Time limit exceeded; reduce the path size or review inputs.');return;}
      if(data.error){fail(data.error);return;}
      try {
        verifyResult(data.result,data.identity,controls);
        if(!equal(data.args,request(controls,data.identity)))throw Error('Worker request differs from explicit controls.');
        if(!data.result.ok){const partial=structuredClone(data.result);stop();last=null;notify({state:'error',message:partial.message,partial});return;}
        if(expected!==null){const imported=importRun(stringifyRun(expected),data.identity);verifyReplay(data.result,imported.result);}
        const saved=exportRun(controls,data.result,data.identity);stop();last=saved;notify({state:'complete',message:'Strain-path response complete.',run:structuredClone(saved)});
      }catch(error){fail(error.message);}
    };
    notify({state:'running',message:'Running strain-path response…'});
    if(now()-started>=timeout){fail('Time limit exceeded; reduce the path size or review inputs.');return;}
    timer=setTimer(()=>fail('Time limit exceeded; reduce the path size or review inputs.'),Math.max(0,timeout-(now()-started)));
    try {current.postMessage({id,controls});}catch(error){fail(error.message);}
  }
  return {run,cancel,get generation(){return generation;},get last(){return last===null?null:structuredClone(last);}};
}
