// Compose model interfaces inside the main atlas without overlapping active workers.
export function createLaboratoryControllerRouter(controllers){
 const byId=new Map();
 for(const controller of controllers){
  if(!controller?.modelId||byId.has(controller.modelId))throw Error('Duplicate or missing laboratory model identity.');
  byId.set(controller.modelId,controller);
 }
 let selected=null;
 return {
  supports(id){return byId.has(id);},
  select(id,options){
   const target=byId.get(id)||null;
   if(target&&target===selected&&target.active)return target.select(id,options);
   // Clear every previous interface before enabling the target: inactive views may
   // restore shared ordinary controls, so this order is part of the contract.
   for(const view of controllers)view.select(null,{auto:false});
   selected=byId.get(id)||null;
   return selected?selected.select(id,options):false;
  },
  get active(){return !!selected?.active;},
  run(...args){return selected?.run(...args);},
  showEquations(){return selected?.showEquations()||false;}
 };
}
