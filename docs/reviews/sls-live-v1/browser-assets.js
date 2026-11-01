async (page) => {
 const assets=await page.evaluate(async()=>{
  const files=['sls.html','sls-review.html','sls-approval.json','sls-agent-review.json','engine-sls/identity.json','engine-sls/models.json','engine-sls/sls.js','engine-sls/sls.wasm','engine-sls/sls-comsol63-deviatoric-zero-spin-ode.json','engine-sls/package-manifest.json'];
  const out=[];for(const path of files){const response=await fetch(new URL(path,location.href),{cache:'no-store'}),bytes=await response.arrayBuffer(),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');out.push({path,status:response.status,bytes:bytes.byteLength,sha256:hash});}return out;
 });
 if(assets.some(x=>x.status!==200))throw Error('Live packaged asset missing: '+JSON.stringify(assets));
 const links=await page.locator('footer a').evaluateAll(els=>els.map(el=>({label:el.textContent,href:el.href}))),statuses=[];
 for(const link of links.filter(x=>!x.href.includes('index.html'))){try{const response=await page.request.get(link.href,{timeout:30000});statuses.push({...link,status:response.status()});}catch(error){statuses.push({...link,error:error.message});}}
 const footer=await page.locator('footer').textContent();if(!footer.includes('cf019ac6a6900d3fd6af91023cd806530d500812b100086062a91bfb1723cfcf'))throw Error('Missing frozen source digest');
 return {url:page.url(),assets,links:statuses,sourceDigestPresent:true};
}
