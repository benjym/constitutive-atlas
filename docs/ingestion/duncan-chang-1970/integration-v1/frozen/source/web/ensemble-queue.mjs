// A single worker call at a time; the executor owns termination on AbortSignal.
export class EnsembleQueue{
 constructor(execute,onChange=()=>{},timeoutMs=30000){this.execute=execute;this.onChange=onChange;this.timeoutMs=timeoutMs;this.running=false;this.cancelled=false;}
 cancel(){this.cancelled=true;this.controller?.abort();if(this.study)for(const job of this.study.jobs)if(job.status==='queued'){job.status='cancelled';job.message='Cancelled before execution.';}this.onChange(this.study);}
 async run(study){
  if(this.running)throw Error('An ensemble is already running.');
  this.running=true;this.cancelled=false;this.study=study;
  try{for(const job of study.jobs){
   if(this.cancelled)break;if(job.status!=='queued')continue;
   job.status='running';this.controller=new AbortController();this.onChange(study);
   let timedOut=false,timer;
   const aborted=new Promise((_,reject)=>this.controller.signal.addEventListener('abort',()=>reject(Error(timedOut?'Run exceeded its time limit.':'Cancelled during execution.')),{once:true}));
   timer=setTimeout(()=>{timedOut=true;this.controller.abort();},this.timeoutMs);
   try{job.result=await Promise.race([this.execute(structuredClone(job),this.controller.signal),aborted]);job.status=job.result.ok?'completed':'stopped';job.message=job.result.message||'';}
   catch(error){job.result=null;job.status=timedOut?'timeout':this.cancelled?'cancelled':'error';job.message=String(error.message||error);}
   finally{clearTimeout(timer);this.controller=null;this.onChange(study);}
  }}finally{this.running=false;this.onChange(study);}return study;
 }
}
