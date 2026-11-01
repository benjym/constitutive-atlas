async (page) => {
 await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 await page.getByText('Inspect complete state and stress at every output',{exact:true}).click();
 const table=await page.locator('#stateTable').evaluate(el=>({rows:el.rows.length,columns:el.rows[0].cells.length}));
 if(table.rows!==7||table.columns!==19||await page.locator('svg polyline').count()!==2)throw Error('Incomplete default display');
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export request & full result',exact:true}).click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/reviews/sls-live-v1/browser-default.json');
 await page.screenshot({path:'output/playwright/sls-live-default.png',fullPage:true});
 return {url:page.url(),browser:page.context().browser().version(),status:await page.locator('#status').textContent(),table,identity:JSON.parse(await page.locator('#identity').textContent())};
}
