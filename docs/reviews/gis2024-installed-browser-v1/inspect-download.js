async (page) => {
 const wire=await page.evaluate(()=>window.__wires.map(x=>({direction:x.direction,data:x.data})));
 const pending=page.waitForEvent('download',{timeout:8000});await page.locator('#export-run').click();
 const download=await pending;await download.saveAs('output/playwright/gis-installed/case-10.json');return {worker_events:wire.length,download:download.suggestedFilename()};
}
