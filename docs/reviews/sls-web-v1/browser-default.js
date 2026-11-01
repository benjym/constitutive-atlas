async (page) => {
 await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 await page.getByText('Inspect complete state and stress at every output',{exact:true}).click();
 const state = await page.locator('#stateTable').evaluate(el=>({rows:el.rows.length,columns:el.rows[0].cells.length,last:[...el.rows[el.rows.length-1].cells].map(x=>x.textContent)}));
 if(state.rows!==7||state.columns!==19)throw Error('Incomplete state table');
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export request & full result',exact:true}).click();await (await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/reviews/sls-web-v1/browser-default.json');
 await page.screenshot({path:'output/playwright/sls-desktop.png',fullPage:true});
 console.log(JSON.stringify({check:'default',status:await page.locator('#status').textContent(),state,plots:await page.locator('svg polyline').count()}));
}
