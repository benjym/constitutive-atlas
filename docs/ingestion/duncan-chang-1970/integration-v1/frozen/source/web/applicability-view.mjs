/** Explicit pending applicability inventory; no solver or overlay filtering. */
const digest=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
const sourcePath=x=>typeof x==='string'&&/^(docs|studies)\/[a-zA-Z0-9_./-]+$/.test(x)&&!x.split('/').some(p=>!p||p==='.'||p==='..');
const pin=x=>x&&sourcePath(x.path)&&digest(x.sha256);
const strings=x=>Array.isArray(x)&&x.length>0&&x.every(v=>typeof v==='string'&&v.trim());
export function validateApplicability(matrix){
  if(matrix?.schema_version!=='0.1'||matrix.kind!=='model-experiment-applicability-matrix'||matrix.independent_review!=='pending'||matrix.reviewer!==null||
    typeof matrix.id!=='string'||!strings(matrix.limitations)||!Array.isArray(matrix.rows)||!matrix.rows.length)throw Error('Unsupported applicability inventory.');
  const d=matrix.dataset;
  if(!d||![d.id,d.material].every(x=>typeof x==='string'&&x.trim())||!pin(d.allocation)||!pin(d.reservations))throw Error('Malformed applicability dataset.');
  const url=new URL(d.source_url);if(url.protocol!=='https:')throw Error('Unsafe dataset source.');
  const seen=new Set();
  for(const row of matrix.rows){
    const m=row?.model;
    if(!m||typeof m.id!=='string'||!/^[a-z][a-z0-9-]*$/.test(m.id)||seen.has(m.id)||m.path!=='models/'+m.id+'.json'||!digest(m.sha256)||
      !['not_assessed','conditional_development_evidence'].includes(row.assessment)||row.scientific_eligibility!=='undetermined'||
      !strings(row.prerequisites)||!strings(row.limitations)||!Array.isArray(row.evidence)||!row.evidence.length||!row.evidence.every(pin))throw Error('Malformed applicability row.');
    seen.add(m.id);
  }
  return matrix;
}
export function applicabilitySection(document,id,matrix,state='loading'){
  const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const section=el('section');section.className='catalogue-applicability';section.style.overflowWrap='anywhere';section.append(el('h3','Model–experiment applicability'));
  if(!matrix){section.append(el('p',state==='failed'?'Applicability inventory could not be loaded. No suitability decision is inferred.':'Loading applicability inventory…'));return section;}
  const row=matrix.rows.find(x=>x.model.id===id);
  if(!row){section.append(el('p','No model–experiment assessment is indexed for this formulation in this build.'));return section;}
  section.append(el('p','Dataset: '+matrix.dataset.material+' · '+matrix.dataset.id));
  section.append(el('p',row.assessment==='not_assessed'?'Pair assessment: not assessed.':'Pair assessment: conditional development evidence; scientific review pending.'));
  section.append(el('p','Scientific eligibility: undetermined. Protocol/channel matching and successful execution do not establish material suitability.'));
  const details=el('details');details.append(el('summary','Scope, prerequisites and exact source identities'));
  for(const [title,items] of [['Prerequisites',row.prerequisites],['Limits of this comparison',row.limitations],['Inventory coverage',matrix.limitations]]){
    details.append(el('h4',title));const list=el('ul');for(const item of items)list.append(el('li',item));details.append(list);
  }
  details.append(el('p','Current model SHA-256: '+row.model.sha256));
  const modelLink=el('a','Exact current model definition');modelLink.href='./'+row.model.path;details.append(modelLink);
  const original=el('a','Measurement source');original.href=matrix.dataset.source_url;original.target='_blank';original.rel='noopener noreferrer';details.append(el('p','Dataset source'),original);
  const sources=el('ul');for(const p of [matrix.dataset.allocation,matrix.dataset.reservations,...row.evidence]){
    const item=el('li'),link=el('a',p.path);link.href='./applicability-records/'+p.path;item.append(link,el('p','SHA-256: '+p.sha256));sources.append(item);
  }
  details.append(el('h4','Bound source and study metadata'),sources);
  const download=el('a','Download the complete applicability inventory');download.href='./applicability.json';details.append(download);
  section.append(details);return section;
}
