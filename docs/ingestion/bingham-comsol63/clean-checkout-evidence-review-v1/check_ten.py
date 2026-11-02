import sys,json,hashlib,zipfile
from pathlib import Path
root=Path('/private/tmp/atlas-bingham-release-v3'); clean=Path('/private/tmp/atlas-bingham-clean-review-v2'); out=root/'docs/ingestion/bingham-comsol63/clean-checkout-evidence-review-v1'; packet=root/'docs/ingestion/bingham-comsol63/clean-checkout-evidence-v1'
sys.path.insert(0,str(root)); from atlas.evidence import checked_receipt
install=json.loads((packet/'INSTALLATION.json').read_text()); results=[]
doc='docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json'
for p,v in install['files'].items():
 b=(packet/v['candidate']).read_bytes(); assert hashlib.sha256(b).hexdigest()==v['sha256']; assert b==(root/p).read_bytes(); assert not (clean/p).exists()
 r={'path':p,'sha256':v['sha256'],'candidate_equal_local':True,'tracked_before':False}
 if 'archive_member' in v:
  with zipfile.ZipFile(root/v['tracked_qualified_archive']) as z: assert z.read(v['archive_member'])==b
  original=p.split('/',3)[3]; r['original_path']=original; r['zip_equal']=True
  assert checked_receipt(root,doc,original,v['sha256'])==root/p
  try: checked_receipt(clean,doc,original,v['sha256'])
  except ValueError as e: r['before_failure']=str(e)
  else: raise AssertionError('missing snapshot unexpectedly accepted')
 target=clean/p; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(b)
 if 'archive_member' in v:
  assert checked_receipt(clean,doc,original,v['sha256'])==target; r['after_receipt']='PASS'
 results.append(r)
(out/'TEN-ADDITIONS-CHECK.json').write_text(json.dumps({'results':results,'new_files':len(results),'old_files_modified':0},indent=2)+'\n')
print('PASS',len(results),'exact additions; three ZIP/receipt before-failure/after-pass witnesses')
