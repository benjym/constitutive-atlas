"""Read retained JSON, run Python assessment and corruption probes only."""
from pathlib import Path
import copy,hashlib,json
from atlas.model import load
from tools import gis2024_integration_study as g
from tools import gis2024_path_reference as reference
# Repository-path adaptation of the independent review runner.
folder=Path(__file__).resolve().parents[1]
p=folder/'native.json';r=json.loads(p.read_text());model=load(g.MODEL_PATH);ref=reference.study()
assessment=g.assess(r['records'],model,ref)
g.assess_probes(r['failure_probes'],r['records'],model)
receipt=json.loads((folder.parent/'gis2024-path-reference-v1/reference.json').read_text())
from tools.verify_gis2024_paths import verify
verify(r,reference_receipt=receipt)
probes={}
for kind in ('failed_settings','failed_diagnostics','intermediate_Omega_domain','intermediate_h_domain'):
 records=copy.deepcopy(r['records']);failures=copy.deepcopy(r['failure_probes'])
 if kind=='failed_settings':failures[0]['response']['integration_settings']={}
 if kind=='failed_diagnostics':failures[0]['response']['diagnostics']['iterations']=float('nan');failures[0]['response']['diagnostics']['rejected']=-3;failures[0]['response']['diagnostics']['increment_fractions']=[99.]
 if kind.startswith('intermediate'):
  group=next(v for v in records if v['partitions']==7)
  z=group['calls'][0]['response']['state']
  if kind=='intermediate_Omega_domain':z[13]=2.
  else:z[7:13]=[.01,0.,0.,0.,0.,0.]
  group['calls'][1]['request']['initial']=z[:];group['calls'][1]['response']['initial']=z[:]
 try:
  if kind.startswith('intermediate'):g.assess(records,model,ref)
  else:g.assess_probes(failures,records,model)
  probes[kind]='accepted'
 except ValueError as exc:probes[kind]={'rejected':type(exc).__name__,'error':str(exc)}
assert all(v!='accepted' for v in probes.values()), 'verifier accepted corrupted evidence'
result={'trajectories':len(r['records']),'calls':sum(len(x['calls'])for x in r['records']),'fresh_independent_assessment_passed':True,'corruption_probes':probes,'pins':{str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in (p,Path(g.__file__),Path(reference.__file__),Path(__file__))}}
print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
