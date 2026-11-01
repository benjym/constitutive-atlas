import assert from'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,existsSync}from'node:fs';
import {resolve,join}from'node:path';
import {tmpdir}from'node:os';
import {pathToFileURL}from'node:url';
import {spawnSync}from'node:child_process';
import {recordedWire,recordedSettings,runRecorded}from'../../../web/recorded.mjs';
import {normalizeSettings,settingsCsv}from'../../../web/numerics.mjs';
const [native,wasmFile,output]=process.argv.slice(2);assert.ok(!existsSync(output));
const requests=JSON.parse(readFileSync(new URL('./requests.json',import.meta.url),'utf8')),report={status:'running',cases:[],raw:[]},save=()=>writeFileSync(output,JSON.stringify(report)+'\n');
const module=await(await import(pathToFileURL(resolve(wasmFile)))).default(),temp=mkdtempSync(join(tmpdir(),'native-fixture-preflight-'));let serial=0;
const wasm={ccall:(fn,type,types,args)=>{const raw=module.ccall(fn,type,types,args);report.raw.push({role:'wasm',fn,args,raw});save();return raw;}};
const nativeEngine={ccall:(fn,type,types,args)=>{
 const common=['--model',args[0],'--parameters',args[1],'--initial',args[2]];let cli;
 if(fn==='atlas_integrate_with_settings')cli=['--mode','integrate',...common,'--strain',args[3],'--integration-settings',args[4]];
 else{assert.equal(fn,'atlas_replay_recorded');const c=join(temp,String(serial++)+'-controls.csv'),k=join(temp,String(serial++)+'-knots.csv');writeFileSync(c,args[4]);writeFileSync(k,args[5]);cli=['--mode','recorded',...common,'--initial-strain',args[3],'--recorded-controls-file',c,'--recorded-knots-file',k,'--integration-settings',args[6],'--recorded-settings',args[7]];}
 const p=spawnSync(native,cli,{encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024});report.raw.push({role:'native',fn,args,argv:cli,status:p.status,signal:p.signal,error:p.error?String(p.error):null,stderr:p.stderr,raw:p.stdout});save();assert.equal(p.error,undefined);assert.equal(p.signal,null);assert.equal(p.stderr,'');assert.equal(p.status,JSON.parse(p.stdout).ok?0:1);return p.stdout;
}};
function compare(a,b,path='result'){
 if(typeof b==='number'){assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=1e-10*Math.max(1,Math.abs(a),Math.abs(b)),path);return;}
 if(Array.isArray(b)){assert.equal(a.length,b.length);b.forEach((v,i)=>compare(a[i],v,path+'['+i+']'));return;}
 if(b&&typeof b==='object'){assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort());for(const k in b)if(k!=='elapsed_ms')compare(a[k],b[k],path+'.'+k);return;}
 assert.equal(a,b,path);
}
const physical=r=>{const {elapsed_ms,...rest}=r;return rest;};
function integrate(engine,s,z,de){const args=[s.model,s.parameters.join(','),z.join(','),de.join(','),settingsCsv(normalizeSettings(s.integration_settings))];return JSON.parse(engine.ccall('atlas_integrate_with_settings','string',args.map(()=> 'string'),args));}
try{
 for(const [name,s]of Object.entries(requests)){
  const row={name,specification:s};report.cases.push(row);save();row.native=runRecorded(nativeEngine,s);save();row.wasm=runRecorded(wasm,s);save();compare(row.native,row.wasm);assert.equal(row.native.ok,true,name+': '+row.native.message);assert.equal(row.native.points.length,5);assert.deepEqual(row.native.points[3].state,row.native.points[2].state);
  const resumed={...structuredClone(s),initial:row.native.points[2].state,path:{...structuredClone(s.path),initial_strain:row.native.points[2].strain,knots:s.path.knots.slice(2)}};
  row.restart_native=runRecorded(nativeEngine,resumed);save();row.restart_wasm=runRecorded(wasm,resumed);save();assert.equal(row.restart_native.ok,true);assert.equal(row.restart_wasm.ok,true);compare(row.restart_native,row.restart_wasm);assert.deepEqual(row.restart_native.state,row.native.state);assert.deepEqual(row.restart_wasm.state,row.wasm.state);
  if(name==='all-strain'){let parent=s.initial,previous=s.path.initial_strain;row.direct=[];
   for(let i=1;i<5;i++){if(i===3)continue;const de=s.path.knots[i].targets.map((v,j)=>v-previous[j]),n=integrate(nativeEngine,s,parent,de),w=integrate(wasm,s,parent,de);row.direct.push({n,w});save();assert.equal(n.ok,true);compare(n,w);compare(n.state,row.native.points[i].state);parent=n.state;previous=s.path.knots[i].targets;}
  }
  row.passed=true;save();
 }
 const s=requests['all-strain'],z=[...s.initial];z[0]=105000;z[1]=95000;z[3]=1000;const de=[.0001,-.00002,.00001,.00003,.00001,-.00001],rotate=a=>[a[1],a[0],a[2],-a[3],a[5],-a[4]],zr=[...z];zr.splice(0,6,...rotate(z.slice(0,6)));
 const row={name:'rotation',native:integrate(nativeEngine,s,z,de),rotated_native:integrate(nativeEngine,s,zr,rotate(de)),wasm:integrate(wasm,s,z,de),rotated_wasm:integrate(wasm,s,zr,rotate(de))};report.cases.push(row);save();for(const key of ['native','rotated_native','wasm','rotated_wasm'])assert.equal(row[key].ok,true,key+': '+row[key].message);compare(row.native,row.wasm);compare(row.rotated_native,row.rotated_wasm);for(let i=0;i<6;i++)assert.ok(Math.abs(rotate(row.native.state.slice(0,6))[i]-row.rotated_native.state[i])<.01);row.passed=true;report.status='passed';save();console.log('Explicit GIS depth20preflight passed: original all-strain/drained geometry, duplicates, restart, direct replay and rotation; unchanged tolerances.');
}catch(error){report.status='failed';report.error=String(error);save();throw error;}
