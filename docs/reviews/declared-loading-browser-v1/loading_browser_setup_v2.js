async(page)=>{
 const audit=await page.evaluate(async()=>{
  const cat=await(await fetch('./models.json')).json();const digest=async name=>{const bytes=await(await fetch('./'+name)).arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');};
  return{catalogue:cat,asset_hashes:{'atlas.js':await digest('atlas.js'),'atlas.wasm':await digest('atlas.wasm')},wires:window.__wires,publications:(await(await fetch('./publications.json')).json()).publications.length};
 });
 if(audit.catalogue.models.length!==11||audit.publications!==17)throw Error('Wrong canonical catalogue/publications');
 const pending=page.waitForEvent('download');await page.evaluate(audit=>{const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([JSON.stringify(audit,null,2)],{type:'application/json'}));link.download='setup.json';link.click();},audit);await(await pending).saveAs('output/playwright/loading-rollout/setup.json');
 return {models:audit.catalogue.models.length,publications:audit.publications,engine_hashes:audit.asset_hashes,first_response_ok:audit.wires.find(w=>w.direction==='response').data.result.ok};
}
