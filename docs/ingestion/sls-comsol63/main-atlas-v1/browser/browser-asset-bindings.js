async(page)=>{
 return await page.evaluate(async()=>{
  const identity=await(await fetch('./engine-sls/identity.json')).json(),manifest=await(await fetch('./engine-sls/package-manifest.json')).json(),assets=[];
  for(const[path,expected]of Object.entries(manifest.files)){
   const response=await fetch('./'+path),bytes=await response.arrayBuffer(),actual=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
   if(!response.ok||actual!==expected)throw Error('Fetched asset differs: '+path);assets.push({path,status:response.status,sha256:actual});
  }
  return {url:location.href,identity,assets,allTwelveAssetsMatch:assets.length===12};
 });
}
