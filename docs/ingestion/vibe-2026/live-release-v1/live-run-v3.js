async (page) => {
 await page.getByRole('combobox',{name:'Starting example',exact:true}).selectOption('0');
 await page.getByRole('button',{name:'Run history',exact:true}).click();
 await page.waitForFunction(()=>/^(History completed|Run failed)/.test(document.querySelector('#ct-status').textContent),{},{timeout:120000});
 const status=await page.locator('#ct-status').textContent();if(!status.startsWith('History completed'))throw Error(status);
 const event=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete run',exact:true}).click();const download=await event;
 await download.saveAs('output/playwright/vibe-live-v3/default-run.json');
 const plots=await page.locator('#ct-stress polyline,#ct-void polyline,#ct-saturation polyline').count();if(plots!==3)throw Error('Expected3plots, got'+plots);
 return {url:page.url(),status,summary:await page.locator('#ct-summary').textContent(),plots};
}
