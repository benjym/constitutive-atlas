async (page) => {
 await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'output/playwright/norsand-live-v2/desktop-top.png'});
 const links=await page.locator('#path-source a').evaluateAll(nodes=>nodes.map(n=>({text:n.textContent,href:n.href})));
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'output/playwright/norsand-live-v2/mobile-top.png'});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);if(overflow)throw Error('Mobile horizontal overflow');await page.setViewportSize({width:1440,height:1000});return {result:'PASS',mobile_horizontal_overflow:false,links};
}
