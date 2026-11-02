"""Prospectively configured full-state reference comparison; pure Python only."""
import sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.controlled_time import initialize,advance,Settings,context_from_dict
from dataclasses import asdict
DEST=Path(__file__).resolve().parent
MODEL=ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
REF=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026/reference-v1')
IDS=['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100']
SETTINGS=Settings(absolute_scale_fraction=1e-12,relative_tolerance=1e-11,minimum_step_seconds=1e-12,maximum_step_seconds=10.,maximum_depth=40,maximum_trials=100000)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=dict(identity='VIBE candidate revision3 Python full-state trajectory study-v1',model_sha256=sha(MODEL),reference_manifest_sha256=sha(REF/'manifest.json'),cases=IDS,settings=asdict(SETTINGS),time_origin_seconds=11.,acceptance=dict(stress_absolute=1e-2,stress_relative=1e-7,scalar_absolute=1e-9,scalar_relative=1e-7,observable_absolute=1e-8,observable_relative=1e-7),comparison='abs(a-b)<=abs_tol+rel_tol*max(abs(a),abs(b)), all components pass',method='Production adaptive midpoint versus independent Decimal RK4; exact reversal split50s. Context serialization roundtrip checked. No native/Wasm observation.',script_sha256=sha(Path(__file__)))
pp=DEST/'mechanical-study-v1-plan.json'
if '--freeze' in sys.argv:
 assert not pp.exists();pp.write_text(json.dumps(plan,indent=2)+'\n');print('Frozen',sha(pp));sys.exit(0)
assert json.loads(pp.read_text())==plan,'prospective plan/source drift'
m=json.loads(MODEL.read_text());parameters={k:v['default'] for k,v in m['parameters'].items()}
def ratios(a,b,at,rt):return [abs(x-y)/(at+rt*max(abs(x),abs(y))) for x,y in zip(a,b)]
obsmap={'em':'micro_void_ratio','eM':'macro_void_ratio','S':'macro_saturation','Sr':'saturation','OA':'overconsolidation','re':'relative_density'}
for ident in IDS:
 dest=DEST/('mechanical-study-v1-'+ident+'.json')
 assert not dest.exists(),'do not overwrite retained evidence'
 t=time.monotonic();data=json.loads((REF/(ident+'.json')).read_text());r=next(x['result'] for x in data['runs'] if x['result']['precision']==70 and x['result']['partitions']==256)
 initial=list(map(float,r['initial_state']));dry=ident.startswith('dry');controls={'strain':[0.]*6,'suction':1e8 if dry else 1e7,'temperature':294.}
 rates={'strain':[2e-8,-1e-8,3e-8,-2e-8,1e-8,-3e-8],'suction':2000. if ident=='coupled_mechanical_THM_100' else 0.,'temperature':.02 if ident=='coupled_mechanical_THM_100' else 0.}
 ctx=initialize(m,dict(sigma_net=initial[:6],e=initial[6],a_scan=initial[7]),11.,controls,rates,parameters)
 saved=asdict(ctx); assert context_from_dict(m,json.loads(json.dumps(saved)))==ctx
 out=dict(id=ident,plan_sha256=sha(pp),reference_sha256=sha(REF/(ident+'.json')))
 try:
  durations=[50.,50.] if ident=='mechanical_reversal_100' else [float(r['duration_s'])];diags=[]
  for n,duration in enumerate(durations):
   end=dict(ctx.controls);end['strain']=[v+duration*r*(1 if n==0 else -1) for v,r in zip(ctx.controls['strain'],rates['strain'])];end['suction']+=duration*rates['suction'];end['temperature']+=duration*rates['temperature']
   before=asdict(ctx);res=advance(m,ctx,duration,ctx.controls,end,SETTINGS);assert asdict(ctx)==before
   ctx=res.context;diags.append(res.diagnostics)
  assert asdict(initialize(m,dict(sigma_net=initial[:6],e=initial[6],a_scan=initial[7]),11.,controls,rates,parameters))==saved
  got=ctx.state['sigma_net']+[ctx.state['e'],ctx.state['a_scan']];expected=list(map(float,r['final_state']))
  rr=ratios(got[:6],expected[:6],1e-2,1e-7)+ratios(got[6:],expected[6:],1e-9,1e-7)
  oo={k:ratios([res.observables[v]],[float(r['endpoint_observables'][k])],1e-8,1e-7)[0] for k,v in obsmap.items()}
  out.update(status='pass' if max(rr+list(oo.values()))<=1 else 'FAIL',final_state=got,expected=expected,state_tolerance_ratios=rr,observable_tolerance_ratios=oo,diagnostics=diags,context=asdict(ctx))
 except Exception as e:out.update(status='FAIL',exception=type(e).__name__,reason=str(e))
 out['runtime_seconds']=time.monotonic()-t;dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(ident,out['status'],out.get('reason',''),out['runtime_seconds'],flush=True)
