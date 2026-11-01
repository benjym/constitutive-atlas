async (page) => {
 await page.getByRole('combobox',{name:'Control on all six components',exact:true}).selectOption('rate');await page.getByLabel('Duration (s)',{exact:true}).fill('1');await page.getByRole('button',{name:'Run experiment',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('· rate.'),null,{timeout:180000});
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export request & full result',exact:true}).click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/reviews/sls-live-v1/browser-rate.json');
 await page.getByRole('button',{name:'Reset illustrative preset',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 return {url:page.url(),rate:'completed',reset:await page.locator('#status').textContent()};
}
