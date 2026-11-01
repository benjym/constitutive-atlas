async(page)=>{
 await page.locator('#run-file').setInputFiles('output/playwright/loading-rollout/named-run.json');
 await page.waitForFunction(()=>!document.querySelector('#export-run').disabled&&window.__wires.filter(x=>x.direction==='response').at(-1)?.data.result?.points?.length===9);
 const a=await page.evaluate(()=>{let r=window.__wires.filter(x=>x.direction==='response').at(-1);return{request:window.__wires.find(x=>x.direction==='request'&&x.data.id===r.data.id).data,result:r.data.result,controls:Object.fromEntries(['model','target','steps','numerical-max_depth','state-h','state-Omega'].map(id=>[id,document.getElementById(id)?.value])),text:document.querySelector('#controls').innerText}});
 const d=page.waitForEvent('download');await page.getByRole('button',{name:'↓ Reproducible run',exact:true}).click();await(await d).saveAs('output/playwright/loading-rollout/imported-run.json');
 const s=page.waitForEvent('download');await page.evaluate(a=>{let l=document.createElement('a');l.href=URL.createObjectURL(new Blob([JSON.stringify(a,null,2)],{type:'application/json'}));l.download='import-audit.json';l.click()},a);await(await s).saveAs('output/playwright/loading-rollout/import-audit.json');return{points:a.result.points.length,controls:a.controls};
}
