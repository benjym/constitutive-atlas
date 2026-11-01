async(page)=>{
 await page.locator('#equations-button').click();if(!await page.locator('#sls-equations').evaluate(el=>el.open))throw Error('Shared equations button did not route to SLS');
 const links=await page.locator('#sls-equations a').evaluateAll(els=>els.map(el=>({text:el.textContent,href:el.href}))),statuses=[];
 for(const link of links){try{const response=await page.request.get(link.href,{timeout:30000});statuses.push({...link,status:response.status()});}catch(error){statuses.push({...link,error:error.message});}}
 if(statuses.filter(x=>x.href.startsWith(new URL(page.url()).origin)).some(x=>x.status!==200))throw Error('Missing SLS review/approval/model');
 const states=[];for(const width of [1280,390]){await page.setViewportSize({width,height:844});await page.evaluate(()=>scrollTo(0,0));const state=await page.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth}));if(state.viewport!==state.width)throw Error('Atlas horizontal overflow at'+width);states.push(state);await page.screenshot({path:`output/playwright/sls-main-${width}-top.png`});await page.locator('#sls-stress').scrollIntoViewIfNeeded();await page.screenshot({path:`output/playwright/sls-main-${width}-results.png`});}
 await page.setViewportSize({width:1280,height:900});return {url:page.url(),links:statuses,states,identities:JSON.parse(await page.locator('#sls-identities').textContent())};
}
