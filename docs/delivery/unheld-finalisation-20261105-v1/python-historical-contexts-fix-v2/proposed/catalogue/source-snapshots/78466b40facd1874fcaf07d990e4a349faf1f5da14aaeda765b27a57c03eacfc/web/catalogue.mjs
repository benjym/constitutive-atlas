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
  if(index.reviews!==undefined){
    if(!Array.isArray(index.reviews))throw Error('Malformed source reviews.');
    for(const r of index.reviews){
      if(!r||typeof r.catalogue_id!=='string'||typeof r.id!=='string'||!safePath(r.record_path)||!r.record_path.startsWith('catalogue/reviews/')||seen.has(r.record_path)||
        !safePath(r.definition_path)||!r.definition_path.startsWith('models/')||!safePath(r.dossier)||!r.dossier.startsWith('docs/models/')||
        typeof r.definition_current!=='boolean'||!['pending','changes-requested','accepted'].includes(r.status)||typeof r.independent!=='boolean'||
        ![r.record_sha256,r.definition_sha256].every(x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x))||
        ![r.evidence_ids,r.unresolved].every(x=>Array.isArray(x)&&x.every(y=>typeof y==='string'))||
        ![r.reviewer,r.reviewed_at].every(x=>x===null||(typeof x==='string'&&x.length>0))||
        (r.status!=='pending'&&(!r.independent||!r.reviewer||!r.reviewed_at))||
        (r.status==='pending'&&!r.unresolved.length)||(r.status==='accepted'&&r.unresolved.length))throw Error('Malformed source review.');
      seen.add(r.record_path);
    }
  }
  return index;
}
export function evidenceSection(document,id,index,state='loading'){
  const el=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
  const section=el('section');section.className='catalogue-evidence';section.append(el('h3','Source review and numerical evidence'));
  if(!index){section.append(el('p',state==='failed'?'Evidence could not be loaded. Availability and source links remain usable.':'Loading evidence index…'));return section;}
  const coverage=el('details'),coverageLink=el('a','Evidence index and coverage gaps');coverageLink.href='./evidence.json';coverage.append(el('summary','What this evidence covers'),el('p',index.coverage_note),el('p','Packaging checks receipt and artifact integrity. It does not rerun numerical studies, establish independent scientific review or demonstrate experimental validity.'),coverageLink);section.append(coverage);
  section.append(el('h4','Recorded source reviews'));
  section.append(el('p','Review records describe the definition and questions at the time they were written. All retained revisions are shown; later records may document progress. A matching model definition does not imply acceptance of its numerical implementation or scientific use.'));
  const reviews=(index.reviews||[]).filter(r=>r.catalogue_id===id);
  if(!reviews.length)section.append(el('p',index.reviews===undefined?'Source reviews were not indexed in this build.':'No formal source-review record for this formulation is indexed. This does not mean its sources have been scientifically accepted.'));
  for(const r of reviews){
    const entry=el('article');entry.className='catalogue-evidence-record';
    entry.append(el('h4',r.id),el('p','Recorded source-review status: '+r.status+' · '+(r.definition_current?'Matches current definition bytes':'Historical definition; current bytes differ or are unavailable')));
    entry.append(el('p','Independence declared: '+(r.independent?'yes':'no')+' · Review date: '+(r.reviewed_at||'not recorded')));
    if(r.reviewer)entry.append(el('p','Recorded attribution: '+r.reviewer));
    if(r.status==='pending')entry.append(el('p','Scientific decision pending. Technical checks and numerical passes do not supply acceptance.'));
    if(r.unresolved.length){entry.append(el('p','Recorded unresolved questions'));const list=el('ul');for(const question of r.unresolved)list.append(el('li',question));entry.append(list);}
    const receipt=el('a','Original source-review record');receipt.href='./evidence-records/'+r.record_path;entry.append(receipt);
    const metadata=el('details');metadata.append(el('summary','Review identity and evidence references'),el('p','Definition SHA-256: '+r.definition_sha256),el('p','Record SHA-256: '+r.record_sha256),el('p','Dossier path: '+r.dossier),el('pre',JSON.stringify({evidence_ids:r.evidence_ids},null,2)));entry.append(metadata);section.append(entry);
  }
  section.append(el('h4','Retained numerical evidence'));
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
