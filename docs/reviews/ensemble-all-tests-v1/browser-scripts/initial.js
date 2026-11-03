async page=>{
 await page.waitForFunction(()=>document.querySelector('#ensemble-status')?.textContent==='19 completed · 6 stopped');
 const initial=await page.evaluate(()=>({count:document.querySelector('#ensemble-test-count').textContent,options:document.querySelector('#ensemble-test').options.length,charts:['stress','volume','path'].map(k=>({channel:k,traces:document.querySelector('#ensemble-'+k).data.length,measurements:document.querySelector('#ensemble-'+k).data[0].x.length})),errors:[...document.querySelectorAll('.chart-panel [role=status]')].map(e=>e.textContent)}));
 const downloading=page.waitForEvent('download');await page.locator('#ensemble-export').click();const download=await downloading;await download.saveAs('/private/tmp/atlas-ensemble-all-tests-v1/default.json');
 await page.locator('#ensemble-test-availability').selectOption('replay');
 const replayOptions=await page.locator('#ensemble-test option').evaluateAll(es=>es.map(e=>e.value));
 await page.locator('#ensemble-test').selectOption('OPARA-TXCU-20');
 await page.waitForFunction(()=>document.querySelector('#ensemble-test-gap')?.textContent.startsWith('Ensemble replay')&&document.querySelector('#ensemble-status')?.textContent==='19 completed · 6 stopped');
 const undrained=await page.evaluate(()=>({selected:document.querySelector('#ensemble-test').value,description:document.querySelector('#ensemble-test-gap').textContent,status:document.querySelector('#ensemble-status').textContent,confinementVisible:!document.querySelector('#ensemble-confinement').parentElement.hidden,charts:['stress','volume','path','pore'].map(k=>({channel:k,traces:document.querySelector('#ensemble-'+k).data.length,measurements:document.querySelector('#ensemble-'+k).data[0].x.length})),request:JSON.parse(document.querySelector('#ensemble-selected').textContent).specification}));
 const nextDownload=page.waitForEvent('download');await page.locator('#ensemble-export').click();const next=await nextDownload;await next.saveAs('/private/tmp/atlas-ensemble-all-tests-v1/undrained.json');
 return {initial,replayOptions,undrained:{...undrained,request:{initial:undrained.request.initial,controls:undrained.request.path.controls,knots:undrained.request.path.knots.length}}};
}
