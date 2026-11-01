async (page) => {
 const root='/Users/bmar5496/code/constitutive-atlas/docs/reviews/gis2024-installed-browser-v1/inputs/';
 const records=[];
 async function replay(file){const n=await page.evaluate(()=>window.__wires.length);await page.locator('#run-file').setInputFiles([]);await page.locator('#run-file').setInputFiles(file);await page.waitForFunction(n=>window.__wires.slice(n).some(x=>x.direction==='response'),n);return await page.evaluate(n=>window.__wires.slice(n),n);}
 const clean=await replay(root+'case-02.json');const cleanResult=clean.find(x=>x.direction==='response').data.result;
 if(!cleanResult.ok)throw Error('Clean recovery baseline rejected');
 const cases=[['blank-h','state-h',''],['malformed-h','state-h','0,0,0'],['blank-Omega','state-Omega',''],['negative-e','state-e','-0.1'],['Omega-outside','state-Omega','1.1'],['memory-outside','state-h','0.001,0,0,0,0,0'],['zero-pressure','confinement','0']];
 for(const [id,field,value]of cases){const n=await page.evaluate(()=>window.__wires.length);await page.locator('#'+field).evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));},value);
  await page.waitForFunction(()=>document.querySelector('#response-charts').getAttribute('aria-busy')==='false');
  const observation=await page.evaluate(n=>({wires:window.__wires.slice(n),status:document.querySelector('#control-status').textContent,run:document.querySelector('#run-state').textContent,disabled:document.querySelector('#export-run').disabled}),n);
  const response=observation.wires.find(x=>x.direction==='response');if(response&&(response.data.result?.ok||response.data.result?.points?.length))throw Error('Invalid input committed: '+id);if(!observation.disabled)throw Error('Invalid run remained exportable: '+id);
  const recovery=await replay(root+'case-02.json');const r=recovery.find(x=>x.direction==='response').data.result;if(!r.ok||JSON.stringify(r.points)!==JSON.stringify(cleanResult.points))throw Error('Recovery leaked state: '+id);
  records.push({id,field,value,observation,recovery});
 }
 const failed=await replay(root+'failure.json');const result=failed.find(x=>x.direction==='response').data.result;const request=failed.find(x=>x.direction==='request').data.specification;
 if(result.ok||result.points.length!==1||JSON.stringify(result.points[0].state)!==JSON.stringify(request.initial))throw Error('Forced failure did not retain initial full state');
 const failureStatus=await page.locator('#control-status').textContent();const recovered=await replay(root+'case-02.json');if(JSON.stringify(recovered.find(x=>x.direction==='response').data.result.points)!==JSON.stringify(cleanResult.points))throw Error('Forced failure leaked state');
 const report={clean,guards:records,forced_failure:{wires:failed,status:failureStatus,recovery:recovered}};
 const pending=page.waitForEvent('download');await page.evaluate(report=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='guards.json';a.click();},report);const d=await pending;await d.saveAs('output/playwright/gis-installed/guards.json');return {guards:records.length,recoveries:records.length+1,forced_failure_points:result.points.length,full_state:request.initial.length};
}
