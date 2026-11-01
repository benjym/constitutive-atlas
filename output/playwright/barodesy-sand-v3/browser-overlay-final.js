async(page)=>{
 await page.goto('http://127.0.0.1:56013/constitutive-atlas/#laboratory?model=barodesy-sand');
 const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v3/';
 await page.waitForFunction(()=>!document.querySelector('#export-run').disabled);
 if(!await page.locator('#experiment-select').isVisible())await page.locator('#measurements > summary').click();
 await page.locator('#experiment-select').selectOption({index:1});
 await page.waitForFunction(()=>!document.querySelector('#show-experiment').disabled&&document.querySelector('#experiment-status').textContent.includes(' rows'));
 const inspect=()=>page.locator('#response-charts').evaluate(x=>({text:x.innerText,lines:[...x.querySelectorAll('polyline')].map(p=>({stroke:p.getAttribute('stroke'),points:p.getAttribute('points').split(' ').length,display:getComputedStyle(p).display}))}));
 await page.locator('#show-experiment').check();const on=await inspect();await page.screenshot({path:base+'overlay-on.png',fullPage:true});
 await page.locator('#show-experiment').uncheck();const off=await inspect();await page.screenshot({path:base+'overlay-off.png',fullPage:true});
 return {on,off,warning:await page.locator('#experiment-status').innerText(),filter:await page.locator('#experiment-filter-note').innerText()};
}
