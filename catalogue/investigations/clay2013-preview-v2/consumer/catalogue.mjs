/** Catalogue navigation and evidence presentation; no solver dependencies. */
export function catalogueHash(id){return '#catalogue/'+encodeURIComponent(id);}
export function catalogueRoute(hash){
  const anchor=hash.replace(/^#/, '');
  if(anchor.startsWith('catalogue/')){
    try{const id=decodeURIComponent(anchor.slice(10));return {page:'catalogue',modelId:id||null,invalid:!id};}
    catch{return {page:'catalogue',modelId:null,invalid:true};}
  }
  return {page:['catalogue','methods','recorded'].includes(anchor)?anchor:'laboratory',modelId:null,invalid:false};
}
const safePath=path=>typeof path==='string'&&path.length>0&&!path.startsWith('/')&&!path.split('/').some(x=>!x||x==='.'||x==='..')&&/^[a-zA-Z0-9_./-]+$/.test(path);
export function validateEvidenceIndex(index){
  if(index?.schema_version!=='0.1'||index.kind!=='catalogue-evidence-index'||typeof index.coverage_note!=='string'||!Array.isArray(index.records))throw Error('Unsupported evidence index.');
  const seen=new Set();
  for(const r of index.records){
    if(!r||typeof r.catalogue_id!=='string'||!safePath(r.record_path)||!safePath(r.definition_path)||!r.definition_path.startsWith('models/')||seen.has(r.record_path)||
      !['numerical-evidence','research-manifest'].includes(r.kind)||typeof r.definition_current!=='boolean'||typeof r.scope!=='string'||
      !(r.outcome===null||typeof r.outcome==='string')||!Array.isArray(r.limitations)||r.limitations.some(x=>typeof x!=='string')||
      ![r.record_sha256,r.definition_sha256].every(x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x)))throw Error('Malformed evidence record.');
    seen.add(r.record_path);
  }
  return index;
}
export function evidenceSection(document,id,index,state='loading'){
  const el=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
  const section=el('section');section.className='catalogue-evidence';section.append(el('h3','Retained numerical evidence'));
  if(!index){section.append(el('p',state==='failed'?'Evidence could not be loaded. Availability and source links remain usable.':'Loading evidence index…'));return section;}
  const coverage=el('details'),coverageLink=el('a','Evidence index and coverage gaps');coverageLink.href='./evidence.json';coverage.append(el('summary','What this evidence covers'),el('p',index.coverage_note),el('p','Packaging checks receipt and artifact integrity. It does not rerun numerical studies, establish independent scientific review or demonstrate experimental validity.'),coverageLink);section.append(coverage);
  const records=index.records.filter(r=>r.catalogue_id===id);
  if(!records.length)section.append(el('p','No evidence record for this formulation is indexed in this build. This does not establish that an implementation is absent.'));
  for(const r of records){
    const entry=el('article');entry.className='catalogue-evidence-record';
    entry.append(el('h4',r.kind==='research-manifest'?'Research implementation study':'Numerical investigation'));
    entry.append(el('p',(r.outcome===null?'Outcome: consult retained record':'Recorded outcome: '+r.outcome)+' · '+(r.definition_current?'Matches current definition bytes':'Historical definition; current bytes differ or are unavailable')));
    entry.append(el('p',r.scope||'This manifest has no summary scope field. Consult the recorded scope, policies and review flags below.'));
    if(r.kind==='research-manifest')entry.append(el('p','This research study does not add the formulation to the browser solver.'));
    if(r.limitations.length){const list=el('ul');for(const text of r.limitations)list.append(el('li',text));entry.append(list);}
    const links=el('p'),receipt=el('a','Original evidence record');receipt.href='./evidence-records/'+r.record_path;links.append(receipt);
    if(r.definition_current){const definition=el('a','Matched definition JSON');definition.href='./'+r.definition_path;links.append(document.createTextNode(' · '),definition);}
    entry.append(links);
    const metadata=el('details');metadata.append(el('summary','Recorded scope, policies and review flags'),el('p','Definition SHA-256: '+r.definition_sha256),el('p','Record SHA-256: '+r.record_sha256));
    if(r.details||r.admission_flags)metadata.append(el('pre',JSON.stringify({admission_flags:r.admission_flags,...r.details},null,2)));
    entry.append(metadata);
    section.append(entry);
  }
  return section;
}
