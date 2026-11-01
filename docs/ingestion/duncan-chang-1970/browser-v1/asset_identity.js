async (page) => {
  return await page.evaluate(async()=>{
    const names=['atlas.js','atlas.wasm','models.json','models/duncan-chang-1970-endpoint-average.json','evidence.json','laboratory-examples.json','app.js','worker.js'];
    const assets=[];
    for(const name of names){
      const r=await fetch('./'+name);if(!r.ok)throw Error(name+': HTTP'+r.status);
      const bytes=await r.arrayBuffer();const hash=await crypto.subtle.digest('SHA-256',bytes);
      assets.push({name,status:r.status,size:bytes.byteLength,sha256:[...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('')});
    }
    return {url:location.href,model:document.getElementById('model').value,state:document.getElementById('run-state').textContent,detail:document.getElementById('run-detail').textContent,assets};
  });
}
