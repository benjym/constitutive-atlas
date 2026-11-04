const out='/Users/bmar5496/code/constitutive-atlas/output/playwright/baseline-five-e7-20261105-v1';
const picker=page.getByRole('combobox',{name:'Experimental test',exact:true});
await picker.selectOption('builtin:GEOLAB-BASKARP-TRIAX-CD-1');
const normalized=page.getByRole('status').filter({hasText:'3600 rows'});
await normalized.waitFor({state:'visible',timeout:30000});
if(!(await normalized.innerText()).includes('Overlay shown.'))throw Error('Normalized overlay missing');
await page.screenshot({path:out+'/compression-normalized-v1.png',fullPage:true});
const toggle=page.getByRole('switch',{name:'Show measurements',exact:true});
await toggle.uncheck();
if(!(await normalized.innerText()).includes('Overlay hidden.'))throw Error('Normalized toggle failed');
await toggle.check();
await page.getByRole('checkbox',{name:'Browse all source records',exact:true}).check();
const nativeOption=await picker.locator('option').evaluateAll(xs=>xs.filter(x=>x.value==='builtin:CHANG-CREEP-RAW-28-01').map(x=>({label:x.textContent,value:x.value})));
if(nativeOption.length!==1)throw Error('Largest native record not exposed');
await picker.selectOption(nativeOption[0].value);
const native=page.getByRole('status').filter({hasText:'200000 rows'});
await native.waitFor({state:'visible',timeout:60000});
if(!(await native.innerText()).includes('Source chart shown. No model overlay.'))throw Error('Native scope or source chart missing');
await page.getByRole('img',{name:'Selected source measurement channels',exact:true}).waitFor({state:'visible'});
await page.screenshot({path:out+'/compression-native-v1.png',fullPage:true});
const assets=await page.evaluate(async()=>{
 const paths=['experiments.mjs','experiments/index.json','experiments/GEOLAB-BASKARP-TRIAX-CD-1.json.gz','experiments/CHANG-CREEP-RAW-28-01.json.gz'];
 const result=[];
 for(const path of paths){const r=await fetch('./'+path,{cache:'no-store'}),b=await r.arrayBuffer();result.push({path,url:r.url,status:r.status,bytes:b.byteLength,sha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('')});}
 return result;
});
if(assets.some(x=>x.status!==200))throw Error('Measurement transport HTTP failure');
return {status:'passed-normalized-and-largest-native-compressed-UI',normalizedRows:3600,nativeRows:200000,nativeOption,normalizedStatus:await normalized.count()?await normalized.innerText():null,nativeStatus:await native.innerText(),assets};
