async page=>{
 await page.waitForFunction(()=>{const status=document.querySelector('#ensemble-status')?.textContent;return status&&!status.includes('Running')&&!status.includes('Updating')&&document.querySelectorAll('#ensemble-runs button').length===25;},{},{timeout:90000});
 const summary=await page.evaluate(()=>({selected:document.querySelector('#ensemble-test').value,status:document.querySelector('#ensemble-status').textContent,confinementVisible:!document.querySelector('#ensemble-confinement').parentElement.hidden,charts:['stress','volume','path','pore'].map(k=>({channel:k,traces:document.querySelector('#ensemble-'+k).data?.length,measurements:document.querySelector('#ensemble-'+k).data?.[0].x.length})),errors:[...document.querySelectorAll('.chart-panel [role=status]')].map(e=>e.textContent)}));
 const downloading=page.waitForEvent('download');await page.locator('#ensemble-export').click();const download=await downloading;await download.saveAs('/private/tmp/atlas-ensemble-all-tests-v1/undrained.json');
 await page.setViewportSize({width:1440,height:1000});await page.locator('#ensemble-test').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/ensemble-all-tests-v1-undrained-desktop.png',scale:'css'});
 return summary;
}
