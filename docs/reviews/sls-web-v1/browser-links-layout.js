async (page) => {
 const links=await page.locator('footer a').evaluateAll(els=>els.map(el=>({label:el.textContent,href:el.href})));
 const local=[];for(const link of links.filter(x=>x.href.startsWith('http://127.0.0.1:18769')&&!x.href.includes('index.html'))){const res=await page.request.get(link.href);if(res.status()!==200)throw Error('Missing '+link.href);local.push({url:link.href,status:res.status()});}
 if(!links.some(x=>x.href==='https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html#3441011'))throw Error('Wrong primary source URL');
 await page.getByText('Inspect complete state and stress at every output',{exact:true}).click();
 await page.setViewportSize({width:1280,height:900});let desktop=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));if(desktop.viewport!==desktop.document)throw Error('Desktop horizontal overflow');await page.screenshot({path:'output/playwright/sls-desktop-final.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});let narrow=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));if(narrow.viewport!==narrow.document)throw Error('Narrow horizontal overflow');await page.screenshot({path:'output/playwright/sls-narrow.png',fullPage:true});
 await page.setViewportSize({width:1280,height:900});
 return {links,local,desktop,narrow,identity:JSON.parse(await page.locator('#identity').textContent())};
}
