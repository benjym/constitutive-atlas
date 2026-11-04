const root='https://benjym.github.io/constitutive-atlas/',checks=[];
await page.goto(root+'#laboratory?model=linear-elastic');await page.locator('#cycles').waitFor();await page.locator('#protocol').selectOption('1');await page.locator('#cycles').selectOption('1');await page.waitForTimeout(500);
if(await page.locator('#cycles').inputValue()!=='1')throw Error('supported cycles value lost');
if(await page.getByText('Material parameters Adjust model constants',{exact:true}).locator('..').getAttribute('open')===null)await page.getByText('Material parameters Adjust model constants',{exact:true}).click();await page.locator('#param-E').fill('31000000');await page.waitForTimeout(500);if(await page.locator('#cycles').inputValue()!=='1')throw Error('supported cycles not retained after update');checks.push('supported-cycles-retained');
await page.locator('#model').selectOption('s-clay1');await page.waitForTimeout(500);if(await page.locator('#cycles').inputValue()!=='0')throw Error('unsupported cycles not reset');if(!await page.locator('#cycles option[value="1"]').isDisabled())throw Error('unsupported cycles enabled');checks.push('unsupported-cycles-reset0-disabled');
return {checks};
