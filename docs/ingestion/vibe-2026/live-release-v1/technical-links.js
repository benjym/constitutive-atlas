async(page)=>{
 const links=await page.locator('.model-profile-technical a').evaluateAll(xs=>xs.map(a=>({text:a.textContent,href:a.href})).filter(a=>a.href.startsWith(location.origin)));
 if(!links.length)throw Error('Missing technical links');
 return await page.evaluate(async links=>{const rows=[];for(const a of links){const r=await fetch(a.href),bytes=await r.arrayBuffer(),digest=await crypto.subtle.digest('SHA-256',bytes);if(r.status!==200)throw Error(a.href+':'+r.status);rows.push({...a,status:r.status,sha256:Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('')});}return rows;},links);
}
