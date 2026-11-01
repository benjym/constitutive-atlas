async (page) => {
 await page.getByRole('searchbox',{name:'Search models',exact:true}).fill('sls-comsol63');
 const entry=page.getByRole('link',{name:'Standard Linear Solid / Zener — COMSOL6.3 deviatoric',exact:true});await entry.waitFor();await entry.click();
 const timed=page.getByRole('link',{name:'Open physical-time laboratory ↗',exact:true});await timed.waitFor();const href=await timed.getAttribute('href');if(href!=='./sls.html')throw Error('Wrong dedicated laboratory link');await timed.click();
 await page.waitForURL('**/sls.html');await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 const sourceDigest='cf019ac6a6900d3fd6af91023cd806530d500812b100086062a91bfb1723cfcf';if(!await page.locator('footer').textContent().then(s=>s.includes(sourceDigest)))throw Error('Missing source digest');
 return {catalogueRoute:href,url:page.url(),defaultStatus:await page.locator('#status').textContent(),sourceDigest,identity:JSON.parse(await page.locator('#identity').textContent())};
}
