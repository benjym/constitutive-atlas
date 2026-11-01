async (page) => {
 const checks=[];
 for(const [name,expected]of [['bad-model','identity'],['bad-state','initial'],['bad-finite','parameters']]){
  await page.getByLabel('Import exported JSON & replay',{exact:true}).setInputFiles('/Users/bmar5496/code/constitutive-atlas/docs/reviews/sls-web-v1/'+name+'.json');
  await page.waitForFunction(text=>document.querySelector('#status').textContent.includes(text),expected);
  if(!await page.getByRole('button',{name:'Export request & full result',exact:true}).isDisabled())throw Error('Rejected import leaves stale export');
  checks.push({name,status:await page.locator('#status').textContent()});
 }
 await page.getByLabel('Duration (s)',{exact:true}).fill('-1');await page.getByRole('button',{name:'Run experiment',exact:true}).click();
 if(await page.getByLabel('Duration (s)',{exact:true}).evaluate(el=>el.validity.valid))throw Error('Negative time admitted');
 checks.push({name:'negative-duration',exportDisabled:await page.getByRole('button',{name:'Export request & full result',exact:true}).isDisabled()});
 await page.getByRole('button',{name:'Reset illustrative preset',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 // Dispatch an edit before the 20ms scheduled Wasm task. This specifically checks the latest-request token.
 await page.locator('#controls').evaluate(form=>{form.requestSubmit();const input=form.querySelector('#duration');input.value='7';input.dispatchEvent(new Event('input',{bubbles:true}));});
 await page.waitForTimeout(100);
 if(!await page.getByRole('button',{name:'Export request & full result',exact:true}).isDisabled())throw Error('Superseded run published');
 checks.push({name:'superseded-request',status:await page.locator('#status').textContent()});
 await page.getByRole('button',{name:'Reset illustrative preset',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Completed'),null,{timeout:180000});
 return {checks,recovery:await page.locator('#status').textContent()};
}
