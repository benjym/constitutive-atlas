async(page)=>{
 const base='/Users/bmar5496/code/constitutive-atlas/docs/ingestion/sls-comsol63/main-atlas-v1/browser/',checks=[];
 for(let i=0;i<2;i++){
  await page.locator('#sls-file').setInputFiles(base+'default.json');await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});
  if(await page.locator('#sls-file').inputValue()!=='')throw Error('Consumed file not cleared; repeat selection can fail');checks.push({sameFileReplay:i+1,status:await page.locator('#sls-status').textContent()});
 }
 let download=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete SLS run',exact:true}).click();await(await download).saveAs(base+'replayed.json');
 await page.locator('#sls-file').setInputFiles(base+'finite-tamper.json');await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.includes('differs from saved output'),null,{timeout:180000});
 if(!await page.getByRole('button',{name:'Export complete SLS run',exact:true}).isDisabled())throw Error('Finite-tampered replay publishes export');checks.push({tamperedReplay:await page.locator('#sls-status').textContent()});
 await page.locator('#sls-file').setInputFiles(base+'default.json');await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});return {checks,recovery:await page.locator('#sls-status').textContent()};
}
