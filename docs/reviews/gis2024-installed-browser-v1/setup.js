async (page) => {
 await page.addInitScript(()=>{window.__wires=[];const Native=window.Worker;window.Worker=class extends Native{constructor(...args){super(...args);this.addEventListener('message',e=>window.__wires.push({direction:'response',data:structuredClone(e.data)}));}postMessage(data,...args){window.__wires.push({direction:'request',data:structuredClone(data)});return super.postMessage(data,...args);}};});
 await page.goto('http://127.0.0.1:8957/constitutive-atlas/');
 await page.waitForFunction(()=>window.__wires.some(x=>x.direction==='response')&&!document.querySelector('#export-run').disabled);
 const identity=await page.evaluate(async()=>{const cat=await(await fetch('./models.json')).json();const files=await Promise.all(cat.models.map(async m=>{const response=await fetch('./models/'+m.id+'.json');const definition=await response.json();return {id:m.id,ok:response.ok,equal:JSON.stringify(definition)===JSON.stringify(m)};}));return {hash:cat.sha256,models:files,requests:window.__wires.filter(x=>x.direction==='request').length,responses:window.__wires.filter(x=>x.direction==='response').map(x=>({hash:x.data.result?.catalogue_hash,ok:x.data.result?.ok})),fields:[...document.querySelectorAll('#model option')].map(x=>x.value)};});
 if(identity.models.length!==11||identity.models.some(m=>!m.ok||!m.equal)||identity.responses.some(x=>x.hash!==identity.hash))throw Error('Package/runtime identity mismatch');
 return identity;
}
