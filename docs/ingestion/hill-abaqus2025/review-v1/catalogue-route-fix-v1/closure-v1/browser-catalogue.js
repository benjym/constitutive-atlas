async (page) => {
 await page.goto('about:blank');
 const errors=[],consoleErrors=[],requestFailures=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});page.on('requestfailed',r=>requestFailures.push({url:r.url(),failure:r.failure()}));
 await page.goto('http://127.0.0.1:8986/index.html#laboratory?model=hill-abaqus2025-perfect-be');
 await page.evaluate(()=>{const make=URL.createObjectURL;URL.createObjectURL=function(blob){if(blob.type==='application/json')blob.text().then(t=>window.__hillExport=JSON.parse(t));return make.call(this,blob);};});
 const panel=page.locator('#hill-material-laboratory'),status=panel.locator('#status');
 await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();

 const report={url:page.url(),checks:{},identity:JSON.parse(await panel.locator('#identity').textContent())};
 const check=(k,v)=>{report.checks[k]=v;if(!v)throw Error(k);};
 check('ordinary_controls_hidden',await page.locator('#laboratory > .lab-layout').isHidden());
 check('ordinary_links_hidden',await page.locator('#laboratory > .workspace-links').isHidden());
 check('header_is_hill',(await page.locator('#model-description').textContent()).includes('Hill anisotropic'));
 check('all_seven_state_entries',await panel.locator('#stateTable tr').count()===5&&await panel.locator('#stateTable th').count()===8);
 check('meaningful_stress_plot',await panel.locator('#stressChart polyline').count()===1);
 check('no_experimental_claim',(await panel.locator('#description').textContent()).includes('All rows committed'));
 const exportRun=async file=>{await page.evaluate(()=>delete window.__hillExport);const download=page.waitForEvent('download');await panel.locator('#download').click();const d=await download;await d.saveAs(file);await page.waitForFunction(()=>window.__hillExport);return await page.evaluate(()=>window.__hillExport);};
 const first=await exportRun('/private/tmp/hill-v6-catalogue-browser-preset.json');report.preset=first;
 await panel.locator('#F').fill('1.1');await panel.locator('#run').click();await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();
 const changed=await exportRun('/private/tmp/hill-v6-catalogue-browser-changed.json');check('changed_parameter_effect',JSON.stringify(changed.points)!==JSON.stringify(first.points));
 await panel.locator('#initial').fill('1000,1000,1000,0,0,0,0');await panel.locator('#run').click();await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();
 const initialized=await exportRun('/private/tmp/hill-v6-catalogue-browser-initial.json');check('changed_initial_state',initialized.points[0].state[0]===1000);
 await panel.locator('#F').fill('-1');await panel.locator('#run').click();check('native_invalid_coefficient',await panel.locator('#F').evaluate(e=>!e.checkValidity()));check('invalid_input_blocks_export',await panel.locator('#download').isDisabled());
 await panel.locator('#resetPreset').click();await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();
 const reset=await exportRun('/private/tmp/hill-v6-catalogue-browser-reset.json');check('reset_exact',JSON.stringify(reset)===JSON.stringify(first));
 await panel.locator('#import').setInputFiles('/private/tmp/hill-v6-catalogue-browser-changed.json');await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();
 const replay=await exportRun('/private/tmp/hill-v6-catalogue-browser-replay.json');check('export_import_exact_replay',JSON.stringify(replay)===JSON.stringify(changed));
 await panel.locator('#increments').fill('0,0,0,.004,0,0\n0,0,0,-.004,0,0');await panel.locator('#run').click();await status.filter({hasText:'Completed 2 increment rows.'}).waitFor();const shear=await exportRun('/private/tmp/hill-v6-catalogue-browser-shear.json');check('shear_protocol',shear.points.at(-1).state.length===7&&shear.points[1].state[3]!==0);
 await panel.locator('#resetPreset').click();await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();
 await page.locator('#model').selectOption('linear-elastic');await page.locator('#laboratory > .lab-layout').waitFor({state:'visible'});check('ordinary_restored',await panel.isHidden());
 await page.locator('#model').selectOption('j2-linear-isotropic-hardening-be');await page.locator('#j2-material-laboratory').waitFor({state:'visible'});check('j2_coexistence',await panel.isHidden());
 await page.locator('#model').selectOption('hill-abaqus2025-perfect-be');await panel.waitFor({state:'visible'});await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();check('hill_return',await page.locator('#laboratory > .lab-layout').isHidden());
 await page.setViewportSize({width:390,height:844});check('mobile_no_document_overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
 await page.screenshot({path:'/private/tmp/hill-v6-catalogue-browser-mobile.png',fullPage:true});await page.setViewportSize({width:1400,height:1000});await page.screenshot({path:'/private/tmp/hill-v6-catalogue-browser-desktop.png',fullPage:true});
 const links=await panel.locator('footer a').evaluateAll(a=>a.map(x=>x.href));report.links=[];for(const url of links.filter(x=>new URL(x).origin===new URL(page.url()).origin&&!x.includes('#catalogue'))){const r=await page.request.get(url);report.links.push({url,status:r.status()});check('link_'+new URL(url).pathname,r.ok());}
 await page.locator('#model').selectOption('orthotropic-linear-elastic-ogs');await page.locator('#orthotropic-material-laboratory').waitFor({state:'visible'});check('orthotropic_coexists',await panel.isHidden()&&await page.locator('#laboratory > .lab-layout').isHidden());await page.locator('#model').selectOption('hill-abaqus2025-perfect-be');await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();check('hill_return_after_orthotropic',await panel.isVisible());await page.goto('http://127.0.0.1:8986/index.html#catalogue/hill-abaqus2025-perfect-be');await page.locator('#catalogue-dialog').waitFor({state:'visible'});check('catalogue_scope_label',(await page.locator('#catalogue-detail-status').textContent()).includes('strain-increment laboratory'));await page.locator('#catalogue-explore').click();await status.filter({hasText:'Completed 3 increment rows.'}).waitFor();check('catalogue_opens_main_lab',page.url().includes('#laboratory?model=hill-abaqus2025-perfect-be'));report.page_errors=errors;report.console_errors=consoleErrors;report.request_failures=requestFailures;check('no_console_errors',consoleErrors.length===0);check('no_request_failures',requestFailures.length===0);check('no_page_errors',errors.length===0);return report;
}