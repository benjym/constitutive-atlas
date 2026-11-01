async (page) => {
 await page.waitForLoadState('networkidle');
 const errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('requestfailed',r=>failed.push(r.url()+': '+r.failure()?.errorText));page.on('response',r=>{if(r.status()>=400)failed.push(r.status()+' '+r.url());});
 await page.goto('http://127.0.0.1:18781/site-v2/index.html?qualification=norsand-v6#laboratory?model=norsand-jefferies-1993-active-axial');
 const lifecycle=await (async (page) => {
 const check=(ok,label)=>{if(!ok)throw Error(label);},done=()=>page.locator('#path-status').filter({hasText:'Completed drained axial history.'}).waitFor({timeout:20000});
 await done();const initial=await page.locator('#path-state').textContent(),identity=JSON.parse(await page.locator('#path-identities').textContent());
 check(await page.locator('#model').inputValue()===identity.model,'share URL model');
 check((await page.locator('.model-meta').textContent()).includes('Fixed axial frame'),'axial header');
 check(await page.locator('#path-q polyline').count()>0&&await page.locator('#path-volume polyline').count()>0&&await page.locator('#path-image polyline').count()>0,'three plotted curves');
 check(await page.locator('#path-state tr').count()===42,'complete41point state table');
 await page.locator('#path-equations summary').click();check((await page.locator('#path-source').textContent()).includes('Jefferies'),'source and review visible');
 await page.screenshot({path:'output/playwright/norsand-v6/default-desktop.png',fullPage:true});
 // A real download event captures the complete UI export.
 const downloadPromise=page.waitForEvent('download');await page.locator('#path-export').click();const download=await downloadPromise;await download.saveAs('/private/tmp/atlas-norsand-main-atlas-v1/default-run.json');
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
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'output/playwright/norsand-v6/default-mobile.png',fullPage:true});await page.setViewportSize({width:1440,height:1000});
 return {result:'PASS',model:identity.model,identity,default_summary:await page.locator('#path-summary').textContent(),default_points:41,plots:3,actual_download:true,invalid_recovery:true,parameter_state_edits:true,mean_and_changing_controls:true,latest_request:true,ordinary_return:true,desktop_mobile_captured:true};
})(page);
 const imported=await (async (page) => {
 const check=(ok,label)=>{if(!ok)throw Error(label);},done=()=>page.locator('#path-status').filter({hasText:'Completed drained axial history.'}).waitFor({timeout:20000});
 await done();const initial=await page.locator('#path-state').textContent(),identity=JSON.parse(await page.locator('#path-identities').textContent());
 const upload=async name=>{await page.locator('#path-file').setInputFiles('/private/tmp/atlas-norsand-main-atlas-v1/'+name);};
 await upload('default-run.json');await done();check(await page.locator('#path-state').textContent()===initial,'exact imported replay');const event=page.waitForEvent('download');await page.locator('#path-export').click();await(await event).saveAs('/private/tmp/atlas-norsand-main-atlas-v1/replayed-run.json');
 await upload('bad-identity.json');await page.locator('#path-status').filter({hasText:'Import rejected: Imported model/engine/review identity differs.'}).waitFor();check(await page.locator('#path-export').isDisabled(),'badidentity export absent');
 await upload('bad-context.json');await page.locator('#path-status').filter({hasText:'Import rejected: Incomplete state.'}).waitFor();
 await upload('bad-result.json');await page.locator('#path-status').filter({hasText:'Replay rejected: results differ.'}).waitFor({timeout:20000});check(await page.locator('#path-state tr').count()===0,'bad replay never publishes table');
 await page.locator('#path-reset').click();await done();check(await page.locator('#path-state').textContent()===initial,'tamper recovery');
 // Catalogue route opens actual source/review details and its laboratory action.
 await page.locator('a[href="#catalogue"]').first().click();await page.locator('a.catalogue-open[href="#catalogue/'+identity.model+'"]').click();await page.locator('#catalogue-dialog[open]').waitFor();check((await page.locator('#catalogue-detail-status').textContent()).includes('controlled-path'),'honest catalogue profile');check((await page.locator('#catalogue-detail-body').textContent()).includes('drained active axial'),'catalogue exact scope');await page.locator('#catalogue-explore').click();await done();
 // Fetch the actual browser-visible bytes and independently digest every declared asset.
 const fetched=await page.evaluate(async identity=>{
  const hash=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');const files={};
  for(const [name,expected]of [...Object.entries(identity.files).map(([n,h])=>['engine-path/'+n,h]),...Object.entries(identity.components)]){const r=await fetch('./'+name,{cache:'reload'});if(!r.ok)throw Error(name);const actual=await hash(await r.arrayBuffer());if(actual!==expected)throw Error('Fetched hash '+name);files[name]=actual;}
  for(const name of ['index.html','app.js','catalogue.json','atlas.sqlite','atlas-database.json']){const r=await fetch('./'+name,{cache:'reload'});if(!r.ok)throw Error(name);files[name]=await hash(await r.arrayBuffer());}return files;
 },identity);
 await page.screenshot({path:'output/playwright/norsand-v6/final-catalogue-return.png',fullPage:true});
 return {result:'PASS',actual_import_replay:true,exported_replay_saved:true,identity_tamper_rejected:true,missing_state_rejected:true,result_tamper_rejected:true,recovery:true,catalogue_route:true,fetched};
})(page);
 if(errors.length||failed.length)throw Error(JSON.stringify({errors,failed}));
 return {result:'PASS',lifecycle,imported,browser_errors:errors,network_failures:failed};
}
