async page=>{
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Ensemble explorer',exact:true}).click();
 const chooser=page.waitForEvent('filechooser');await page.locator('#ensemble-load-saved').click();await (await chooser).setFiles('/Users/bmar5496/code/constitutive-atlas/.local/private-evidence/ensemble-all-tests-v1/OPARA-TXCU-100-elastic.json');
 const done=async id=>page.waitForFunction(id=>document.querySelector('#ensemble-test').value===id&&document.querySelector('#ensemble-status').textContent==='1 completed'&&!document.querySelector('#ensemble-export').disabled,id,{timeout:60000});
 await done('OPARA-TXCU-100');
 const imported=await page.evaluate(()=>({selected:document.querySelector('#ensemble-test').value,runs:document.querySelectorAll('#ensemble-runs button').length,initial:JSON.parse(document.querySelector('#ensemble-selected').textContent).specification.initial.slice(0,6)}));
 await page.route('**/ensemble-tests/OPARA-TXCD-20.json',async route=>{await new Promise(r=>setTimeout(r,700));await route.continue();});
 await page.locator('#ensemble-test').selectOption('OPARA-TXCD-20');await page.locator('#ensemble-test').selectOption('OPARA-TXCU-60');await done('OPARA-TXCU-60');
 await page.waitForFunction(()=>document.querySelector('#ensemble-pore').data?.[0].x.length===1267);
 await page.unroute('**/ensemble-tests/OPARA-TXCD-20.json');
 const latest=await page.evaluate(()=>({selected:document.querySelector('#ensemble-test').value,initial:JSON.parse(document.querySelector('#ensemble-selected').textContent).specification.initial.slice(0,6),gap:document.querySelector('#ensemble-test-gap').textContent,points:document.querySelector('#ensemble-pore').data[0].x.length}));
 await page.locator('#ensemble-test-search').fill('FI-HAARAJOKI');await page.locator('#ensemble-test-protocol').selectOption('oedometer');
 const filtered=await page.locator('#ensemble-test-count').textContent();await page.locator('#ensemble-test').selectOption('FI-HAARAJOKI-1601');
 await page.waitForFunction(()=>document.querySelector('#ensemble-test-gap').textContent.startsWith('Measurements only.')&&document.querySelector('#ensemble-source').data?.[0].x.length>0&&!document.querySelector('#ensemble-source').parentElement.hidden);
 const source=await page.evaluate(()=>({id:document.querySelector('#ensemble-test').value,gap:document.querySelector('#ensemble-test-gap').textContent,controlsHidden:document.querySelector('#ensemble-controls').hidden,runs:document.querySelectorAll('#ensemble-runs button').length,axes:document.querySelector('#ensemble-source')._fullLayout.xaxis.title.text,rows:document.querySelector('#ensemble-source').data[0].x.length}));
 const xOptions=await page.locator('#ensemble-source-x option').evaluateAll(es=>es.map(e=>e.value));await page.locator('#ensemble-source-x').selectOption(xOptions.at(-1));
 await page.waitForFunction(key=>document.querySelector('#ensemble-source').data?.[0].x.length>0&&document.querySelector('#ensemble-source-x').value===key,xOptions.at(-1));
 await page.setViewportSize({width:1440,height:1000});await page.locator('#ensemble-test').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/ensemble-all-tests-v1-source-desktop.png',scale:'css'});
 await page.locator('#ensemble-test-search').fill('ROCKFILL-01');await page.locator('#ensemble-test-protocol').selectOption('');await page.locator('#ensemble-test').selectOption('ROCKFILL-01');
 await page.waitForFunction(()=>document.querySelector('#ensemble-test-gap').textContent.startsWith('Measurements only.')&&document.querySelector('#ensemble-source').data?.[0].mode==='markers');
 const summary=await page.evaluate(()=>({id:document.querySelector('#ensemble-test').value,mode:document.querySelector('#ensemble-source').data[0].mode,rows:document.querySelector('#ensemble-source').data[0].x.length}));
 await page.locator('#ensemble-test-search').fill('GEOLAB-FONTAINEBLEAU');await page.locator('#ensemble-test').selectOption('GEOLAB-FONTAINEBLEAU-TRIAX-CD-1');
 await page.waitForFunction(()=>document.querySelector('#ensemble-test-gap').textContent.includes('Initial effective stress')&&!document.querySelector('#ensemble-stress').parentElement.hidden);
 const missingState=await page.evaluate(()=>({id:document.querySelector('#ensemble-test').value,gap:document.querySelector('#ensemble-test-gap').textContent,runs:document.querySelectorAll('#ensemble-runs button').length,measured:document.querySelector('#ensemble-stress').data[0].x.length}));
 // Import from a measurements-only view while search excludes the imported ID.
 const chooser2=page.waitForEvent('filechooser');await page.locator('#ensemble-load-saved').click();await (await chooser2).setFiles('/Users/bmar5496/code/constitutive-atlas/.local/private-evidence/ensemble-all-tests-v1/OPARA-TXCU-100-elastic.json');await done('OPARA-TXCU-100');
 await page.setViewportSize({width:390,height:844});
 await page.waitForFunction(()=>document.querySelector('#ensemble-stress')._fullLayout.width===document.querySelector('#ensemble-stress').clientWidth);
 await page.locator('#ensemble-test').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/ensemble-all-tests-v1-mobile-selectors.png',scale:'css'});
 await page.locator('#ensemble-pore').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/ensemble-all-tests-v1-mobile-pore.png',scale:'css'});
 const mobile=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,charts:[...document.querySelectorAll('#ensemble .chart-panel')].filter(e=>!e.hidden).map(e=>{const g=e.querySelector('.ensemble-plot');return {id:g.id,width:g._fullLayout.width,container:g.clientWidth};}),errors:[...document.querySelectorAll('#ensemble .chart-panel [role=status]')].map(e=>e.textContent)}));
 if(mobile.overflow||mobile.charts.some(c=>c.width!==c.container)||mobile.errors.some(Boolean)||latest.initial[0]!==63882||source.runs||missingState.runs)throw Error('Browser qualification failed: '+JSON.stringify({mobile,latest,source,missingState}));
 return {imported,latest,filtered,source,summary,missingState,mobile};
}
