"""Compare declarative candidate with independently frozen Decimal references."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from atlas.model import validate
from atlas.controlled_time import evaluate_stage
MODEL=ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
REF=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026/reference-v1/point-results.json')
m=json.loads(MODEL.read_text());validate(m)
rows=[]
obsmap={'em':'micro_void_ratio','eM':'macro_void_ratio','S':'macro_saturation','Sr':'saturation','OA':'overconsolidation','re':'relative_density'}
def checks(a,b,absolute,relative):
 return [abs(x-y)/(absolute+relative*max(abs(x),abs(y))) for x,y in zip(a,b)]
for c in json.loads(REF.read_text())['cases']:
 r=c['reference'];p={k:v['default'] for k,v in m['parameters'].items()};p.update({k:float(v) for k,v in r['parameter_overrides'].items()})
 s=list(map(float,r['initial_state']));state={'sigma_net':s[:6],'e':s[6],'a_scan':s[7]}
 controls={'strain':[0.]*6,'suction':float(r['suction_Pa']),'temperature':float(r['temperature_K'])}
 rates={'strain':list(map(float,r['mechanical_rate_per_s'])),'suction':float(r['suction_rate_Pa_per_s']),'temperature':float(r['temperature_rate_K_per_s'])}
 try:
  rr,oo,_=evaluate_stage(m,state,p,0.,controls,rates)
  got=rr['sigma_net']+[rr['e'],rr['a_scan']];expected=list(map(float,r['rate']))
  ratios=checks(got[:6],expected[:6],1e-8,1e-7)+checks(got[6:],expected[6:],1e-12,1e-7)
  obsratios={k:checks([oo[v]],[float(r['observables'][k])],1e-8,1e-7)[0] for k,v in obsmap.items()}
  rows.append(dict(id=c['id'],status='pass' if max(ratios+list(obsratios.values()))<=1 else 'FAIL',rate=got,expected_rate=expected,rate_tolerance_ratios=ratios,observable_tolerance_ratios=obsratios))
 except Exception as e:rows.append(dict(id=c['id'],status='REFUSED',exception=type(e).__name__,reason=str(e)))
out=dict(model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),reference_sha256=hashlib.sha256(REF.read_bytes()).hexdigest(),cases=rows)
dest=Path(sys.argv[1]);dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print({s:sum(c['status']==s for c in rows) for s in ('pass','FAIL','REFUSED')});print([(c['id'],c.get('reason'),max(c.get('rate_tolerance_ratios',[0]))) for c in rows if c['status']!='pass'])
