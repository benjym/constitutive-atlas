async(page)=>{
const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-live-v3/';
const errors=[],warnings=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());if(m.type()==='warning')warnings.push(m.text());});
await page.goto('https://benjym.github.io/constitutive-atlas/#laboratory?model=barodesy-sand');
await page.waitForFunction(()=>document.querySelector('#model').value==='barodesy-sand'&&!document.querySelector('#export-run').disabled&&document.querySelector('#response-charts').getAttribute('aria-busy')==='false');
const download=page.waitForEvent('download');await page.locator('#export-run').click();await(await download).saveAs(base+'default.json');
const run={status:await page.locator('#run-state').innerText(),model:await page.locator('#model').inputValue(),curves:await page.locator('svg polyline').count()};
await page.screenshot({path:base+'live-laboratory.png',fullPage:true});await page.locator('#response-charts').screenshot({path:base+'live-response-closeup.png'});
await page.goto('https://benjym.github.io/constitutive-atlas/#catalogue/barodesy-sand');await page.locator('#catalogue-detail-body .model-profile').waitFor();
await page.locator('#catalogue-detail-body .technical-review-links a').first().waitFor({state:'attached'});
const profile=await page.locator('#catalogue-detail-body').evaluate(x=>({text:x.querySelector('.model-profile').innerText,technicalOpen:x.querySelector('.model-profile-technical').open,links:[...x.querySelectorAll('.technical-review-links a')].map(a=>({text:a.innerText,href:a.getAttribute('href')}))}));
const fetched=await page.evaluate(async paths=>{const rows=[];for(const path of paths){const r=await fetch(path);const raw=await r.arrayBuffer();rows.push({path,status:r.status,sha256:[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(x=>x.toString(16).padStart(2,'0')).join('')});}return rows;},profile.links.map(x=>x.href));
await page.screenshot({path:base+'live-profile.png',fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:base+'live-profile-mobile.png',fullPage:true});await page.locator('#catalogue-dialog').screenshot({path:base+'live-profile-mobile-closeup.png'});
const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,dialogWidth:document.querySelector('#catalogue-dialog').getBoundingClientRect().width}));
await page.setViewportSize({width:1280,height:900});
await page.locator('#catalogue-detail-body a[href="#catalogue/barodesy-clay-2017"]').click();
await page.waitForFunction(()=>location.hash==='#catalogue/barodesy-clay-2017'&&document.querySelector('#catalogue-detail-title').innerText.includes('clay'));
const navigation={related_model:new URL(page.url()).hash};
await page.goto('https://benjym.github.io/constitutive-atlas/#catalogue/barodesy-sand');await page.locator('#catalogue-detail-body .model-profile').waitFor();
await page.locator('#catalogue-explore').click();await page.waitForFunction(()=>document.querySelector('#model').value==='barodesy-sand'&&!document.querySelector('#export-run').disabled);navigation.laboratory_model=await page.locator('#model').inputValue();
return {run,profile,fetched,mobile,navigation,errors,warnings};
}