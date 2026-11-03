async(page)=>{
 const names=['index.html','app.js','plot-labels.mjs','model-profile-data.mjs','model-profiles.mjs','models.json','catalogue.json','controlled-time-engine.mjs','controlled-time-worker.mjs','controlled-time-laboratory.mjs','atlas.js','atlas.wasm',...['model.json','catalogue.json','engine.mjs','engine.wasm','examples.json','expected-results.json','review.json','qualification.json','approval.json','identity.json','package-manifest.json'].map(n=>'engine-controlled-time/'+n)];
 const rows=await page.evaluate(async names=>{
  const result=[];
  for(const name of names){const r=await fetch(new URL(name,location.href)),bytes=await r.arrayBuffer();const digest=await crypto.subtle.digest('SHA-256',bytes);result.push({name,url:r.url,status:r.status,bytes:bytes.byteLength,sha256:Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('')});}
  return result;
 },names);
 if(rows.some(x=>x.status!==200))throw Error(JSON.stringify(rows.filter(x=>x.status!==200)));
 return rows;
}
