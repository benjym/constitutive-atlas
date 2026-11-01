async(page)=>{
 await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});
 const selected=await page.locator('#model').inputValue();if(selected!=='sls-comsol63-deviatoric-zero-spin-ode'||!await page.locator('#sls-laboratory').isVisible()||await page.locator('#timed-laboratory').isVisible()||await page.locator('#laboratory > .lab-layout').isVisible())throw Error('Catalogue did not route to SLS main laboratory');
 const assets=await page.evaluate(async()=>{const a=[];for(const path of ['app.js','catalogue.json']){const r=await fetch('./'+path),b=await r.arrayBuffer(),sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');a.push({path,status:r.status,sha256});}return a;});
 const download=page.waitForEvent('download');await page.locator('#sls-export').click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/sls-comsol63/main-atlas-v1/browser/final-v3-default.json');
 await page.locator('#sls-controls').evaluate(el=>el.scrollTop=0);await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'output/playwright/sls-main-final-v3.png'});
 return {url:page.url(),selected,actualCatalogueExplore:true,status:await page.locator('#sls-status').textContent(),assets};
}
