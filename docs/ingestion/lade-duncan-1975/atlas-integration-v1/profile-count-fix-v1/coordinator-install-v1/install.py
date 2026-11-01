"""Exact reviewed positive-fixture correction with old-byte preservation."""
from pathlib import Path
import hashlib,json,os,sys,uuid
HERE=Path(__file__).resolve().parent;P=HERE.parent;ROOT=HERE.parents[5];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda b:hashlib.sha256(b).hexdigest()
def pin(p,h):
 b=p.read_bytes();assert sha(b)==h,str(p);return b
def prior(p,h):
 assert not p.is_symlink(),str(p)
 assert (not p.exists()) if h is None else (p.is_file() and sha(p.read_bytes())==h),str(p)
review=ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/profile-count-fix-v1/review-receipt.json'
r=json.loads(pin(review,'79063d66ef165aebf0a6370e2e4771780a154caa6245dc191b44290e53751e53'));assert r['status']=='accepted' and r['reviewer_run']=='/root/lade_source_review'
f=json.loads(pin(P/'SOURCE_FREEZE.json','7f54923b8c99907de3438ed1f1c2092fd291a4ffb6e9d737b18cc1758fa61b26'))
for row in f['files']:pin(ROOT/row['original_path'],row['old_sha256'])
plan=json.loads(pin(P/'PROPOSAL.json','368535e58e4a70024170e5bd572b9a5dbc93c04077a36d42f49fd17495a60ec6'))
w=json.loads(pin(P/'APPLY_WHITELIST.json','9afa29f23ef8fac9edcf7a83b9de247b8fd168b28adfb92cf84ce249cfc1f4a2'))
maps={x['original_path']:x for x in plan['maps']};archives={x['canonical_archive']:x for x in plan['archives']};ops=[]
for row in sorted(w['metadata_writes'],key=lambda x:0 if x['operation']=='create_canonical_snapshot' else 1):
 name=row['original_path'];assert not Path(name).is_absolute() and '..' not in Path(name).parts
 src=P/(archives[name]['snapshot'] if name in archives else maps[name]['candidate'])
 ops.append((row,pin(src,row['new_sha256'])))
row=w['source_replacement'];ops.append((row,pin(P/row['future_copy'],row['new_sha256'])))
assert len(ops)==17
for row,data in ops:prior(ROOT/row['original_path'],row['old_sha256'])
state={'status':'preflight-passed','operations':[],'review_sha256':sha(review.read_bytes())}
def save():
 (HERE/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
save()
try:
 for row,data in ops:
  dest=ROOT/row['original_path'];prior(dest,row['old_sha256']);dest.parent.mkdir(parents=True,exist_ok=True)
  if row['old_sha256'] is None:
   with dest.open('xb') as out:out.write(data)
  else:
   stage=dest.with_name('.'+dest.name+'.lade-count-'+uuid.uuid4().hex)
   with stage.open('xb') as out:out.write(data)
   prior(dest,row['old_sha256']);os.replace(stage,dest)
  pin(dest,row['new_sha256']);state['operations'].append(row);save()
 for c in plan['checks']:
  assert c['outcome']=='passed';checked_receipt(ROOT,c['document'],c['original_path'],c['old_sha256'])
 state.update(status='passed',checked_bindings=len(plan['checks']));save()
 with (HERE/'INSTALLED.json').open('x') as out:json.dump(state,out,indent=2);out.write('\n')
 print(json.dumps({'status':'passed','operations':17,'bindings':len(plan['checks'])}))
except BaseException as e:
 state.update(status='failed',error=str(e));save();raise
