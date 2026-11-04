// Only explicitly published, project-local timed laboratories are navigable.
export function timedLaboratoryRoute(entry){
 if(entry.public_timed_laboratory!==true)return null;
 if(typeof entry.timed_laboratory!=='string'||!/^[a-z0-9][a-z0-9-]*\.html$/.test(entry.timed_laboratory))throw new Error('Unsafe public timed laboratory route');
 return entry.timed_laboratory;
}
