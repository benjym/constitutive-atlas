"""Freeze source references and requests without evaluating any constitutive law."""
import argparse,hashlib,json
from pathlib import Path
from decimal import Decimal as D

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--examples',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 m=json.loads(a.model.read_text());examples=json.loads(a.examples.read_text());files=[a.model,a.examples];base={n:v['default'] for n,v in m['parameters'].items()};canonical=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 def obs(r,T,params):
  mapping={'micro_void_ratio':'em','macro_void_ratio':'eM','macro_saturation':'S','saturation':'Sr','relative_density':'re','overconsolidation':'OA'}
  out={n:r[key] for n,key in mapping.items()}
  # Independent scalar source Appendix A35 check, not evaluation of the candidate DSL.
  out['viscosity_factor']=str(D('.004')+D(str(params['IvT']))*(D(str(T))-D(str(params['Tr'])))**3*D('1e-8'))
  return out
 points_path=a.reference_root/'reference-v1/point-results.json';files.append(points_path);points=[]
 for c in json.loads(points_path.read_text())['cases']:
  assert c['status']=='pass';r=c['reference'];z=list(map(float,r['initial_state']));params={**base,**{n:float(v) for n,v in r['parameter_overrides'].items()}}
  context=dict(profile='controlled-time-ode-v1',model_sha256=canonical,state=dict(sigma_net=z[:6],e=z[6],a_scan=z[7]),time=11.,controls=dict(strain=[0.]*6,suction=float(r['suction_Pa']),temperature=float(r['temperature_K'])),control_rates=dict(strain=list(map(float,r['mechanical_rate_per_s'])),suction=float(r['suction_rate_Pa_per_s']),temperature=float(r['temperature_rate_K_per_s'])),parameters=params)
  points.append(dict(id=c['id'],context=context,expected_rate=r['rate'],expected_observables=obs(r['observables'],r['temperature_K'],params)))
 histories=[]
 for e in examples:
  assert e['request']['context']['model_sha256']==canonical
  rp=a.reference_root/('reference-v2' if e['id'] in ('mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100') else 'reference-v1')/(e['id']+'.json');files.append(rp);rr=json.loads(rp.read_text());r=next(x['result'] for x in rr['runs'] if x['status']=='pass' and x['result']['precision']==70 and x['result']['partitions']==256)
  assert list(map(float,r['initial_state']))==[*e['request']['context']['state']['sigma_net'],e['request']['context']['state']['e'],e['request']['context']['state']['a_scan']]
  assert sum(s['duration'] for s in e['request']['segments'])==float(r['duration_s'])
  histories.append(dict(id=e['id'],request=e['request'],expected_state=r['final_state'],expected_observables=obs(r['endpoint_observables'],r['endpoint_temperature_K'],e['request']['context']['parameters']),reference_path=str(rp),reference_sha256=digest(rp)))
 assert len(points)==32 and len(histories)==8
 plan=dict(identity='vibe2026-backend-qualification-v1',model_file_sha256=digest(a.model),model_sha256=canonical,model_id=m['id'],source_files=[dict(path=str(p),sha256=digest(p)) for p in files],settings=examples[0]['request']['settings'],bounds=dict(point_stress_rate=[1e-8,1e-7],point_scalar_rate=[1e-12,1e-7],trajectory_stress=[.01,1e-7],trajectory_scalar=[1e-9,1e-7],observable=[1e-8,1e-7]),points=points,histories=histories,refinement_max_steps=[10.,5.,2.5],raw_domain_suctions=[0.,-1.])
 assert all(e['request']['settings']==plan['settings'] for e in histories)
 with a.output.open('x') as f:json.dump(plan,f,indent=2,allow_nan=False);f.write('\n')
 print(len(points),'rate points;',len(histories),'public histories; no equations or compiled calls')
if __name__=='__main__':main()
