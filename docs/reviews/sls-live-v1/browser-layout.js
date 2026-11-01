async (page) => {
 const states=[];
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:844});await page.evaluate(()=>scrollTo(0,0));
  const state=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight}));if(state.viewport!==state.document)throw Error('Horizontal overflow at '+width);states.push(state);
  await page.screenshot({path:`output/playwright/sls-live-${width}-top.png`});
  await page.getByRole('heading',{name:'Total Cauchy stress',exact:true}).scrollIntoViewIfNeeded();await page.screenshot({path:`output/playwright/sls-live-${width}-results.png`});
 }
 await page.setViewportSize({width:1280,height:900});return {url:page.url(),states,plots:await page.locator('svg polyline').count()};
}
