async (page) => {
 await page.route('**/engine-sls/sls.wasm',route=>route.fulfill({status:200,contentType:'application/wasm',body:'tampered binary'}));await page.reload();await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('File identity mismatch'));
 const rejected=await page.locator('#status').textContent();if(!await page.getByRole('button',{name:'Engine unavailable',exact:true}).isDisabled())throw Error('Tampered runtime enabled');
 await page.unroute('**/engine-sls/sls.wasm');await page.reload();await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 return {rejected,recovered:await page.locator('#status').textContent()};
}
