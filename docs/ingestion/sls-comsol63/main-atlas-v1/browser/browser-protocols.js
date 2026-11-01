async(page)=>{
 const checks=[];for(const mode of ['creep','rate']){
  await page.locator('#sls-mode').selectOption(mode);if(mode==='rate')await page.locator('#sls-duration').fill('1');
  await page.getByRole('button',{name:'Run physical-time history',exact:true}).click();await page.waitForFunction(m=>document.querySelector('#sls-status').textContent.includes('· '+m+'.'),mode,{timeout:180000});
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete SLS run',exact:true}).click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/sls-comsol63/main-atlas-v1/browser/'+mode+'.json');checks.push({mode,status:await page.locator('#sls-status').textContent()});
 }
 await page.getByRole('button',{name:'Reset SLS preset',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete SLS run',exact:true}).click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/sls-comsol63/main-atlas-v1/browser/reset.json');return {checks,reset:await page.locator('#sls-status').textContent()};
}
