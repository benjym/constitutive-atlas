"""Re-audit original tagged-v3 opaque bundles; no compiled execution/rebuild."""
import json,subprocess
from unittest.mock import patch
from atlas.model import ROOT
from tools.research_rate_parity_v3 import assess
rows=[]
with patch.object(subprocess,'Popen',side_effect=AssertionError('compiled/external execution forbidden')):
 for name,expected in [('clay2005-rates-v3','failed'),('clay2005-boundary-parity-v1','passed')]:
  h=ROOT/'catalogue/investigations'/name
  bundles=lambda role:tuple(h/(role+s)for s in ('-build.json','-observation.json','-observation.transport.json'))
  result=assess(h/'protocol.json',bundles('native'),bundles('wasm'))
  assert result==json.loads((h/'comparison.json').read_text())
  assert result['outcome']==expected
  rows.append({'study':name,'outcome':expected,'calls_per_backend':len(result['native']['cases']),'max_parity_budget_fraction':result['parity']['maximum_parity_budget_fraction']})
print(json.dumps({'studies':rows,'compiled_execution':False,'artifact_reopen':False,'scientific_admission':False},sort_keys=True))
