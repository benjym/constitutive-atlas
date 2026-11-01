async (page) => {
 await page.waitForLoadState('networkidle');
 const errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('requestfailed',r=>failed.push(r.url()+': '+r.failure()?.errorText));page.on('response',r=>{if(r.status()>=400)failed.push(r.status()+' '+r.url());});
 await page.goto('https://benjym.github.io/constitutive-atlas/?qualification=norsand-live-v2#laboratory?model=norsand-jefferies-1993-active-axial');
 const lifecycle=await (async (page) => {
 const check=(ok,label)=>{if(!ok)throw Error(label);},done=()=>page.locator('#path-status').filter({hasText:'Completed drained axial history.'}).waitFor({timeout:20000});
 await done();const initial=await page.locator('#path-state').textContent(),identity=JSON.parse(await page.locator('#path-identities').textContent());
 check(await page.locator('#model').inputValue()===identity.model,'share URL model');
 check((await page.locator('.model-meta').textContent()).includes('Fixed axial frame'),'axial header');
 check(await page.locator('#path-q polyline').count()>0&&await page.locator('#path-volume polyline').count()>0&&await page.locator('#path-image polyline').count()>0,'three plotted curves');
 check(await page.locator('#path-state tr').count()===42,'complete41point state table');
 await page.locator('#path-equations summary').click();check((await page.locator('#path-source').textContent()).includes('Jefferies'),'source and review visible');
 await page.screenshot({path:'output/playwright/norsand-live-v2/default-desktop.png',fullPage:true});
 // A real download event captures the complete UI export.
 const downloadPromise=page.waitForEvent('download');await page.locator('#path-export').click();const download=await downloadPromise;await download.saveAs('/private/tmp/atlas-norsand-live-v2/default-run.json');
 // Unsupported endpoint: no partial plot/export is exposed, then recover.
 await page.locator('#path-end-pressure_control').fill('0');await page.locator('#path-run').click();await page.locator('#path-status').filter({hasText:'Run failed:'}).waitFor();check(await page.locator('#path-export').isDisabled(),'failed run cannot export');check(await page.locator('#path-state tr').count()===0,'failed run hides prior table');await page.locator('#path-reset').click();await done();check(await page.locator('#path-state').textContent()===initial,'exact reset recovery');
 // Change a parameter and complete initial history through the exposed form.
 await page.locator('#path-controls details').nth(1).locator('summary').click();await page.locator('#path-param-h').fill('281');await page.locator('#path-initial-ev').fill('0.01');await page.locator('#path-run').click();await done();check(await page.locator('#path-state').textContent()!==initial,'parameter/history change executed');await page.locator('#path-reset').click();await done();
 // Supported mean-pressure and linearly changing controls, then recover preset.
 await page.locator('#path-start-stress_ratio_control').fill('0');await page.locator('#path-end-stress_ratio_control').fill('0');await page.locator('#path-run').click();await done();const mean=await page.locator('#path-summary').textContent();check(!mean.includes('q=234.3717'),'mean-pressure result differs');
 await page.locator('#path-end-pressure_control').fill('140000');await page.locator('#path-end-stress_ratio_control').fill('0.1');await page.locator('#path-run').click();await done();await page.locator('#path-reset').click();await done();
 // Edit immediately after submit: stale worker result must stay absent.
 await page.locator('#path-samples').fill('200');await page.locator('#path-run').click();await page.locator('#path-progress').fill('0.08');await page.waitForTimeout(500);check(await page.locator('#path-export').isDisabled(),'superseded result absent');await page.locator('#path-run').click();await done();check(await page.locator('#path-state tr').count()===202,'latest200interval result');await page.locator('#path-reset').click();await done();
 // Leave the view and return: header and ordinary controls restore correctly.
 await page.locator('#model').selectOption('linear-elastic');await page.waitForLoadState('networkidle');check(await page.locator('#path-laboratory').isHidden(),'ordinary view restored');check((await page.locator('.model-meta').textContent()).includes('3D · small strain'),'ordinary header restored');await page.locator('#model').selectOption(identity.model);await done();check(await page.locator('#path-state').textContent()===initial,'selection returns exact preset');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'output/playwright/norsand-live-v2/default-mobile.png',fullPage:true});await page.setViewportSize({width:1440,height:1000});
 return {result:'PASS',model:identity.model,identity,default_summary:await page.locator('#path-summary').textContent(),default_points:41,plots:3,actual_download:true,invalid_recovery:true,parameter_state_edits:true,mean_and_changing_controls:true,latest_request:true,ordinary_return:true,desktop_mobile_captured:true};
})(page);
 if(errors.length||failed.length)throw Error(JSON.stringify({errors,failed}));
 return {result:'PASS',lifecycle,browser_errors:errors,network_failures:failed};
}
