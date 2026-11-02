"""Seal reviewable candidates only; never install into the release tree."""
from pathlib import Path
import gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-final-context-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
c=json.loads((H/'SEALED-COMPOSITION.json').read_text());p=json.loads((H/'SEALED-PRESERVATION.json').read_text());s=json.loads((H/'SEALED-SUMMARY.json').read_text());assert s['newly_broken']==s['changed_failure']==s['unresolved_context_requests']==0
for n in ['INTEGRITY.json','SOURCE-GUARDS.json']:assert json.loads((H/n).read_text())['passed']
targets={**c['selected_source_and_admission_files'],**p['files']};installation={}
for n,h in sorted(targets.items()):
 assert sha(C/n)==h
 dst=H/'installation-candidates'/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((C/n).read_bytes())
 installation[n]={'before_sha256':sha(R/n) if (R/n).exists() else None,'sha256':h,'candidate':'installation-candidates/'+n}
write(H/'INSTALLATION.json',{'installed':False,'source_admission_tracking_count':33,'unique_candidate_count':len(targets),'files':installation,'canonical_review_sha256':sha(R/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json'),'requires_independent_review':True})
files={q.relative_to(H).as_posix():sha(q) for q in H.rglob('*') if q.is_file() and q.name!='MANIFEST.json' and '__pycache__' not in q.parts}
write(H/'MANIFEST.json',{'identity':'bingham-final-imported-context-v1','status':'prospective-source-only-review-request','files':files,'installation_sha256':sha(H/'INSTALLATION.json'),'summary':s,'build_material_remote_calls':0,'independent_acceptance_claimed':False})
print(json.dumps({'manifest_sha256':sha(H/'MANIFEST.json'),'files':len(files),'unique_installation_candidates':len(targets),'source_admission_tracking':33,'preservation_candidates':len(p['files'])},indent=2))
