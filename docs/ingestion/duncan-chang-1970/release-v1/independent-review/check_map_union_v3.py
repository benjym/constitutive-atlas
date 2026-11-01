"""Prospective saved-source overlay test, no parent-tree mutations."""
from pathlib import Path
import json,hashlib,sys,tempfile,shutil
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
pre=Path('docs/ingestion/duncan-chang-1970/release-v2');combined=json.loads((root/pre/'remote-map-union-v1/combined-plan.json').read_text());plan=json.loads((root/pre/'preservation-v3/preservation-plan.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ops={x['path']:x for x in combined['operations']}
for p,o in ops.items():
 assert h(root/o['proposed_path'])==o['proposed_sha256']
 assert (h(root/p) if (root/p).exists() else None)==o['original_sha256']
 old=json.loads((root/p).read_text()) if (root/p).exists() else {'documents':{},'entries':[]};new=json.loads((root/o['proposed_path']).read_text())
 assert all(new['documents'].get(k)==v for k,v in old['documents'].items())
 assert all(e in new['entries'] for e in old['entries'])
for r in json.loads((root/pre/'remote-map-union-v1/map-proposals.json').read_text()):
 new=json.loads((root/ops[r['path']]['proposed_path']).read_text())
 for k in ['own_sha256','remote_sha256']:
  a=root/'catalogue/source-snapshots'/r[k]/r['path'];assert h(a)==r[k];old=json.loads(a.read_text())
  assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries'] for e in old['entries'])
for p,v in plan['document_pins'].items():assert h(root/p)==v
assert not plan['document_pin_rollforwards']
bindings=[]
for version in ['v1','v2','v3']:
 bindings+=json.loads((root/pre/f'preservation-{version}/preservation-plan.json').read_text())['bindings']
with tempfile.TemporaryDirectory(prefix='duncan-review-union-v3-') as d:
 virtual=Path(d)
 def copy(p,source=None):
  dest=virtual/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source or root/p,dest)
 for b in bindings:
  copy(b['document']);copy(b['archived_path']);assert h(root/b['archived_path'])==b['sha256']
  side=str(Path(b['document']).parent/'source-archive-map.json')
  if side in ops:copy(side,root/ops[side]['proposed_path'])
  elif (root/side).exists():copy(side)
  original=b['original_path']
  if original in ops:copy(original,root/ops[original]['proposed_path'])
  elif (root/original).exists():copy(original)
 for b in bindings:checked_receipt(virtual,b['document'],b['original_path'],b['sha256'])
print(json.dumps({'status':'PASS','base':combined['base'],'operations':len(ops),'new_bindings':len(plan['bindings']),'prior_and_new_bindings_replayed':len(bindings),'new_document_pins':len(plan['document_pins']),'rollforwards':0,'both_local_remote_maps_exact_archived_and_inclusive':True},indent=2))
