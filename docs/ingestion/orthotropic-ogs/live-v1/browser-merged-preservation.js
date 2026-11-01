async(page)=>{
 const selector=page.locator('#model'),orthotropic=page.locator('#orthotropic-material-laboratory'),options=await selector.locator('option').evaluateAll(x=>x.map(o=>({id:o.value,label:o.textContent}))),checks=[];
 for(const[id,panel]of [['lade-duncan-1975-midpoint-elastic-eq19-gap-v4','#implicit-path-laboratory'],['maxwell-itasca900-zero-spin-ode','#maxwell-laboratory']]){
  if(!options.some(x=>x.id===id))throw Error('Merged model selector entry missing: '+id);await selector.selectOption(id);await page.locator(panel).waitFor({state:'visible'});if(await orthotropic.isVisible())throw Error('Merged model panel overlaps orthotropic');checks.push({id,selectable:true,panelVisible:true});await selector.selectOption('orthotropic-linear-elastic-ogs');await orthotropic.waitFor({state:'visible'});
 }
 const q=id=>orthotropic.locator('#'+id);await q('resetPreset').click();await page.waitForFunction(()=>{const r=document.getElementById('orthotropic-material-laboratory').shadowRoot;return r.querySelector('#status').textContent.startsWith('Completed')&&!r.querySelector('#download').disabled;},null,{timeout:180000});
 const d=page.waitForEvent('download');await q('download').click();await(await d).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/orthotropic-ogs/live-v1/after-merged-switch.json');return {url:page.url(),options,checks,returnedOrthotropic:await q('status').textContent()};
}
