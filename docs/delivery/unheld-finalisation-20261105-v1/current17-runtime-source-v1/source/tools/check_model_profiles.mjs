/** Public-content gate, also called by the standard web builder. No material execution. */
import {readFileSync,readdirSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve,join,relative} from 'node:path';
import {validateModelProfiles,modelProfile} from '../web/model-profiles.mjs';
const root=resolve(process.argv[2]??fileURLToPath(new URL('../',import.meta.url)));
const read=path=>JSON.parse(readFileSync(path,'utf8'));
const entries=read(join(root,'catalogue/manifest.json')).models;
function definitions(directory){return readdirSync(directory,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?definitions(join(directory,entry.name)):entry.name.endsWith('.json')?[read(join(directory,entry.name))]:[]).filter(record=>typeof record.id==='string'&&record.parameters&&Array.isArray(record.state));}
const models=definitions(join(root,'models'));
const staged=readdirSync(join(root,'models')).filter(name=>name.endsWith('.json')).map(name=>read(join(root,'models',name))).filter(model=>!entries.some(entry=>entry.id===model.id));
const publicEntries=[...entries,...staged];
validateModelProfiles(publicEntries,models);
for(const entry of publicEntries){
  for(const path of modelProfile(entry.id).contentSources){
    const target=resolve(root,path);if(relative(root,target).startsWith('..')||!statSync(target).isFile())throw Error(entry.id+': unavailable content source '+path);
  }
}
console.log(`Public model profiles: ${entries.length}/${entries.length} catalogue entries, ${staged.length} additional top-level definitions; parameter names, local provenance and related links checked.`);
