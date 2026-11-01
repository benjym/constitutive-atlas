"""Bounded documentary completion for actual review validators; no build/artifact calls."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
SOURCE=Path('/private/tmp/atlas-control-partition-support-v1/source');BASE='3873a48b256ed37cbc78378ee6b41d73139676f8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def fetch(p):
 try:return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT,stderr=subprocess.DEVNULL)
 except subprocess.CalledProcessError:return None
def install(p,b):
 q=SOURCE/p
 assert not Path(p).is_absolute()and '..'not in Path(p).parts
 if q.exists():assert q.read_bytes()==b,'preserve existing bytes '+p
 else:q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
registry=json.loads((SOURCE/'catalogue/approved-models.json').read_text())['models']
needles=['power-creep','burgers','sls','j2-linear','orthotropic','maxwell','norsand','lade-duncan','hill']
roots=[a for a in registry if any(n in a['model_id']for n in needles)and a.get('review',{}).get('kind')=='agent-model-review']
entries=[];gaps=[];installed=[]
def satisfy(document,p,h):
 q=SOURCE/p;canonical='catalogue/source-snapshots/'+h+'/'+p
 if q.is_file()and sha(q)==h:location=p
 else:
  b=fetch(p)
  if b is None or hashlib.sha256(b).hexdigest()!=h:b=fetch(canonical)
  if b is None or hashlib.sha256(b).hexdigest()!=h:
   if (SOURCE/canonical).is_file()and sha(SOURCE/canonical)==h:b=(SOURCE/canonical).read_bytes()
  if b is None or hashlib.sha256(b).hexdigest()!=h:
   gaps.append(dict(document=document,path=p,sha256=h,reason='Exact bytes unavailable through named original/canonical baseline paths'));return
  location=canonical if q.exists()else p
  install(location,b);installed.append(location)
 entries.append(dict(document=document,path=p,sha256=h,location=location))
for a in roots:
 rp=a['review']['path'];r=json.loads((SOURCE/rp).read_text());assert sha(SOURCE/rp)==a['review']['sha256']
 sidecar=str(Path(rp).parent/'source-archive-map.json');b=fetch(sidecar)
 if b is not None and not(SOURCE/sidecar).exists():install(sidecar,b)
 for item in r['artifacts']:satisfy(rp,item['path'],item['sha256'])
# Explicit packager documentary/text inputs outside review artifact sets.
explicit=['docs/admission/maxwell-agent-v2/approval.json','docs/admission/j2-approved-v2/approval.json','docs/admission/orthotropic-ogs-approved-v1/approval.json','docs/reviews/maxwell-checklist-v2/README.md','docs/ingestion/power-creep-itasca900/review-v2/README.md','docs/reviews/j2-scientific-v2/README.md','docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/catalogue-copy-followup/receipt.json','docs/ingestion/orthotropic-ogs/source-v1/README.md','docs/ingestion/orthotropic-ogs/scientific-review-v1/report.md','docs/models/hill-abaqus2025.md','docs/ingestion/lade-duncan-1975/atlas-integration-v1/independent-review/interface-review-receipt.json','docs/ingestion/maxwell-itasca900/atlas-controller-v1/independent-review/receipt.json','docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json','docs/ingestion/norsand-1993/approval-v1/REPORT.md']
for p in explicit:
 b=fetch(p)
 if b is None:gaps.append(dict(path=p,reason='Explicit guard documentary input absent at frozen base'))
 elif not(SOURCE/p).exists():install(p,b);installed.append(p)
# The actual source-only validator owns receipt resolution semantics, including maps.
sys.dont_write_bytecode=True;sys.path.insert(0,str(SOURCE))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
validation=[]
for a in roots:
 rp=a['review']['path']
 try:
  r=validate_review(SOURCE/rp,root=SOURCE,for_approval=True)
  assert approval_entry(SOURCE/rp,root=SOURCE)==a
  validation.append(dict(model=a['model_id'],passed=True))
 except Exception as e:validation.append(dict(model=a['model_id'],passed=False,error=type(e).__name__+': '+str(e)))
# Direct current guards intentionally remain direct: record their failures rather than archive-waive them.
raw=[]
for a in roots:
 if any(n in a['model_id']for n in ['power-creep','norsand']):
  for item in a['supporting_files']:
   p=SOURCE/item['path']
   if not p.is_file()or sha(p)!=item['sha256']:raw.append(dict(model=a['model_id'],path=item['path'],expected=item['sha256'],actual=sha(p)if p.is_file()else None,kind='direct-current-supporting-file-check; canonical archive does not override it'))
# Maxwell/Lade actual checked_receipt contexts.
checked=[]
for a in roots:
 if 'maxwell'in a['model_id']or'lade-duncan'in a['model_id']:
  document='docs/admission/maxwell-agent-v2/approval.json'if'maxwell'in a['model_id']else a['review']['path']
  sidecar=str(Path(document).parent/'source-archive-map.json');b=fetch(sidecar)
  if b is not None and not(SOURCE/sidecar).exists():install(sidecar,b)
  for item in a['supporting_files']:
   try:location=checked_receipt(SOURCE,document,item['path'],item['sha256']);checked.append(dict(document=document,path=item['path'],passed=True,location=str(location.relative_to(SOURCE))))
   except Exception as e:checked.append(dict(document=document,path=item['path'],passed=False,error=str(e)))
save('semantic-closure.json',dict(base=BASE,scope='Actual nine agent-review validators plus exact Maxwell/Lade checked_receipt contexts and direct Power/NorSand supporting-file loops; no compiler/package/artifact execution',review_validator_results=validation,checked_receipt_results=checked,current_raw_supporting_failures=raw,exact_artifact_edges=entries,installed_additions=sorted(set(installed)),missing_bytes=gaps,complete=False,guarded_package_ready=False,uncovered=['Generated files and new current qualification/build-review receipts are not yet produced','Other dynamic packager and profile-specific freeze semantics remain separately qualified','Hill/Lade exact reviewed binary availability is not inferred from restored receipt bytes']))
files={p.relative_to(SOURCE).as_posix():sha(p)for p in SOURCE.rglob('*')if p.is_file()}
original=json.loads((ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json').read_text())
assert all(sha(Path(original['source_directory'])/p)==h and files[p]==h for p,h in original['source_files'].items())
sets=json.loads((OUT/'patched-source-manifests.json').read_text())
assert all(files[p]==h for info in sets['profiles'].values()for p,h in info['files'].items())
save('support-source-freeze-v2.json',dict(identity='generic-control-isolated-support-context-v2-final',source_directory=str(SOURCE),runtime_receipt_sha256=sha(ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json'),files=files,file_count=len(files),original582_source_and_copy_verified=True,semantic_closure_report_sha256=sha(OUT/'semantic-closure.json'),qualification_ready=False))
print(json.dumps(dict(files=len(files),review_results=validation,missing_bytes=len(gaps),direct_current_failures=len(raw),checked_receipt_failures=sum(not x['passed']for x in checked))))
