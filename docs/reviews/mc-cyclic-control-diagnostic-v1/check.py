"""Saved-evidence diagnostic checks; no original/candidate execution."""
from pathlib import Path
import json,sys
from decimal import Decimal as D
P=Path(__file__).parent;R=Path(sys.argv[1]);a=json.loads((P/'reconstruction.json').read_bytes());b=json.loads((R/'catalogue/investigations/mc-preview-envelope-v2/parity-diagnostic.json').read_bytes());checks=0
assert a['failure_count']==b['failed_scalars']==15;checks+=1
for x,y in zip(a['parity_failures'],b['failures']):
 for k in('id','point','field','component','difference','budget','fraction'):assert x[k]==y[k];checks+=1
for r in a['backends']:
 assert len(r['points'])==65;checks+=1
 for p in r['points'][1:]:assert p['outer_stopping_fraction']<1;checks+=1
 assert a['summaries'][r['backend']]['all_outer_residuals_within_source_threshold'];checks+=1
u=json.loads((P/'source-update-check.json').read_bytes())
for r in u['backends']:
 assert D(r['maximum_source_update_error_norm'])<D('1e-9');checks+=1
 assert len(r['points'])==64;checks+=1
result={'identity':'mc-cyclic-control-saved-evidence-selfcheck-v1','passed':True,'checks':checks,'new_candidate_calls':0,'new_compiled_calls':0,'bounds_changed':False};print(json.dumps(result,indent=2))
