"""Prepare complete imposed-field requests; Python initialization/domain checks run; no compiled interface is called."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.controlled_time import identity,validate_request
R=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026')
M=ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json';m=json.loads(M.read_text());dest=Path(__file__).resolve().parent
settings=dict(absolute_scale_fraction=1e-12,relative_tolerance=1e-11,minimum_step_seconds=1e-12,maximum_step_seconds=10.,maximum_depth=40,maximum_trials=100000)
names={
'near_hold_1000':('Relaxation · 1000 seconds','Hold every imposed field fixed near the asymptotic state boundary. Viscosity relaxes net stress while void ratio and hydraulic memory remain fixed.'),
'near_hold_3600':('Relaxation · 1 hour','Continue the same illustrative hold for 3600 seconds to see accumulated rate-dependent relaxation.'),
'dry_hold_1000':('Dry state · negligible relaxation','A much more overconsolidated dry starting state has essentially zero relaxation over this interval. Compare it with the near-boundary examples.'),
'mixed_ramp_100':('Heating and drying · 100 seconds','Hold mechanical strain fixed, increase suction by 0.2 MPa and temperature by 2 K. Both thermal and hydraulic terms contribute; this uses the published explicit AppendixA variant.'),
'hydraulic_reversal_100':('Drying then wetting','Increase suction for 50 seconds and return it over 50 seconds. The evolving scanning memory retains hydraulic history.'),
'mixed_mechanical_100':('Six-component mechanical loading','Apply all six constant Mandel strain-rate components for 100 seconds at fixed suction and temperature. These small imposed strains exercise normal and shear response.'),
'mechanical_reversal_100':('Mechanical loading then reversal','Apply the six-component mechanical rate for 50 seconds, then reverse its sign for 50 seconds. Returning strain to its starting value can leave residual stress history.'),
'coupled_mechanical_THM_100':('Combined mechanical, thermal and hydraulic loading','Apply the same small six-component mechanical rate while heating by 2 K and increasing suction by 0.2 MPa over 100 seconds.')}
examples=[];bindings=[]
for ident,(title,help) in names.items():
 ref=(R/('reference-v2' if ident in list(names)[5:] else 'reference-v1')/(ident+'.json'));data=json.loads(ref.read_text());r=next(x['result'] for x in data['runs'] if x['result']['precision']==70 and x['result']['partitions']==256)
 z=list(map(float,r['initial_state']));dry=ident=='dry_hold_1000';suction=1e8 if dry else 1e7
 controls=dict(strain=[0.]*6,suction=suction,temperature=294.)
 context=dict(profile='controlled-time-ode-v1',model_sha256=identity(m),state=dict(sigma_net=z[:6],e=z[6],a_scan=z[7]),time=11.,controls=controls,control_rates=dict(strain=[0.]*6,suction=0.,temperature=0.),parameters={n:p['default'] for n,p in m['parameters'].items()})
 mechanical=ident in list(names)[5:];coupled=ident in ('mixed_ramp_100','coupled_mechanical_THM_100');reversal=ident in ('hydraulic_reversal_100','mechanical_reversal_100')
 vector=[2e-8,-1e-8,3e-8,-2e-8,1e-8,-3e-8] if mechanical else [0.]*6;durations=[50.,50.] if reversal else [float(r['duration_s'])];segments=[]
 for i,duration in enumerate(durations):
  if i==0:end=dict(strain=[duration*v for v in vector],suction=suction+(duration*2000. if coupled or ident=='hydraulic_reversal_100' else 0.),temperature=294.+(duration*.02 if coupled else 0.))
  else:end=dict(strain=[0.]*6,suction=suction,temperature=294.)
  segments.append(dict(id=ident+'_'+str(i+1),duration=duration,samples=10 if reversal else 40 if ident=='near_hold_3600' else 20,controls_end=end))
 request=dict(profile='controlled-time-ode-v1',model=m['id'],context=context,settings=settings,segments=segments);validate_request(m,request)
 examples.append(dict(id=ident,title=title,help=help,request=request));bindings.append(dict(id=ident,reference_path=str(ref.relative_to(R.parents[2])),reference_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),reference_precision=70,reference_partitions=256))
(dest/'examples.json').write_text(json.dumps(examples,indent=2,allow_nan=False)+'\n');(dest/'reference-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(len(examples),'complete requests validated with Python initial-domain checks; no compiled calls')
