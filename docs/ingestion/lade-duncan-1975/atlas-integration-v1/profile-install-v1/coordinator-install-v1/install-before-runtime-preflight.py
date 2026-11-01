"""Guarded application of the exact independently accepted preservation plan."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from tools.build_implicit_path_laboratory import runtime_manifest
OUT=Path(__file__).resolve().parent
PROPOSAL=OUT.parent/'revision-v2'
REVIEW=ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/profile-preservation-review/review-receipt.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 assert not (OUT/'INSTALLED.json').exists(),'Refuse repeated installation'
 review=json.loads(REVIEW.read_bytes());assert review['status']=='accepted' and review.get('blocking_findings')==[]
 plan=json.loads((PROPOSAL/'PLAN.json').read_bytes());white=json.loads((PROPOSAL/'APPLY_WHITELIST.json').read_bytes())
 assert sha((PROPOSAL/'PLAN.json').read_bytes())=='e0439b53c593c38ca75488691bba2eeeca027be88a4a9195e1fc0016ca85271a'
 assert sha((PROPOSAL/'APPLY_WHITELIST.json').read_bytes())=='276540c16c1320b1247f740f5195eeba5dd187a23aa7d2f500012ca0dd59a1c0'
 assert plan['passed'] and len(white['writes'])==26
 # All old states and all candidate bytes are checked before any mutation.
 writes=[]
 for row in white['writes']:
  name=row['original_path'];target=ROOT/name
  assert not target.is_symlink(),name
  assert (sha(target.read_bytes()) if target.exists() else None)==row['old_sha256'],name
  prefix='snapshots' if row['operation']=='create_canonical_snapshot' else 'candidates'
  data=(PROPOSAL/prefix/name).read_bytes();assert sha(data)==row['new_sha256'],name
  writes.append((row,target,data))
 source=plan['source'];old=ROOT/source['original_path'];future=ROOT/source['future_copy']
 assert sha(old.read_bytes())==source['old_sha256']
 expected=json.loads((ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/EXPECTED_F_BINDING.json').read_bytes())
 assert sha(future.read_bytes())==expected['expected_runtime']['files']['include/atlas/solver.hpp']
 for row,target,data in sorted(writes,key=lambda v:v[0]['operation']!='create_canonical_snapshot'):
  assert (sha(target.read_bytes()) if target.exists() else None)==row['old_sha256'],row['original_path']
  target.parent.mkdir(parents=True,exist_ok=True)
  if row['old_sha256'] is None:
   with target.open('xb') as f:f.write(data)
  else:target.write_bytes(data)
 # Every prior binding must remain valid even before source replacement.
 for c in plan['combined_overlay_checks']:checked_receipt(ROOT,c['document'],c['original_path'],c['old_sha256'])
 assert sha(old.read_bytes())==source['old_sha256'];old.write_bytes(future.read_bytes())
 current=runtime_manifest();assert current==expected['expected_runtime']
 for c in plan['combined_overlay_checks']:checked_receipt(ROOT,c['document'],c['original_path'],c['old_sha256'])
 for row in json.loads((ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/legacy-prerequisite-recovery-v1/RECOVERY.json').read_bytes())['records']:
  assert sha((ROOT/row['original_path']).read_bytes())==row['current_full_sha256']
 result={'status':'passed','review':{'path':REVIEW.relative_to(ROOT).as_posix(),'sha256':sha(REVIEW.read_bytes())},'writes':white['writes'],'installed_source':{'path':source['original_path'],'sha256':sha(old.read_bytes())},'runtime':current,'old_binding_checks':len(plan['combined_overlay_checks']),'full_raw_hashes_unchanged':57,'scope':'Exact reviewed metadata preservation and F profile source installation. No new compilation or material execution.'}
 (OUT/'INSTALLED.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','writes':len(writes),'runtime_sha256':current['sha256'],'old_binding_checks':len(plan['combined_overlay_checks'])}))
if __name__=='__main__':main()
