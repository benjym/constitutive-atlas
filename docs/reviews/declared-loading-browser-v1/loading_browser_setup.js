async(page)=>{
 await page.addInitScript(()=>{window.__wires=[];const Native=window.Worker;window.Worker=class extends Native{constructor(...args){super(...args);this.addEventListener('message',e=>window.__wires.push({direction:'response',data:structuredClone(e.data)}));}postMessage(data,...args){window.__wires.push({direction:'request',data:structuredClone(data)});return super.postMessage(data,...args);}};});
 await page.reload();await page.waitForFunction(()=>window.__wires.some(x=>x.direction==='response')&&!document.querySelector('#export-run').disabled);
 const audit=await page.evaluate(async()=>{
  const cat=await(await fetch('./models.json')).json();const digest=async name=>{const bytes=await(await fetch('./'+name)).arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');};
  return{catalogue:cat,asset_hashes:{'atlas.js':await digest('atlas.js'),'atlas.wasm':await digest('atlas.wasm')},wires:window.__wires,publications:(await(await fetch('./publications.json')).json()).publications.length};
 });
 if(audit.catalogue.models.length!==11||audit.publications!==17)throw Error('Wrong canonical catalogue/publications');
 const fs=await import('node:fs/promises');await fs.mkdir('output/playwright/loading-rollout',{recursive:true});await fs.writeFile('output/playwright/loading-rollout/setup.json',JSON.stringify(audit,null,2));
 return {models:audit.catalogue.models.length,publications:audit.publications,engine_hashes:audit.asset_hashes,first_response_ok:audit.wires.find(w=>w.direction==='response').data.result.ok};
}
