"""Read-only failed-baseline closure; no material/backend execution."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[5];B=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'checkpoint-manifest.json';assert sha(p)=='6cc917c91796faadfab9a9abadc3857ff471ecbf07c3e1d9c9eceac27da8d940'
m=json.loads(p.read_text())
for group in ['files','private_raw_responses']:
 for x in m[group]:assert sha(R/x['path'])==x['sha256'],x['path']
read=lambda n:json.loads((B/n).read_text())
d=read('native-domain-results.json');t=read('native-triaxial-results.json');l=read('native-lifecycle-corrected-results.json');g=read('native-legacy-results.json');s=read('native-supplement-results.json')
assert len(d['requests'])==704 and len(d['checks'])==94 and not d['passed'] and sum(not c['passed'] for c in d['checks'])==2
assert len(t['requests'])==24 and all(x['ok'] and x['within_bounds'] for x in t['requests']) and sum(not x['stress_error_decreases'] for x in t['refinement'])==4 and not t['passed']
assert len(l['checks'])==38 and all(c['passed'] for c in l['checks']) and l['passed']
assert len(g['checks'])==57 and all(c['passed'] for c in g['checks']) and g['passed']
assert len(s['checks'])==3825 and len(s['requests'])==90 and sum(not c['passed'] for c in s['checks'])==1 and not s['passed']
out={'id':'REVIEW-lade-v3-native-failed-checkpoint-closure','checkpoint_sha256':sha(p),'public_bindings_verified':len(m['files']),'private_raw_bindings_verified':len(m['private_raw_responses']),'domain':{'requests':704,'checks':94,'failures':2,'passed':False},'triaxial':{'requests':24,'all_success_and_individual_bounds':True,'failed_plastic_refinement_trends':4,'passed':False},'lifecycle':{'checks':38,'passed':True},'legacy':{'checks':57,'passed':True},'supplement':{'requests':90,'checks':3825,'failures':1,'passed':False},'verdict':'Retained v3 native checkpoint hash closure verified; scientific/numerical admission remains blocked by required failures. Separate v4 design is not completion of these gates.','limits':['No compiled execution','No new native/Wasm/model acceptance','No historical files changed']}
Path(__file__).with_name('v3-checkpoint-results.json').write_text(json.dumps(out,indent=2)+'\n');print('v3failedcheckpoint all967hashes and required failure statuses verified')
