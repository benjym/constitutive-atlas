async page => {
 await page.locator('.ensemble-legend').getByRole('checkbox',{name:'Linear isotropic elasticity',exact:true}).check();
 await page.locator('#ensemble-runs button').first().click();
 await page.waitForFunction(()=>document.querySelector('#ensemble-stress').data.at(-1).meta.jobId==='linear-elastic:baseline');
 const downloading=page.waitForEvent('download');await page.locator('#ensemble-export').click();const download=await downloading;await download.saveAs('/private/tmp/atlas-ensemble-plotly-v1/ensemble.json');
 await page.setViewportSize({width:1440,height:1000});
 const metrics=()=>{const legend=document.querySelector('.ensemble-legend'),chart=document.querySelector('#ensemble-stress');return {width:innerWidth,legendHeight:legend.getBoundingClientRect().height,columns:getComputedStyle(legend).gridTemplateColumns,labels:[...legend.querySelectorAll('label')].map(e=>({text:e.textContent,title:e.title,accessible:e.querySelector('input').getAttribute('aria-label')})),overflow:document.documentElement.scrollWidth>innerWidth,chartWidth:chart._fullLayout.width,containerWidth:chart.clientWidth};};
 await page.waitForFunction(()=>document.querySelector('#ensemble-stress')._fullLayout.width===document.querySelector('#ensemble-stress').clientWidth);
 await page.evaluate(()=>{const l=document.querySelector('.ensemble-legend');window.scrollTo({top:l.getBoundingClientRect().top+scrollY-100,behavior:'instant'});});
 const desktop=await page.evaluate(metrics);await page.screenshot({path:'output/playwright/ensemble-plotly-v1-final-desktop.png',scale:'css'});
 await page.setViewportSize({width:390,height:844});await page.waitForFunction(()=>document.querySelector('#ensemble-stress')._fullLayout.width===document.querySelector('#ensemble-stress').clientWidth);
 await page.evaluate(()=>{const l=document.querySelector('.ensemble-legend');window.scrollTo({top:l.getBoundingClientRect().top+scrollY-150,behavior:'instant'});});
 const mobile=await page.evaluate(metrics);await page.screenshot({path:'output/playwright/ensemble-plotly-v1-final-mobile.png',scale:'css'});
 await page.locator('#ensemble-stress').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/ensemble-plotly-v1-final-mobile-chart.png',scale:'css'});
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Home',exact:true}).click();await page.setViewportSize({width:1280,height:1000});await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Ensemble explorer',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#ensemble-stress')._fullLayout.width===document.querySelector('#ensemble-stress').clientWidth);
 const routeReturn=await page.evaluate(metrics);
 await page.evaluate(()=>Plotly.relayout('ensemble-stress',{'xaxis.range':[2,6],'xaxis.autorange':false}));
 await page.locator('#ensemble-controls [data-parameter="E"]').first().fill('31000000');
 await page.waitForFunction(()=>document.querySelector('#ensemble-stress')._fullLayout.uirevision===2&&document.querySelector('#ensemble-stress')._fullLayout.xaxis.autorange===true);
 const newStudy=await page.evaluate(()=>({range:document.querySelector('#ensemble-stress')._fullLayout.xaxis.range,revision:document.querySelector('#ensemble-stress')._fullLayout.uirevision}));
 await page.waitForFunction(()=>document.querySelector('#ensemble-status').textContent==='19 completed · 6 stopped');
 return {desktop,mobile,routeReturn,newStudy,status:await page.locator('#ensemble-status').textContent(),chartErrors:await page.locator('.chart-panel [role=status]').allTextContents(),runtimeAssets:await page.evaluate(()=>performance.getEntriesByType('resource').filter(e=>e.name.includes('plotly-basic')).map(e=>e.name))};
}
