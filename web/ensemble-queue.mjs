// Leave a core for interaction where possible; bound simultaneous Wasm instances.
export function ensembleConcurrency(cores=4){return Math.min(8,Math.max(1,Math.floor(Number(cores)||4)-1));}
// Bounded independent runs; the executor owns worker termination on AbortSignal.
export class EnsembleQueue{
 constructor(execute,onChange=()=>{},timeoutMs=30000,concurrency=1){
  if(!Number.isInteger(concurrency)||concurrency<1||concurrency>8)throw Error('Use one to eight concurrent ensemble runs.');
  this.execute=execute;this.onChange=onChange;this.timeoutMs=timeoutMs;this.concurrency=concurrency;this.running=false;this.cancelled=false;this.controllers=new Map();
 }
 cancel(){
  this.cancelled=true;
  if(this.study)for(const job of this.study.jobs)if(job.status==='queued'){job.status='cancelled';job.message='Cancelled before execution.';}
  for(const controller of this.controllers.values())controller.abort();
  this.onChange(this.study);
 }
 // Reuse only requests bound to the same catalogue and exact model definition.
 reconcile(study){
  const previous=this.study,old=new Map((previous?.jobs||[]).map(job=>[job.id,job]));
  const sameCatalogue=previous?.catalogue_hash===study.catalogue_hash&&JSON.stringify(previous?.experiment)===JSON.stringify(study.experiment);
  study.jobs=study.jobs.map(job=>{
   const prior=old.get(job.id);
   if(sameCatalogue&&prior&&prior.status!=='cancelled'&&
      JSON.stringify(previous.model_definitions?.find(m=>m.id===job.model))===JSON.stringify(study.model_definitions?.find(m=>m.id===job.model))&&
      JSON.stringify([prior.specification,prior.parameters,prior.history])===JSON.stringify([job.specification,job.parameters,job.history]))return prior;
   return job;
  });
  this.study=study;
  const retained=new Set(study.jobs);
  for(const [job,controller]of this.controllers)if(!retained.has(job))controller.abort();
  return study;
 }
 async run(study){
  if(this.running)throw Error('An ensemble is already running.');
  this.running=true;this.cancelled=false;this.study=study;
  const consume=async()=>{
   while(!this.cancelled){
    const job=this.study.jobs.find(job=>job.status==='queued');if(!job)break;
    const controller=new AbortController();this.controllers.set(job,controller);job.status='running';
    let timedOut=false,timer;
    const aborted=new Promise((_,reject)=>controller.signal.addEventListener('abort',()=>reject(Error(timedOut?'Run exceeded its time limit.':'Cancelled during execution.')),{once:true}));
    timer=setTimeout(()=>{timedOut=true;controller.abort();},this.timeoutMs);
    this.onChange(this.study);
    try{job.result=await Promise.race([this.execute(structuredClone(job),controller.signal),aborted]);job.status=job.result.ok?'completed':'stopped';job.message=job.result.message||'';}
    catch(error){job.result=null;job.status=timedOut?'timeout':this.cancelled?'cancelled':'error';job.message=String(error.message||error);}
    finally{clearTimeout(timer);this.controllers.delete(job);this.onChange(this.study);}
   }
  };
  try{await Promise.all(Array.from({length:this.concurrency},consume));}
  finally{this.running=false;this.onChange(this.study);}return this.study;
 }
}
