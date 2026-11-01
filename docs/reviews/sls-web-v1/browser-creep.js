async (page) => {
 await page.getByRole('combobox',{name:'Control on all six components',exact:true}).selectOption('creep');
 if(!await page.getByRole('button',{name:'Export request & full result',exact:true}).isDisabled())throw Error('Stale export on edit');
 await page.getByRole('button',{name:'Run experiment',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('· creep.'),null,{timeout:180000});
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export request & full result',exact:true}).click();await (await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/reviews/sls-web-v1/browser-creep.json');
 await page.getByRole('combobox',{name:'Plot component · Mandel',exact:true}).selectOption({index:5});
 console.log(JSON.stringify({check:'creep',status:await page.locator('#status').textContent(),plots:await page.locator('svg polyline').count(),selected:await page.locator('#component').inputValue()}));
}
