"""Read-only retrospective audit; saved receipts are never rewritten."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from atlas.model import load
paths=['docs/ingestion/sls-comsol63/manifest.json','docs/ingestion/sls-comsol63/execution-v1/manifest.json','docs/reviews/sls-comsol63-scientific-v1/manifest.json','docs/admission/sls-comsol63-approved-v1/manifest.json','docs/reviews/sls-web-v1/manifest.json','docs/reviews/sls-atlas-integration-v1/manifest.json','docs/reviews/sls-live-v1/manifest.json','docs/reviews/sls-release-v1/manifest.json']
counts={}
for name in paths:
 p=ROOT/name;obj=json.loads(p.read_text());groups=[obj['sha256']] if 'sha256' in obj else [obj['files']] if 'files' in obj else [obj['input_sha256'],obj['review_sha256']] if 'input_sha256' in obj else [obj];n=0
 for group in groups:
  for file,digest in group.items():
   if 'input_sha256' in obj:checked_receipt(ROOT,name,file,digest)
   else:assert hashlib.sha256((p.parent/file).read_bytes()).hexdigest()==digest,(name,file)
   n+=1
 counts[name]=n
model=ROOT/'models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json';load(model)
assert hashlib.sha256(model.read_bytes()).hexdigest()=='eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906'
review=json.loads((ROOT/'catalogue/agent-reviews/sls-comsol63-agent-v1.json').read_text());assert review['status']=='accepted' and len(review['checklist'])==9 and all(x['outcome']=='pass' for x in review['checklist']) and not review['blocking_findings']
run=json.loads((HERE/'release-ci-recheck.json').read_text());assert run['headSha']=='f18db8e75d27cf182f2c03dfcd6534b7f51d5a86' and run['conclusion']=='success' and len(run['jobs'])==5 and all(x['conclusion']=='success' for x in run['jobs'])
statuses=json.loads((HERE/'release-deploy-recheck.json').read_text());assert statuses[0]['state']=='success'
print(json.dumps(dict(ok=True,manifest_receipts=counts,total_receipts=sum(counts.values()),accepted_checklist_items=9,ci_jobs=5,model_unchanged=True),indent=2))
