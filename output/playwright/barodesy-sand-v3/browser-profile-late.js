async(page)=>{
 let release;const pending=new Promise(resolve=>release=resolve);
 await page.route('**/evidence.json',async route=>{await pending;await route.continue();});
 await page.goto('http://127.0.0.1:56013/constitutive-atlas/#catalogue/barodesy-sand',{waitUntil:'domcontentloaded'});
 await page.reload({waitUntil:'domcontentloaded'});
 await page.locator('#catalogue-detail-body .model-profile').waitFor();
 const before=await page.locator('#catalogue-detail-body').evaluate(x=>{x.scrollTop=137;return {text:x.querySelector('.model-profile').innerText,scroll:x.scrollTop,technicalOpen:x.querySelector('.model-profile-technical').open,reviewLinks:x.querySelector('.technical-review-links').querySelectorAll('a').length};});
 release();
 await page.locator('#catalogue-detail-body .technical-review-links a').first().waitFor({state:'attached'});
 const after=await page.locator('#catalogue-detail-body').evaluate(x=>({text:x.querySelector('.model-profile').innerText,scroll:x.scrollTop,technicalOpen:x.querySelector('.model-profile-technical').open,links:[...x.querySelectorAll('.technical-review-links a')].map(a=>({text:a.innerText,href:a.getAttribute('href')}))}));
 await page.unroute('**/evidence.json');
 if(before.text!==after.text||before.scroll!==after.scroll||before.technicalOpen||after.technicalOpen||before.reviewLinks!==0||after.links.length!==3)throw Error('Late evidence changed profile/disclosure/scroll or missed review links');
 const fetched=await page.evaluate(async paths=>{const rows=[];for(const path of paths){const response=await fetch(path);const raw=await response.arrayBuffer();rows.push({path,status:response.status,sha256:[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(x=>x.toString(16).padStart(2,'0')).join('')});}return rows;},after.links.map(x=>x.href));
 return {before,after,fetched};
}
