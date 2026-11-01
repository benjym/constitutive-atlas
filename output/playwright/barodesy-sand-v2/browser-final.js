async(page)=>{
 const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v2/';
 const responses=[],errors=[];page.on('response',r=>responses.push({url:r.url(),status:r.status()}));page.on('requestfailed',r=>errors.push({url:r.url(),error:r.failure()}));page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:56013/constitutive-atlas/#laboratory?model=barodesy-sand');
 await page.reload();
 await page.waitForFunction(()=>!document.querySelector('#export-run').disabled&&document.querySelector('#model').value==='barodesy-sand');
 const out={responses,errors,status:await page.locator('#model-status').innerText(),run:await page.locator('#run-state').innerText()};
 await page.screenshot({path:base+'default-fresh-final.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:base+'mobile-fresh-final.png',fullPage:true});
 out.mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
 await page.setViewportSize({width:1280,height:900});
 return out;
}
