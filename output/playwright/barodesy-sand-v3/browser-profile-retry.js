async(page)=>{
 const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v3/';
 await page.goto('http://127.0.0.1:56013/constitutive-atlas/#catalogue/barodesy-sand');
 await page.locator('#catalogue-dialog').waitFor({state:'visible'});
 const body=page.locator('#catalogue-detail-body');await body.locator('.model-profile').waitFor();
 const out={title:await page.locator('#catalogue-detail-title').innerText(),text:await body.locator('.model-profile').innerText(),rows:await body.locator('.model-profile tbody tr').allTextContents(),technicalInitiallyClosed:!await body.locator('.model-profile-technical').evaluate(x=>x.open),links:await body.locator('a').evaluateAll(xs=>xs.map(x=>({text:x.innerText,href:x.getAttribute('href')})))};
 if(out.rows.length!==7||!out.technicalInitiallyClosed||!out.text.includes('Pressure-stiffening slope'))throw Error('Profile presentation mismatch');
 await page.screenshot({path:base+'public-profile.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});
 out.mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,dialogWidth:document.querySelector('#catalogue-dialog').getBoundingClientRect().width}));
 await page.screenshot({path:base+'public-profile-mobile.png',fullPage:true});
 await page.setViewportSize({width:1280,height:900});
 await body.locator('.model-profile-technical > summary').click();out.technicalText=await body.locator('.model-profile-technical').innerText();
 await page.locator('#catalogue-explore').click();
 await page.waitForFunction(()=>document.querySelector('#model').value==='barodesy-sand'&&!document.querySelector('#export-run').disabled);
 out.laboratory={url:page.url(),model:await page.locator('#model').inputValue(),run:await page.locator('#run-state').innerText()};
 return out;
}
