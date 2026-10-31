import {readFileSync,writeFileSync} from 'node:fs';
import createAtlas from '/private/tmp/atlas-recorded-scope-view-v1/build/atlas.js';
import {runScopedLaboratory} from '/Users/bmar5496/code/constitutive-atlas/web/laboratory-scope.mjs';
import {createLoading} from '/Users/bmar5496/code/constitutive-atlas/web/loading.mjs';
const {catalogue,rows}=JSON.parse(readFileSync(new URL('./inputs.json',import.meta.url))),engine=await createAtlas(),results=[];
function compare(a,b,path=''){
 if(typeof b==='number'){if(typeof a!=='number'||!Number.isFinite(a)||Math.abs(a-b)>1e-9*Math.max(1,Math.abs(b))||(['iterations','substeps','rejected','steps','cycles','protocol'].includes(path.split('.').at(-1))&&a!==b))throw Error('numeric mismatch '+path);}
 else if(b&&typeof b==='object'){if(!a||Array.isArray(a)!==Array.isArray(b)||Object.keys(a).sort().join(',')!==Object.keys(b).sort().join(','))throw Error('shape mismatch '+path);for(const k of Object.keys(b))compare(a[k],b[k],path+'.'+k);}
 else if(a!==b)throw Error('value mismatch '+path);
}
for(const row of rows){const result=runScopedLaboratory(engine,row.request,catalogue);results.push({label:row.label,result});writeFileSync(new URL('./responses.json',import.meta.url),JSON.stringify(results,null,2)+'\n');const {elapsed_ms:a,...actual}=result,{elapsed_ms:b,...expected}=row.response;compare(actual,expected,row.label);}
const seed=rows.find(r=>r.label==='scoped-elastic-1'),request={...seed.request,target:1e-5,steps:16,cycles:1};request.loading=createLoading(request);
const result=runScopedLaboratory(engine,request,catalogue);results.push({label:'independent-exact-reversal',request,result});writeFileSync(new URL('./responses.json',import.meta.url),JSON.stringify(results,null,2)+'\n');
const model=catalogue.models.find(m=>m.id===request.model),parameters=Object.fromEntries(Object.keys(model.parameters).map((k,i)=>[k,request.parameters[i]]));
let stressError=0,strainError=0;
for(const p of result.points){const a=p.control,expectedStress=[request.initial[0]+parameters.E*a,request.initial[1],request.initial[2],0,0,0],expectedStrain=[a,-parameters.nu*a,-parameters.nu*a,0,0,0];for(let i=0;i<6;i++){stressError=Math.max(stressError,Math.abs(p.state[i]-expectedStress[i]));strainError=Math.max(strainError,Math.abs(p.strain[i]-expectedStrain[i]));}if(JSON.stringify(p.state.slice(6))!==JSON.stringify(request.initial.slice(6)))throw Error('history changed');}
if(stressError>.002||strainError>2e-10)throw Error('independent elastic gate failed');
console.log(JSON.stringify({ok:true,native_pairs:10,wasm_material_requests:11,max_stress_error_Pa:stressError,max_strain_error:strainError}));
