const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const texts=v=>Array.isArray(v)&&v.length>0&&v.every(s=>typeof s==='string'&&s.trim());
export function validateReview(v){
  if(v?.id!=='kfs-development-agent-v1'||v.outcome!=='accept_qualified_reporting'||v.model_admission!==false||v.redistribution_permission!==false||!hash(v.decision_sha256))throw Error('Unsupported reporting decision');
  if(v.decision_url!=='./reporting-review/decision.json'||v.review_url!=='./reporting-review/review.html')throw Error('Unsafe reporting links');
  if(!texts([v.scope,v.reviewer,v.date])||!texts(v.qualifications)||!texts(v.excluded_claims))throw Error('Missing review scope or qualifications');
  if(!Array.isArray(v.claims)||v.claims.length!==7||new Set(v.claims.map(c=>c.id)).size!==7||v.claims.some(c=>!/^C[1-7]$/.test(c.id)||!texts([c.title,c.reason])))throw Error('Incomplete reporting claims');
  return v;
}
export function renderReview(doc,data){
  const v=validateReview(data),put=(id,text)=>{doc.getElementById(id).textContent=text;};
  put('reporting-review-status','Qualified reporting accepted by a separate agent. Model admission and data-release permission remain open.');
  put('reporting-review-scope',v.scope+' This decision covers the density3 factorial comparison and its pinned TMD7 connection; it does not review the separate pressure3 comparison or TMD2 + IGS calculation.');
  put('reporting-review-identity',v.reviewer+' · '+v.date+' · Decision SHA-256: '+v.decision_sha256);
  const links=doc.getElementById('reporting-review-links');links.replaceChildren();
  for(const [title,url] of [['Read the independent review',v.review_url],['Download the exact decision',v.decision_url]]){const a=doc.createElement('a');a.textContent=title;a.href=url;links.append(a,doc.createTextNode(' '));}
  for(const [id,items] of [['reporting-review-claims',v.claims.map(c=>c.id+' — '+c.title+': '+c.reason)],['reporting-review-qualifications',v.qualifications],['reporting-review-exclusions',v.excluded_claims]])doc.getElementById(id).replaceChildren(...items.map(text=>{const li=doc.createElement('li');li.textContent=text;return li;}));
}
export async function mountReview(doc,fetcher=fetch){
  try{const response=await fetcher('./development.json');if(!response.ok)throw Error('Evidence download failed');renderReview(doc,(await response.json()).reporting_review);}
  catch(error){const node=doc.getElementById('reporting-review-status');node.textContent='Reporting review unavailable: '+error.message;node.setAttribute('role','alert');}
}
if(typeof document!=='undefined')mountReview(document);
