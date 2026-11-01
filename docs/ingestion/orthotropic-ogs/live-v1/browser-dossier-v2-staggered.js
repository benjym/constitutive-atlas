async(page)=>{
 const result=await page.evaluate(async()=>{
  const paths=['docs/models/orthotropic-linear-elastic-ogs.md','docs/models/orthotropic-linear-elastic-ogs.md.html'],assets=[],texts=[];
  for(const path of paths){const r=await fetch('./'+path),b=await r.arrayBuffer(),sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');assets.push({path,status:r.status,sha256});texts.push(new TextDecoder().decode(b));}
  const [markdown,html]=texts,doc=new DOMParser().parseFromString(html,'text/html'),htmlURL=new URL(paths[1],location.href),urls=[...new Set(markdown.match(/https?:\/\/[^\s)]+/g)||[])],navigation=[...doc.querySelectorAll('a[href]')].map(a=>new URL(a.getAttribute('href'),htmlURL).href);
  return {assets,markdownSha256:assets[0].sha256,htmlPreMatchesMarkdown:doc.querySelector('pre')?.textContent===markdown,currentStatusAccurate:markdown.includes('source-complete, independently agent-approved formulation is available in the general atlas laboratory')&&!markdown.includes('compiled backend/control/restart/browser checks outstanding')&&!markdown.includes('Task ID: ING-orthotropic-ogs-v1'),noUnpublishedRelativeLedger:!markdown.includes('../ingestion/orthotropic-ogs/DELIVERY.md'),urls:[...new Set([...urls,...navigation])]};
 });
 const links=[];for(const url of result.urls){if(new URL(url).hostname==='github.com')await page.waitForTimeout(20000);const started=new Date().toISOString(),r=await page.request.get(url,{timeout:30000});links.push({url,status:r.status(),started,finished:new Date().toISOString(),headers:r.headers()});}return {...result,links};
}
