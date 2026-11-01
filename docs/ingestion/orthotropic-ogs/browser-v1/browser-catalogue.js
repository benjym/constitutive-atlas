async(page)=>{
 await page.getByRole('link',{name:/Model catalogue/}).click();const card=page.locator('a.catalogue-open[href*="orthotropic-linear-elastic-ogs"]');await card.click();
 const dialogTitle=await page.locator('#catalogue-detail-title').textContent();await page.locator('#catalogue-explore').click();
 await page.waitForFunction(()=>document.getElementById('orthotropic-material-laboratory').shadowRoot.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 if(await page.locator('#model').inputValue()!=='orthotropic-linear-elastic-ogs'||!await page.locator('#orthotropic-material-laboratory').isVisible()||await page.locator('#laboratory > .lab-layout').isVisible())throw Error('Catalogue Explore did not open embedded orthotropic');
 return {url:page.url(),dialogTitle,actualCatalogueCardAndExplore:true,selected:await page.locator('#model').inputValue()};
}
