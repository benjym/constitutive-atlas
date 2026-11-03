async (page) => {
 const results=[];
 for(let i=0;i<8;i++){
  await page.getByRole('combobox',{name:'Starting example',exact:true}).selectOption(String(i));
  await page.getByRole('button',{name:'Run history',exact:true}).click();
  await page.waitForFunction(()=>/^(History completed|Run failed)/.test(document.querySelector('#ct-status').textContent),{},{timeout:120000});
  const status=await page.locator('#ct-status').textContent();
  if(!status.startsWith('History completed'))throw Error('Example '+i+': '+status);
  const event=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export complete run',exact:true}).click();
  const download=await event;await download.saveAs('output/playwright/vibe-browser-v1/example-'+i+'.json');
  results.push({example:i,status,summary:await page.locator('#ct-summary').textContent(),plots:await page.locator('#ct-stress path,#ct-void path,#ct-saturation path').count(),file:'example-'+i+'.json'});
 }
 return results;
}
