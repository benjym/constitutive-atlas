async(page)=>{
 const h=page.locator('#orthotropic-material-laboratory'),q=id=>h.locator('#'+id),base='/Users/bmar5496/code/constitutive-atlas/docs/ingestion/orthotropic-ogs/browser-v1/',selector=page.locator('#model'),checks=[];
 const complete=()=>page.waitForFunction(()=>document.getElementById('orthotropic-material-laboratory').shadowRoot.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 const names=['E1','E2','E3','G12','G23','G13','nu12','nu23','nu13'],values=[40e6,55e6,70e6,13e6,19e6,16e6,.18,.22,.12];for(let i=0;i<9;i++)await q(names[i]).fill(String(values[i]));
 await q('initial').fill('120000,-230000,340000,45000,-56000,67000');await q('increments').fill('0.0007,-0.0004,0.0002,-0.0003,0.0006,-0.0005\n-0.0002,0.0003,-0.0001,0.0004,-0.0002,0.0006\n0,0,0,0,0,0');
 for(const name of ['custom','custom-fresh']){await q('run').click();await complete();const d=page.waitForEvent('download');await q('download').click();await(await d).saveAs(base+name+'.json');}
 await q('nu12').fill('2');await q('run').click();await page.waitForFunction(()=>document.getElementById('orthotropic-material-laboratory').shadowRoot.querySelector('#status').textContent.includes('positive definite'));
 if(!await q('download').isDisabled())throw Error('Invalid compliance retained stale export');checks.push({invalidCompliance:await q('status').textContent()});await q('resetPreset').click();await complete();
 const long=Array(200).fill('0.001,-0.0002,0.0003,0.0004,-0.0005,0.0006').join('\n');await q('increments').fill(long);await q('run').click();await q('increments').fill('0.001,-0.0002,0.0003,0.0004,-0.0005,0.0006\n0,0,0,0,0,0');if(!await q('download').isDisabled())throw Error('Input edit retained stale export');await q('run').click();await complete();if(await q('stepValue').textContent()!=='2 / 2')throw Error('Stale long run replaced latest request');
 const d=page.waitForEvent('download');await q('download').click();await(await d).saveAs(base+'latest.json');
 await q('increments').fill(long);await q('run').click();await selector.selectOption('linear-elastic');if(await h.isVisible()||!await page.locator('#laboratory > .lab-layout').isVisible())throw Error('Ordinary switch failed');
 await selector.selectOption('sls-comsol63-deviatoric-zero-spin-ode');if(!await page.locator('#sls-laboratory').isVisible()||await h.isVisible())throw Error('SLS switch overlaps orthotropic');
 await selector.selectOption('orthotropic-linear-elastic-ogs');await q('resetPreset').click();await complete();if(await page.locator('#sls-laboratory').isVisible()||await page.locator('#laboratory > .lab-layout').isVisible())throw Error('Orthotropic return overlaps other laboratory');
 checks.push({customAllNineParametersAndSixInitialAndIncrementComponents:true,exactFreshRun:'exports compared offline',latestTwoRowRequest:true,ordinarySlsOrthotropicSwitch:true,resetRecovery:await q('status').textContent()});return {checks};
}
