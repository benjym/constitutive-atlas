async(page)=>{
 const p=page.locator('.model-profile');
 const rows=await p.locator('table tbody tr').count();if(rows!==30)throw Error('Parameter rows '+rows);
 const tech=await page.locator('.model-profile-technical').evaluate(d=>({open:d.open,summary:d.querySelector('summary').textContent}));if(tech.open)throw Error('Technical disclosure initially open');
 const links=await p.locator('a').evaluateAll(xs=>xs.map(a=>({text:a.textContent,href:a.getAttribute('href')})));
 for(const id of ['hypoplastic-clay-2013','hypoplastic-thermal-ma-2017'])if(!links.some(a=>a.href==='#catalogue/'+id))throw Error('Missing related link '+id);
 const text=await p.textContent();for(const needle of ['suction','temperature','seconds','Mandel'])if(!text.toLowerCase().includes(needle.toLowerCase()))throw Error('Missing guidance '+needle);
 const bounds=await page.evaluate(()=>({viewport:innerWidth,page:document.documentElement.scrollWidth}));if(bounds.page!==bounds.viewport)throw Error('Profile overflow');
 await p.evaluate(el=>{for(let p=el;p;p=p.parentElement)p.scrollTop=0;window.scrollTo(0,0);});return {rows,tech,links,bounds};
}
