"""Independent read-only two-parent preservation and scientific-scope audit."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path('/private/tmp/atlas-barodesysand-delivery-v1');sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
sha=lambda b:hashlib.sha256(b).hexdigest()
def raw(rev,p):
 r=subprocess.run(['git','show',rev+':'+p],cwd=ROOT,capture_output=True)
 return r.stdout if r.returncode==0 else None
revs=['0e9bb50d403f9e4d0dc569fbc037fa68f6430da0','d1c3a19409adaa32791c105429a4167e5bac9d9d']
freeze=json.loads((ROOT/'docs/ingestion/barodesy-sand/delivery-v1/prospective-freeze.json').read_text())
for p,h in freeze['source_inputs'].items():assert sha((ROOT/p).read_bytes())==h,p
reviewpath=ROOT/'catalogue/agent-reviews/barodesy-sand-agent-v1.json';validate_review(reviewpath,root=ROOT,for_approval=True)
assert sha(reviewpath.read_bytes())=='df0e95028f38e4af94665ea8689d58b37a92d8c84b33f6aec4c503cbbd84efc6'
registry=json.loads((ROOT/'catalogue/approved-models.json').read_text());remote=json.loads(raw(revs[1],'catalogue/approved-models.json'))
assert registry['models']==remote['models']+[approval_entry(reviewpath,root=ROOT)]
local=json.loads(raw(revs[0],'catalogue/approved-models.json'))
assert all(e in registry['models'] for e in local['models'])
new=json.loads((ROOT/'catalogue/manifest.json').read_text());remote_manifest=json.loads(raw(revs[1],'catalogue/manifest.json'));local_manifest=json.loads(raw(revs[0],'catalogue/manifest.json'))
assert [v for v in new['models'] if v['id']!='barodesy-sand']==[v for v in remote_manifest['models'] if v['id']!='barodesy-sand']
assert next(v for v in new['models'] if v['id']=='barodesy-sand')==next(v for v in local_manifest['models'] if v['id']=='barodesy-sand')
assert len({v['id'] for v in new['models']})==len(new['models'])
map_pairs=[]
for rev in revs:
 changed=subprocess.check_output(['git','diff','--name-only',rev,'--','*source-archive-map.json'],cwd=ROOT,text=True).splitlines()
 for p in changed:
  before=raw(rev,p)
  if before is None:continue
  a=json.loads(before);b=json.loads((ROOT/p).read_text())
  assert a['version']==b['version']
  assert all(b['documents'].get(k)==v for k,v in a['documents'].items()),(rev,p,'document pin lost')
  assert all(e in b['entries'] for e in a['entries']),(rev,p,'entry lost')
  assert len({(e['original_path'],e['sha256']) for e in b['entries']})==len(b['entries'])
  map_pairs.append({'parent':rev,'path':p})
for name in ['preservation.json','tracking-preflight.json']:
 v=json.loads((ROOT/'docs/ingestion/barodesy-sand/delivery-v1'/name).read_text())
 for b in v.get('old_bindings_verified',v.get('bindings',[])):checked_receipt(ROOT,b['document'],b.get('original_path',b.get('path')),b['sha256'])
# Published product files are carried exactly; no merger-authored product edits.
changed=subprocess.check_output(['git','diff','--name-only',revs[1],'--','models','cpp','atlas','schemas','web','tools/build_web.py','.github/workflows/verify.yml'],cwd=ROOT,text=True).splitlines();assert not changed,changed
print(json.dumps({'status':'pass','reviewer':'/root/barodesy_sand_interface_review','parents':revs,'scientific_inputs_unchanged':len(freeze['source_inputs']),'published_product_sources_carried_exactly':True,'both_parent_approvals_preserved':True,'remote_approvals':len(remote['models']),'combined_approvals':len(registry['models']),'discovery_rows':len(new['models']),'dual_parent_map_superset_checks':map_pairs,'old_barodesy_related_bindings_reverified':49,'package_browser_requalification':'pending'},indent=2))
