async (page) => {
 const base='/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v1/';
 const errors=[],failed=[]; page.on('pageerror',e=>errors.push(String(e))); page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()})});
 const wait=async()=>{await page.waitForFunction(()=>document.querySelector('#response-charts').getAttribute('aria-busy')==='false'&&!document.querySelector('#export-run').disabled);};
 const save=async(name)=>{const d=page.waitForEvent('download');await page.locator('#export-run').click();await(await d).saveAs(base+name+'.json');};
 const out={};
 if(!await page.locator('#state-e').isVisible()) await page.getByText('Initial state details',{exact:true}).click();
 if(!await page.locator('#param-c1').isVisible()) await page.getByText('Material parameters Adjust',{exact:false}).click();
 out.inputs=await page.locator('input[id^="state-"],input[id^="param-"]').evaluateAll(xs=>xs.map(x=>({id:x.id,value:x.value})));
 await page.locator('#param-c1').fill('-1.02'); await page.locator('#state-e').fill('0.74');await wait();await save('edited');
 await page.locator('#target').fill('0.3');await page.locator('#target').fill('0.4');await page.locator('#target').fill('0.5');await wait();await save('latest-request');
 await page.locator('#state-e').fill('0.35');
 await page.waitForFunction(()=>document.querySelector('#response-charts').getAttribute('aria-busy')==='false'&&document.querySelector('#export-run').disabled);
 out.invalid={status:await page.locator('#run-state').innerText(),text:await page.locator('#response-charts').innerText(),disabled:await page.locator('#export-run').isDisabled()};
 await page.getByRole('button',{name:'Reset',exact:true}).click();await wait();await save('reset-recovery');
 await page.locator('#run-file').setInputFiles(base+'edited.json');await wait();await save('import-replayed');
 await page.getByRole('button',{name:'Reset',exact:true}).click();await wait();
 await page.locator('#experiment-select').selectOption({index:1});
 out.overlay={note:await page.locator('#experiment-filter-note').innerText(),checked:await page.locator('#show-experiment').isChecked()};
 await page.locator('#show-experiment').check();out.overlay.onCurves=await page.locator('svg polyline').count();
 await page.locator('#show-experiment').uncheck();out.overlay.offCurves=await page.locator('svg polyline').count();
 await page.getByText('Sources & model definition',{exact:true}).click();
 await page.getByText('Equations & source provenance',{exact:true}).click();
 out.links=await page.locator('a').evaluateAll(xs=>xs.map(x=>({text:x.innerText,href:x.getAttribute('href')})).filter(x=>/doi|review|definition|dossier|barodesy/i.test(x.text+' '+x.href)));
 out.text=await page.locator('main').innerText();out.errors=errors;out.failed=failed;
 await page.screenshot({path:base+'interface.png',fullPage:true});
 return out;
}
