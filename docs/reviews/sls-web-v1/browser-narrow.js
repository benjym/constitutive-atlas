async (page) => {
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:'output/playwright/sls-narrow-top.png'});
 await page.getByRole('heading',{name:'Total Cauchy stress',exact:true}).scrollIntoViewIfNeeded();
 await page.screenshot({path:'output/playwright/sls-narrow-results.png'});
 const state=await page.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,scrollY,chart:document.querySelector('#stressChart').getBoundingClientRect().toJSON()}));
 if(state.viewport!==state.width)throw Error('Narrow horizontal overflow');await page.setViewportSize({width:1280,height:900});return state;
}
