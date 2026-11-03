async page => {
 await page.addInitScript(() => {
  const Native=window.Worker;
  window.ensembleWorkerAudit={live:0,maxLive:0,active:0,maxActive:0,requests:0,duplicateRequests:0,created:0,events:[]};
  window.Worker=class extends Native{
   constructor(url,options){super(url,options);this.tracked=String(url).includes('ensemble-worker.mjs');this.busy=false;this.dead=false;if(this.tracked){const a=window.ensembleWorkerAudit;this.auditId=++a.created;a.live++;a.maxLive=Math.max(a.maxLive,a.live);a.events.push({event:'create',worker:this.auditId,time:performance.now()});this.addEventListener('message',()=>{if(this.busy){a.active--;this.busy=false;a.events.push({event:'response',worker:this.auditId,time:performance.now()});}});}}
   postMessage(...args){if(this.tracked){const a=window.ensembleWorkerAudit;if(this.busy)a.duplicateRequests++;this.busy=true;a.active++;a.requests++;a.maxActive=Math.max(a.maxActive,a.active);a.events.push({event:'request',worker:this.auditId,model:args[0].specification.model,time:performance.now()});}return super.postMessage(...args);}
   terminate(){if(this.tracked&&!this.dead){const a=window.ensembleWorkerAudit;this.dead=true;a.live--;if(this.busy){a.active--;this.busy=false;}a.events.push({event:'terminate',worker:this.auditId,time:performance.now()});}return super.terminate();}
  };
 });
 await page.goto('http://127.0.0.1:58743/index.html?parallel-v1#ensemble');
 return await page.evaluate(()=>window.ensembleWorkerAudit);
}
