"""Independently inspect the frozen collector/plan/reference binding, without backend calls."""
from pathlib import Path
import json,hashlib,ast
from decimal import Decimal as D
R=Path(__file__).resolve().parents[4];W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');P='docs/ingestion/vibe-2026/';Q=W/P/'numerical-qualification-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=Q/'source-manifest-v2.json';assert sha(manifest)=='bd73a00ace2f559f4396a4c8866c6d46bce43a4e275b7455255a9b90c7eef22b';v=json.loads(manifest.read_text())
 for row in v['files']:
  p=W/row['path'];assert sha(p)==row['sha256'];assert p.stat().st_size==row['bytes']
 prior=json.loads((Q/'source-manifest-v1.json').read_text());recovery=[]
 for row in prior['files']:
  candidates=[W/row['path'],Q/'preimages/source-freeze-v1'/row['path']];matches=[str(p) for p in candidates if p.is_file() and sha(p)==row['sha256']];assert matches;recovery.append(dict(original=row['path'],retained=matches[0],sha256=row['sha256']))
 planpath=Q/'plan-v2.json';assert sha(planpath)=='b70950d1981602d9bc053f708214fde7c93efda1dde97420b10295c015d890da';plan=json.loads(planpath.read_text())
 for row in plan['source_files']:
  p=Path(row['path']);p=p if p.is_absolute() else W/p;assert sha(p)==row['sha256']
 assert plan['bounds']==dict(point_stress_rate=[1e-8,1e-7],point_scalar_rate=[1e-12,1e-7],trajectory_stress=[.01,1e-7],trajectory_scalar=[1e-9,1e-7],observable=[1e-8,1e-7]);assert plan['refinement_max_steps']==[10.,5.,2.5]
 points=json.loads((R/P/'reference-v1/point-results.json').read_text())['cases'];assert len(points)==len(plan['points'])==32
 def obs(source,T,params):
  aliases={'micro_void_ratio':'em','macro_void_ratio':'eM','macro_saturation':'S','saturation':'Sr','relative_density':'re','overconsolidation':'OA'}
  expected={n:source[k] for n,k in aliases.items()};expected['viscosity_factor']=str(D('.004')+D(str(params['IvT']))*(D(str(T))-D(str(params['Tr'])))**3*D('1e-8'));return expected
 for reference,case in zip(points,plan['points']):
  r=reference['reference'];assert reference['id']==case['id'];assert r['rate']==case['expected_rate'];assert obs(r['observables'],r['temperature_K'],case['context']['parameters'])==case['expected_observables'];assert [*case['context']['state']['sigma_net'],case['context']['state']['e'],case['context']['state']['a_scan']]==list(map(float,r['initial_state']))
 examples=json.loads((W/P/'public-examples-v1/examples.json').read_text());assert len(plan['histories'])==8
 for e,c in zip(examples,plan['histories']):
  assert e['id']==c['id'] and e['request']==c['request'];rp=Path(c['reference_path']);assert sha(rp)==c['reference_sha256'];r=next(x['result'] for x in json.loads(rp.read_text())['runs'] if x['status']=='pass' and x['result']['precision']==70 and x['result']['partitions']==256);assert c['expected_state']==r['final_state'];assert c['expected_observables']==obs(r['endpoint_observables'],r['endpoint_temperature_K'],c['request']['context']['parameters'])
  previous=e['request']['context']['controls'];mechanical=e['id'] in ['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100'];elapsed=0
  for i,s in enumerate(e['request']['segments']):
   mechanical_rate=[(2e-8,-1e-8,3e-8,-2e-8,1e-8,-3e-8)[j]*(-1 if e['id']=='mechanical_reversal_100' and i==1 else 1) if mechanical else 0 for j in range(6)];actual=[(b-a)/s['duration'] for a,b in zip(previous['strain'],s['controls_end']['strain'])];assert all(abs(a-b)<1e-22 for a,b in zip(actual,mechanical_rate));sd=(s['controls_end']['suction']-previous['suction'])/s['duration'];td=(s['controls_end']['temperature']-previous['temperature'])/s['duration'];assert sd==(2000*(-1 if i==1 else 1) if e['id']=='hydraulic_reversal_100' else 2000 if e['id'] in ['mixed_ramp_100','coupled_mechanical_THM_100'] else 0);assert td==(.02 if e['id'] in ['mixed_ramp_100','coupled_mechanical_THM_100'] else 0);elapsed+=s['duration'];previous=s['controls_end']
  if len(e['request']['segments'])==2:assert e['request']['segments'][0]['duration']==50
 assert len(plan['invalid_cases'])==7;assert {x['id'] for x in plan['invalid_cases']}=={'zero_suction','negative_suction','low_void_ratio','scan_low','scan_high','nonpositive_micro_pressure','negative_viscosity'}
 for p in [W/'tools/qualify_vibe2026.py',Q/'prepare_plan.py',Q/'pure_source_checks.py']:ast.parse(p.read_text())
 print(json.dumps(dict(source_manifest=str(manifest),sha256=sha(manifest),verified_source_files=len(v['files']),prior_recovery=recovery,verified_reference_files=len(plan['source_files']),rate_cases=32,full_histories=8,protocols_match_source=True,invalid_cases=7,original_bounds_unchanged=True,compiled_execution=False),indent=2))
if __name__=='__main__':main()
