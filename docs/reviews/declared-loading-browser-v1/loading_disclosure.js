async(page)=>{
 await page.waitForFunction(()=>document.querySelector('#catalogue-dialog').open&&document.querySelector('#catalogue-detail-body').textContent.includes('Recorded source-review status: pending'));
 const body=page.locator('#catalogue-detail-body');const a={title:await page.locator('#catalogue-detail-title').textContent(),text:await body.innerText(),links:await body.locator('a').evaluateAll(ls=>ls.map(l=>({text:l.textContent,href:l.href})))};
 const link=a.links.find(x=>x.text==='Original source-review record');a.review=await(await page.request.get(link.href)).json();
 if(a.review.status!=='pending'||a.review.independent||a.review.reviewer||!a.text.includes('Retained numerical evidence')||!a.text.includes('Pair assessment: not assessed.'))throw Error('Disclosure regression');
 const s=page.waitForEvent('download');await page.evaluate(a=>{let l=document.createElement('a');l.href=URL.createObjectURL(new Blob([JSON.stringify(a,null,2)],{type:'application/json'}));l.download='disclosure-audit.json';l.click()},a);await(await s).saveAs('output/playwright/loading-rollout/disclosure-audit.json');return{pending_unsigned:true,numerical_evidence_visible:true,pair_unassessed:true};
}
