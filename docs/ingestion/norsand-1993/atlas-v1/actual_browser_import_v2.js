async (page) => {
 const check=(ok,label)=>{if(!ok)throw Error(label);},done=()=>page.locator('#path-status').filter({hasText:'Completed drained axial history.'}).waitFor({timeout:20000});
 await done();const initial=await page.locator('#path-state').textContent(),identity=JSON.parse(await page.locator('#path-identities').textContent());
 const upload=async name=>{await page.locator('#path-file').setInputFiles('/private/tmp/atlas-norsand-main-atlas-v1/'+name);};
 await upload('default-run.json');await done();check(await page.locator('#path-state').textContent()===initial,'exact imported replay');const event=page.waitForEvent('download');await page.locator('#path-export').click();await(await event).saveAs('/private/tmp/atlas-norsand-main-atlas-v1/replayed-run.json');
 await upload('bad-identity.json');await page.locator('#path-status').filter({hasText:'Import rejected: Imported model/engine/review identity differs.'}).waitFor();check(await page.locator('#path-export').isDisabled(),'badidentity export absent');
 await upload('bad-context.json');await page.locator('#path-status').filter({hasText:'Import rejected: Incomplete state.'}).waitFor();
 await upload('bad-result.json');await page.locator('#path-status').filter({hasText:'Replay rejected: results differ.'}).waitFor({timeout:20000});check(await page.locator('#path-state tr').count()===0,'bad replay never publishes table');
 await page.locator('#path-reset').click();await done();check(await page.locator('#path-state').textContent()===initial,'tamper recovery');
 // Catalogue route opens actual source/review details and its laboratory action.
 await page.goto('http://127.0.0.1:18781/site-v2/index.html#catalogue/'+identity.model);await page.locator('#catalogue-dialog[open]').waitFor();check((await page.locator('#catalogue-detail-status').textContent()).includes('controlled-path'),'honest catalogue profile');check((await page.locator('#catalogue-detail-body').textContent()).includes('drained active axial'),'catalogue exact scope');await page.locator('#catalogue-explore').click();await done();
 // Fetch the actual browser-visible bytes and independently digest every declared asset.
 const fetched=await page.evaluate(async identity=>{
  const hash=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');const files={};
  for(const [name,expected]of [...Object.entries(identity.files).map(([n,h])=>['engine-path/'+n,h]),...Object.entries(identity.components)]){const r=await fetch('./'+name,{cache:'reload'});if(!r.ok)throw Error(name);const actual=await hash(await r.arrayBuffer());if(actual!==expected)throw Error('Fetched hash '+name);files[name]=actual;}
  for(const name of ['index.html','app.js','catalogue.json','atlas.sqlite','atlas-database-manifest.json']){const r=await fetch('./'+name,{cache:'reload'});if(!r.ok)throw Error(name);files[name]=await hash(await r.arrayBuffer());}return files;
 },identity);
 await page.screenshot({path:'output/playwright/norsand-v1/final-catalogue-return.png',fullPage:true});
 return {result:'PASS',actual_import_replay:true,exported_replay_saved:true,identity_tamper_rejected:true,missing_state_rejected:true,result_tamper_rejected:true,recovery:true,catalogue_route:true,fetched};
}
