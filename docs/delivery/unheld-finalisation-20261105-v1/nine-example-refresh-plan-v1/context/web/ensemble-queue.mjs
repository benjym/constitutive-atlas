// Bounded independent runs; the executor owns worker termination on AbortSignal.
export class EnsembleQueue{
 constructor(execute,onChange=()=>{},timeoutMs=30000,concurrency=1){
  if(!Number.isInteger(concurrency)||concurrency<1||concurrency>4)throw Error('Use one to four concurrent ensemble runs.');
  this.execute=execute;this.onChange=onChange;this.timeoutMs=timeoutMs;this.concurrency=concurrency;this.running=false;this.cancelled=false;this.controllers=new Set();
 }
 cancel(){
  this.cancelled=true;
  if(this.study)for(const job of this.study.jobs)if(job.status==='queued'){job.status='cancelled';job.message='Cancelled before execution.';}
  for(const controller of this.controllers)controller.abort();
  this.onChange(this.study);
 }
 async run(study){
  if(this.running)throw Error('An ensemble is already running.');
  this.running=true;this.cancelled=false;this.study=study;let next=0;
  const consume=async()=>{
   while(!this.cancelled&&next<study.jobs.length){
    const job=study.jobs[next++];if(job.status!=='queued')continue;
    const controller=new AbortController();this.controllers.add(controller);job.status='running';
    let timedOut=false,timer;
    const aborted=new Promise((_,reject)=>controller.signal.addEventListener('abort',()=>reject(Error(timedOut?'Run exceeded its time limit.':'Cancelled during execution.')),{once:true}));
    timer=setTimeout(()=>{timedOut=true;controller.abort();},this.timeoutMs);
    this.onChange(study);
    try{job.result=await Promise.race([this.execute(structuredClone(job),controller.signal),aborted]);job.status=job.result.ok?'completed':'stopped';job.message=job.result.message||'';}
    catch(error){job.result=null;job.status=timedOut?'timeout':this.cancelled?'cancelled':'error';job.message=String(error.message||error);}
    finally{clearTimeout(timer);this.controllers.delete(controller);this.onChange(study);}
   }
  };
  try{await Promise.all(Array.from({length:this.concurrency},consume));}
  finally{this.running=false;this.onChange(study);}return study;
 }
}
