async(page)=>{
 await page.getByRole('combobox',{name:'Starting example',exact:true}).selectOption('2');
 if(await page.locator('#ct-state').locator('..').getAttribute('open')===null)await page.getByText('Complete starting state, imposed fields and incoming rates',{exact:true}).click();
 if(await page.locator('#ct-parameters').locator('..').getAttribute('open')===null)await page.getByText('Material parameters',{exact:true}).click();
 await page.getByRole('spinbutton',{name:'Hydraulic scanning memory (1)',exact:true}).fill('0.4');
 await page.getByRole('spinbutton',{name:'vf · viscous contribution fraction (1)',exact:true}).fill('0');
 await page.getByRole('spinbutton',{name:'Start time (s)',exact:true}).fill('12');
 await page.getByRole('spinbutton',{name:'Duration (s)',exact:true}).fill('200');
 await page.getByRole('spinbutton',{name:'Output intervals',exact:true}).fill('10');
 await page.getByRole('button',{name:'Run history',exact:true}).click();
 await page.waitForFunction(()=>/^(History completed|Run failed)/.test(document.querySelector('#ct-status').textContent),{},{timeout:120000});
 const status=await page.locator('#ct-status').textContent();if(!status.startsWith('History completed'))throw Error(status);
 const dl=page.waitForEvent('download');await page.getByRole('button',{name:'Export complete run',exact:true}).click();await(await dl).saveAs('output/playwright/vibe-browser-v1/edited-run.json');
 return {status,summary:await page.locator('#ct-summary').textContent(),fixedConstants:await page.locator('#ct-parameters input[readonly]').count(),stateInputs:await page.locator('#ct-state input').count(),startInputs:await page.locator('#ct-start input').count(),incomingInputs:await page.locator('#ct-incoming input').count(),plots:await page.locator('#ct-stress polyline,#ct-void polyline,#ct-saturation polyline').count(),tableRows:await page.locator('#ct-table tr').count(),tableHeaders:await page.locator('#ct-table th').allTextContents()};
}
