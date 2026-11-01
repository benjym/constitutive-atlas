async page=>{
 const assert=(v,m)=>{if(!v)throw Error(m);};
 await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:19484/#home');
 await page.reload();
 await page.waitForSelector('#home:not([hidden])');
 await page.waitForFunction(()=>document.querySelector('.home-cover-image').complete);
 await page.evaluate(()=>document.fonts.ready);
 assert(await page.locator('#home .home-kicker,#home .home-tile-number,#home .home-tile-arrow,#home .home-introduction,#home .home-scroll').count()===0,'Decorative labels, arrows, intro and scroll prompt removed');
 const text=await page.locator('#home').textContent();
 for(const removed of ['A laboratory for material behaviour','From equations to experiments','Bring their equations to life','03 / COMPARE','↗','⟶'])assert(!text.includes(removed),'Removed '+removed);
 assert(await page.locator('.home-destinations>a').count()===4,'Four destinations retained');
 assert(await page.locator('.home-destinations').evaluate(e=>getComputedStyle(e).display)==='grid','Desktop grid retained');
 await page.screenshot({path:'output/playwright/home-simplify-v2-desktop-v3.png',fullPage:true});
 await page.locator('.home-tile-ensemble').click();
 await page.waitForSelector('#ensemble:not([hidden])');
 await page.locator('.brand').click();
 await page.waitForSelector('#home:not([hidden])');
 await page.setViewportSize({width:390,height:844});
 await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 assert(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth),'Mobile no overflow');
 await page.screenshot({path:'output/playwright/home-simplify-v2-mobile-v3.png',fullPage:true});
 return {status:'passed',checks:['Removed eyebrows, numbering, decorative arrows, discover prompt and introduction','Four links retained; ensemble/brand navigation works','Desktop and390px mobile layout']};
}
