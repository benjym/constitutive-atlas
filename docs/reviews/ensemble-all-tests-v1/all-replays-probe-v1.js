async page=>{
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Ensemble explorer',exact:true}).click();
 await page.waitForSelector('#ensemble-controls');
 const editors=page.locator('#ensemble-controls details.ensemble-model');
 for(let i=1;i<await editors.count();i++){const editor=editors.nth(i);if(await editor.getAttribute('open')===null)await editor.locator('summary').click();await editor.getByRole('checkbox').uncheck();}
 const elastic=editors.first();for(const input of await elastic.locator('[data-variation]').all())await input.fill('');
 await page.waitForFunction(()=>document.querySelectorAll('#ensemble-runs button').length===1&&document.querySelector('#ensemble-status').textContent==='1 completed'&&!document.querySelector('#ensemble-export').disabled);
 await page.locator('#ensemble-test-availability').selectOption('replay');
 const ids=await page.locator('#ensemble-test option').evaluateAll(es=>es.map(e=>e.value));
 const results=[];
 for(const id of ids){
  await page.locator('#ensemble-test').selectOption(id);
  await page.waitForFunction(id=>document.querySelector('#ensemble-test').value===id&&document.querySelector('.model-card h2')?.textContent.startsWith(id)&&document.querySelectorAll('#ensemble-runs button').length===1&&document.querySelector('#ensemble-status').textContent==='1 completed'&&!document.querySelector('#ensemble-export').disabled,id,{timeout:60000});
  const result=await page.evaluate(()=>{
   const d=JSON.parse(document.querySelector('#ensemble-selected').textContent),s=d.specification,r=d.result,p=d.parameters,E=p.E,nu=p.nu,G=E/(2*(1+nu)),lambda=E*nu/((1+nu)*(1-2*nu));let maxScaledError=0,maxVolume=0,maxLateralMismatch=0;
   for(const point of r.points){const trace=point.strain[0]+point.strain[1]+point.strain[2];for(let i=0;i<6;i++){const expected=s.initial[i]+2*G*point.strain[i]+(i<3?lambda*trace:0);maxScaledError=Math.max(maxScaledError,Math.abs(point.state[i]-expected)/Math.max(1,Math.abs(expected),Math.abs(s.initial[i])));}maxVolume=Math.max(maxVolume,Math.abs(trace));maxLateralMismatch=Math.max(maxLateralMismatch,Math.abs(point.state[1]-point.state[2]));}
   return {id:document.querySelector('#ensemble-test').value,status:document.querySelector('#ensemble-status').textContent,points:r.points.length,knots:s.path.knots.length,initial:s.initial.slice(0,6),controls:s.path.controls,maxScaledError,maxVolume,maxLateralMismatch,charts:[...document.querySelectorAll('.chart-panel')].filter(e=>!e.hidden).map(e=>({id:e.querySelector('.ensemble-plot').id,rows:e.querySelector('.ensemble-plot').data?.[0].x.length}))};
  });
  if(result.maxScaledError>1e-8||result.points!==result.knots||result.id.includes('TXCU')&&(result.maxVolume>1e-10||result.maxLateralMismatch>1e-4))throw Error('Analytic elastic/constraint audit failed: '+JSON.stringify(result));
  const downloading=page.waitForEvent('download');await page.locator('#ensemble-export').click();const download=await downloading;await download.saveAs('/Users/bmar5496/code/constitutive-atlas/.local/private-evidence/ensemble-all-tests-v1/'+id+'-elastic.json');results.push(result);
 }
 return {tests:results.length,results};
}
