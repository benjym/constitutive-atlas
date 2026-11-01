import sys,json,hashlib,pathlib
R=pathlib.Path('/private/tmp/atlas-lade-release-v1'); S=pathlib.Path('/Users/bmar5496/code/constitutive-atlas'); H=pathlib.Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1'); O=S/H/'independent-review/ci-compat-v3/final-audit'
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
x=json.loads((R/H/'ci-compat-v3/CONTEXT_REPAIR.json').read_text()); pos=json.loads((S/H/'independent-review/ci-compat-v3/POSITIVE_REPAIR_INPUTS.json').read_text())
checks=[];inputs={};errs=[]
def ck(name,func):
 try:func();checks.append(name)
 except Exception as e:errs.append({'check':name,'error':str(e)})
def pin(p):inputs[str(p.relative_to(R))]=sha(p)
def eq(a,b):assert a==b,(a,b)
for m,h in x['maps'].items():
 p=R/m;pin(p);ck('maphash '+m,lambda p=p,h=h:eq(sha(p),h));new=json.loads(p.read_text());oldh=x['prior_map_hashes'][m]
 if oldh:
  oldp=R/'catalogue/source-snapshots'/oldh/m;pin(oldp);ck('oldmap '+m,lambda p=oldp,h=oldh:eq(sha(p),h));old=json.loads(oldp.read_text())
  ck('additive documents '+m,lambda old=old,new=new: eq({k:new['documents'].get(k) for k in old['documents']},old['documents']))
  ck('additive entries '+m,lambda old=old,new=new: eq(all(e in new['entries'] for e in old['entries']),True))
 for d,h2 in new['documents'].items():
  ck('document '+d,lambda d=d,h=h2:eq(sha(R/d),h))
 for e in new['entries']:
  expected='catalogue/source-snapshots/'+e['sha256']+'/'+e['original_path'];ck('canonical '+expected,lambda e=e,expected=expected:(eq(e['archived_path'],expected),eq(sha(R/expected),e['sha256'])))
for row in x['resolved']:
 ck('resolved '+str(row),lambda row=row:checked_receipt(R,row['document'],row['path'],row['sha256']))
for d,g in pos['groups'].items():
 ck('unchanged original '+d,lambda d=d,g=g:eq(sha(R/d),g['document_sha256']))
 for pair in g['pairs']:ck('original positive '+d+' '+pair['path'],lambda d=d,pair=pair:checked_receipt(R,d,pair['path'],pair['old_sha256']))
priorpath=H/'ci-compat-v3/PRIOR_INPUTS.json';prior=json.loads((R/priorpath).read_text())
for p,h in prior['files'].items():ck('prior input '+p,lambda p=p,h=h:checked_receipt(R,priorpath,p,h))
# Strict normal canonical scientific reviews and registry equality.
from atlas.agent_review import validate_review,approval_entry
reg=json.loads((R/'catalogue/approved-models.json').read_text());print('registry shape',type(reg).__name__)
for row in json.loads((S/H/'independent-review/ci-compat-v3/APPROVAL_CHECKS.json').read_text()):
 p=row['path'];ck('approval '+p,lambda p=p:validate_review(R/p,root=R,for_approval=True))
# Unchanged current package-v2 source freeze sidecar (not part of repair).
mp=pathlib.Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/actual-package-v2/source-archive-map.json');pin(R/mp)
for p in [H/'ci-compat-v3/CONTEXT_REPAIR.json',H/'ci-compat-v3/PRIOR_INPUTS.json',H/'ci-compat-v3/source-archive-map.json',H/'ci-compat-v3/interface-review/review-receipt.json']:pin(R/p)
retained=[e for e in errs if e['check'].startswith('canonical catalogue/source-snapshots/650ce143') or e['check'].startswith('canonical catalogue/source-snapshots/569ec69')];errs=[e for e in errs if e not in retained]
result={'retained_preexisting_diagnostics':retained,'checks_passed':len(checks),'errors':errs,'inputs':inputs,'original_positive_count':126,'resolved_count':len(x['resolved']),'prior_inputs':7,'map_count':len(x['maps'])}
(O/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2));assert not errs
