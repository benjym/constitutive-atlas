/** Public explanations are editorial content, separate from executable definitions. */
import {modelProfiles} from './model-profile-data.mjs';
export const modelProfile=id=>Object.hasOwn(modelProfiles,id)?modelProfiles[id]:null;

/** A package must explain every entry, including literature and family records. */
export function validateModelProfiles(entries,definitions=[]){
  const nonempty=value=>typeof value==='string'&&value.trim().length>0;
  const require=(condition,message)=>{if(!condition)throw Error(message);};
  const seen=new Set();
  for(const entry of entries){
    require(nonempty(entry?.id)&&!seen.has(entry.id),'Duplicate or missing catalogue identity.');seen.add(entry.id);
    const profile=modelProfile(entry.id);
    require(profile,'Missing public model profile: '+entry.id);
    for(const key of ['title','summary','introduction','preparation','scope','limits'])require(nonempty(profile[key]),entry.id+': missing '+key);
    require(Array.isArray(profile.behaviours)&&profile.behaviours.length>=2&&profile.behaviours.every(pair=>Array.isArray(pair)&&pair.length===2&&pair.every(nonempty)),entry.id+': explain the model behaviour.');
    require(Array.isArray(profile.contentSources)&&profile.contentSources.length>0&&profile.contentSources.every(path=>nonempty(path)&&/^(models|docs|catalogue|web)\//.test(path)&&!path.split('/').includes('..')),entry.id+': missing local content provenance.');
    require(Array.isArray(profile.references)&&profile.references.length>0,entry.id+': missing readable references.');
    for(const reference of profile.references){
      require(nonempty(reference.label),entry.id+': missing reference title.');
      const url=new URL(reference.url);require(url.protocol==='https:',entry.id+': unsafe reference URL.');
    }
    require(Array.isArray(profile.parameters),entry.id+': missing parameter guide.');
    const names=new Set(),definition=definitions.find(model=>model.id===entry.id);
    for(const parameter of profile.parameters){
      require(['name','symbol','meaning','help'].every(key=>nonempty(parameter[key]))&&!names.has(parameter.name),entry.id+': incomplete or duplicate parameter guidance.');names.add(parameter.name);
      if(definition)require(Object.hasOwn(definition.parameters??{},parameter.name),entry.id+': unknown parameter '+parameter.name);
    }
    if(definition)for(const name of Object.keys(profile.stateLabels??{}))require(definition.state.some(field=>field.name===name),entry.id+': unknown initial-state label '+name);
    if(profile.exploration)require(nonempty(profile.explorationTitle),entry.id+': missing exploration title.');
    if(profile.related)require(profile.related.every(id=>id!==entry.id&&Object.hasOwn(modelProfiles,id)),entry.id+': unknown related model.');
  }
  return entries.length;
}

export function modelProfileSection(document,spec,{catalogue=[]}={}){
  const profile=modelProfile(spec?.id);if(!profile)return null;
  const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const root=el('div');root.className='model-profile';
  const lead=el('p',profile.summary);lead.className='model-profile-lead';root.append(lead,el('p',profile.introduction));
  const section=(title,...children)=>{const node=el('section');node.append(el('h3',title),...children);root.append(node);return node;};
  const behaviours=el('dl');for(const [title,text] of profile.behaviours)behaviours.append(el('dt',title),el('dd',text));
  section('What it describes',behaviours);
  if(profile.exploration){const explore=section(profile.explorationTitle,el('p',profile.exploration));if(profile.comparison)explore.append(el('p',profile.comparison));}
  if(profile.parameters.length){
    const hasExamples=profile.parameters.some(parameter=>spec.parameters?.[parameter.name]?.default!==undefined);
    const table=el('table'),head=el('thead'),row=el('tr');
    for(const text of ['Parameter','Meaning',hasExamples?'Example value and units':'Units']){const th=el('th',text);th.scope='col';row.append(th);}head.append(row);table.append(head);
    const body=el('tbody');
    for(const parameter of profile.parameters){
      const declared=spec.parameters?.[parameter.name],row=el('tr'),name=el('th',parameter.symbol+' · '+parameter.meaning);name.scope='row';
      const unit=parameter.unit??(typeof declared?.unit==='string'?declared.unit:null),units=unit==='1'?'dimensionless':unit??'See definition';
      const value=declared?.default;
      row.append(name,el('td',parameter.help),el('td',(hasExamples&&value!==undefined?String(value)+' · ':'')+units));body.append(row);
    }
    table.append(body);section('Material parameters',el('p',profile.parameterNote),table);
  }
  section('Starting state',el('p',profile.preparation));
  section('Scope and limitations',el('p',profile.scope),el('p',profile.limits));
  if(profile.equations?.length){
    const equations=el('details');equations.className='model-profile-equations';equations.append(el('summary','The core equations'));
    if(profile.equationIntro)equations.append(el('p',profile.equationIntro));
    for(const [name,expression] of profile.equations)equations.append(el('h4',name),el('p',expression));
    if(profile.equationNote)equations.append(el('p',profile.equationNote));root.append(equations);
  }
  const links=el('ul');for(const reference of profile.references){const item=el('li'),link=el('a',reference.label+' ↗');link.href=reference.url;link.target='_blank';link.rel='noopener noreferrer';item.append(link);links.append(item);}
  section('Read more',links);
  const related=(profile.related??[]).map(id=>catalogue.find(entry=>entry.id===id)).filter(Boolean);
  if(related.length){const list=el('ul');for(const entry of related){const item=el('li'),link=el('a',modelProfile(entry.id)?.title??entry.name);link.href='#catalogue/'+encodeURIComponent(entry.id);item.append(link);list.append(item);}section('Related models and formulations',list);}
  return root;
}
