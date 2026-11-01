async(page)=>{
 const selector=page.getByRole('combobox',{name:'Select a model',exact:true}),checks=[];
 await page.getByText('Coefficients & complete initial history',{exact:true}).click();
 await page.locator('#sls-parameters').fill('[20000000,8000000,12000000,3]');await page.locator('#sls-initial').fill('[0.003,0.002,-0.002,0.0006,-0.0005,0.0004,4000,-1000,-3000,800,-300,200]');
 await page.getByRole('button',{name:'Run physical-time history',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete SLS run',exact:true}).click();await(await download).saveAs('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/sls-comsol63/main-atlas-v1/browser/custom.json');
 await page.locator('#sls-initial').fill('[0.003,0.002,-0.002,0.0006,-0.0005,0.0004,4001,-1000,-3000,800,-300,200]');await page.getByRole('button',{name:'Run physical-time history',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.includes('traceless'));
 if(!await page.getByRole('button',{name:'Export complete SLS run',exact:true}).isDisabled())throw Error('Invalid trace retains stale export');checks.push({invalidTrace:await page.locator('#sls-status').textContent()});
 await page.getByRole('button',{name:'Reset SLS preset',exact:true}).click();await page.locator('#sls-duration').fill('7');if(!await page.getByRole('button',{name:'Export complete SLS run',exact:true}).isDisabled())throw Error('Worker supersession retained export');
 await selector.selectOption('linear-elastic');if(await page.locator('#sls-laboratory').isVisible())throw Error('SLS remains visible after ordinary switch');
 await selector.selectOption('burgers-itasca900-dry-zero-spin-ode');if(!await page.locator('#timed-laboratory').isVisible()||await page.locator('#sls-laboratory').isVisible())throw Error('Timed interfaces overlap');
 await selector.selectOption('sls-comsol63-deviatoric-zero-spin-ode');await page.getByRole('button',{name:'Reset SLS preset',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#sls-status').textContent.startsWith('Completed'),null,{timeout:180000});
 checks.push({ordinaryBurgersSlsSwitch:'passed',latestWorker:'pending worker cancelled on input and model switches',recovery:await page.locator('#sls-status').textContent()});return {checks};
}
