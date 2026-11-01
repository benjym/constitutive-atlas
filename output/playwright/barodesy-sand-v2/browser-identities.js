async(page)=>{
 const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v2/';
 const links=await page.locator('#catalogue-dialog a').evaluateAll(xs=>xs.map(x=>({text:x.innerText,href:x.getAttribute('href')})));
 const assets=await page.evaluate(async()=>{
  const paths=['index.html','app.js','worker.js','atlas.js','atlas.wasm','models.json','models/barodesy-sand.json','catalogue.json','evidence.json','atlas.sqlite','evidence-records/catalogue/agent-reviews/barodesy-sand-agent-v1.json','evidence-records/catalogue/agent-reviews/definitions/barodesy-sand-agent-v1.json','docs/models/barodesy-sand-qualified-v1.md.html'];
  const rows=[];for(const path of paths){const r=await fetch('./'+path,{cache:'no-store'});const b=await r.arrayBuffer();rows.push({path,status:r.status,bytes:b.byteLength,sha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')});}return rows;
 });
 await page.screenshot({path:base+'accepted-catalogue.png',fullPage:true});
 return {url:page.url(),links,assets};
}
