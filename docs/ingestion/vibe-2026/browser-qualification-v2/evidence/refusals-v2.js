async(page)=>{
 const out=[];
 const details=page.locator('#ct-state').locator('..');
 if(await details.getAttribute('open')===null) await page.getByText('Complete starting state, imposed fields and incoming rates',{exact:true}).click();
 for(const value of ['0','-1']){
  await page.getByRole('spinbutton',{name:'Suction (Pa)',exact:true}).fill(value);
  const staleExportDisabled=await page.getByRole('button',{name:'Export complete run',exact:true}).isDisabled();if(!staleExportDisabled)throw Error('Stale export');
  await page.getByRole('button',{name:'Run history',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#ct-status').textContent.startsWith('Run failed'),{},{timeout:120000});out.push({value,status:await page.locator('#ct-status').textContent(),staleExportDisabled});
  await page.getByRole('button',{name:'Reset starting example',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#ct-status').textContent.startsWith('History completed'),{},{timeout:120000});out.push({recoveryAfter:value,status:await page.locator('#ct-status').textContent()});
 }
 return out;
}
