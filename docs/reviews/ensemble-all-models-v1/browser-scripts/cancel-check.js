async page => {
 await page.locator('#ensemble-reset').click();
 await page.waitForFunction(()=>window.ensembleWorkerAudit.active===2);
 await page.locator('#ensemble-controls [data-parameter="E"]').first().fill('31000000');
 await page.locator('#ensemble-controls [data-parameter="E"]').first().fill('32000000');
 await page.locator('#ensemble-cancel').click();
 await page.waitForFunction(()=>window.ensembleWorkerAudit.live===0&&window.ensembleWorkerAudit.active===0);
 const cancelled=await page.evaluate(()=>({status:document.querySelector('#ensemble-status').textContent,live:ensembleWorkerAudit.live,active:ensembleWorkerAudit.active}));
 await page.locator('#ensemble-controls [data-parameter="E"]').first().fill('33000000');
 await page.waitForFunction(()=>window.ensembleWorkerAudit.active===2);
 await page.locator('#ensemble-controls [data-parameter="E"]').first().fill('34000000');
 await page.waitForFunction(()=>window.ensembleWorkerAudit.active===2);
 await page.waitForFunction(()=>window.ensembleWorkerAudit.live===0&&!document.querySelector('#ensemble-status').textContent.includes('Running'),{timeout:30000});
 return await page.evaluate(cancelled=>({cancelled,audit:ensembleWorkerAudit,latestE:document.querySelector('#ensemble-controls [data-parameter="E"]').value,status:document.querySelector('#ensemble-status').textContent}),cancelled);
}
