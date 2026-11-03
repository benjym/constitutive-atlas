from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;sys.path.insert(0,str(R))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
v='catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json';r=read(R/v);assert len(r['artifacts'])==281
for f in r['artifacts']:assert h(R/f['path'])==f['sha256']==h(checked_receipt(R,v,f['path'],f['sha256']))
reg=read(R/'catalogue/approved-models.json');approvals=[]
for a in reg['models']:
 review=R/a['review']['path'];validate_review(review,root=R,for_approval=True);assert approval_entry(review,root=R)==a;approvals.append({'model':a['model_id'],'review_sha256':h(review)})
closures=[]
for name in ['controlled-path-refresh-v1/plan-v5.json','maxwell-refresh-v1/plan.json']:
 p=R/'docs/ingestion/vibe-2026'/name;plan=read(p);pins=plan.get('source_closure',plan.get('source_manifest',{}).get('files',{}));pins={**pins,**{f['path']:f['sha256'] for f in plan.get('files',[])}}
 for path,sha in pins.items():assert h(R/path)==sha,path
 assert not {'tools/test_web_package.mjs','tests/test_web_package.mjs'}&set(pins)
 closures.append({'plan':name,'sha256':h(p),'pins_checked':len(pins)})
mentions=[]
for p in (R/'catalogue/agent-reviews').glob('*.json'):
 s=p.read_text()
 if 'tools/test_web_package.mjs' in s or 'tests/test_web_package.mjs' in s:
  for line in s.splitlines():
   if 'tools/test_web_package.mjs' in line or 'tests/test_web_package.mjs' in line:mentions.append({'review':str(p.relative_to(R)),'line':line.strip()})
assert len(mentions)==1 and 'catalogue/source-snapshots/654998eb4379da6405300f4c2a3c8d616eb812eabb6c6d01937a48b7e36c5553/tools/test_web_package.mjs' in mentions[0]['line']
snapshot=R/'catalogue/source-snapshots/654998eb4379da6405300f4c2a3c8d616eb812eabb6c6d01937a48b7e36c5553/tools/test_web_package.mjs';assert h(snapshot)=='654998eb4379da6405300f4c2a3c8d616eb812eabb6c6d01937a48b7e36c5553'
result={'vibe_support_direct_and_resolver':281,'vibe_review_sha256':h(R/v),'approvals':approvals,'closures':closures,'verifier_path_mentions':mentions,'historical_snapshot_exact':True,'no_live_verifier_or_test_scientific_pin':True,'source_archive_map_sha256':h(R/'catalogue/agent-reviews/source-archive-map.json'),'material_calls':0};out=O/('preservation-postfreeze.json' if '--postfreeze' in sys.argv else 'preservation-baseline.json');out.write_text(json.dumps(result,indent=2)+'\n');print(out.name,h(out),'approvals',len(approvals),'closures',closures)
