import {validateExampleIndex,prepareExample}from './laboratory-examples.mjs';
export function setupLaboratoryExamples({catalogue,getModel,applySpecification,document=globalThis.document,fetcher=fetch,onError=()=>{}}){
 const el=id=>document.getElementById(id),panel=el('named-examples'),select=el('named-example'),status=el('named-example-status'),button=el('load-named-example'),evidence=el('named-example-evidence');
 let index=null,prepared=null,revision=0;
 function refresh(){
  ++revision;prepared=null;button.disabled=true;evidence.hidden=true;select.replaceChildren(new Option('Choose a named run example',''));status.textContent='Preview an example before replacing inputs. Global defaults stay unchanged.';
  const rows=index?.examples.filter(e=>e.model===getModel()?.id)??[];panel.hidden=!rows.length;
  for(const entry of rows)select.append(new Option(entry.label,entry.id));
 }
 select.onchange=async()=>{
  const token=++revision;prepared=null;button.disabled=true;evidence.hidden=true;
  const entry=index?.examples.find(e=>e.id===select.value&&e.model===getModel()?.id);if(!entry){status.textContent='Choose an example to preview its inputs and settings.';return;}
  status.textContent='Checking example and model identity…';
  try{const result=await prepareExample(entry,index,catalogue,{fetcher});if(token!==revision)return;prepared=result;status.textContent=result.summary;evidence.href=entry.evidence_url;evidence.textContent='Example evidence and limitations ↗';evidence.hidden=false;button.disabled=false;}
  catch(error){if(token!==revision)return;status.textContent=error.message;onError(error.message);}
 };
 button.onclick=()=>{if(!prepared)return;const chosen=prepared;try{applySpecification(structuredClone(chosen.specification));}catch(error){status.textContent=error.message;onError(error.message);}};
 const ready=(async()=>{try{const response=await fetcher('./laboratory-examples.json');if(!response.ok)throw Error('Named examples are unavailable.');index=validateExampleIndex(await response.json(),catalogue);refresh();}catch(error){panel.hidden=false;status.textContent=error.message;onError(error.message);}})();
 refresh();return {refresh,ready};
}
