"""Saved-only audit; never invokes artifacts or subprocesses."""
from pathlib import Path
import hashlib,json,math,importlib.util,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());pins={}
def pin(p):pins[str(p.relative_to(ROOT))]=h(p)
freeze=read(P/'freeze-v1.json')
for n,s in freeze['files'].items():assert h(P/n)==s,n
build=read(P/'native-build-receipt.json');pin(P/'native-build-receipt.json')
for n,s in build['files'].items():assert h(ROOT/n)==s,n
source=P/'proposed-native-source';mirror=ROOT/'.local/lade-outer-predictor-v1/native-source';count=0
for q in source.rglob('*'):
 if q.is_file():assert q.read_bytes()==(mirror/q.relative_to(source)).read_bytes();count+=1
flags=P/'build-configuration'
prod=(flags/'atlas_lade_domain_candidate-flags.make').read_text();cold=(flags/'atlas_lade_cold_cache_candidate-flags.make').read_text();budget=(flags/'atlas_outer_budget_regression-flags.make').read_text()
assert 'ATLAS_TEST_OUTER_BUDGET' not in prod+cold and 'ATLAS_DISABLE_OUTER_REUSE' not in prod
assert '-DATLAS_TEST_OUTER_BUDGET=1' in budget and '-DATLAS_DISABLE_OUTER_REUSE=1' in cold
summ={}
for name,n in [('predictor',214),('outer',157),('hierarchical',33),('tail',10375),('seed',49),('metric',16),('budget',1)]:
 q=P/(name+'-results.json');d=read(q);assert d['passed'] is True and d['checks']==n and d.get('failures',0)==0
 pin(q);summ[name]=d
assert summ['predictor']['seeded_trials']==15 and summ['predictor']['cold_integrations']==112 and summ['predictor']['warm_integrations']==70
spec=importlib.util.spec_from_file_location('saved_fidelity',P/'fidelity.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
f=read(P/'fidelity-results.json');assert f['passed'] and len(f['records'])==6;pin(P/'fidelity-results.json');paircounts=[]
policy=read(P/'FIDELITY_POLICY.json')
for i in range(3):
 pair=f['records'][2*i:2*i+2];responses=[]
 for k,row in enumerate(pair):
  assert row['returncode']==0 and row['timeout'] is False and row['elapsed_seconds']<120
  cmd=policy['cases'][i]['command'].copy();cmd[0]=policy['baseline_exe'] if k==0 else policy['candidate_exe'];assert row['command']==cmd
  assert h(Path(cmd[0]))==row['exe_sha256']
  for key in ['stdout','stderr']:
   q=ROOT/row[key]['path'];assert h(q)==row[key]['sha256'];pin(q)
  b=(ROOT/row['stdout']['path']).read_bytes();responses.append(mod.parse_response(b));r=json.loads(b);assert r['ok'] is True
  assert len(r['points'])==int(cmd[cmd.index('--steps')+1])+1
  for point in r['points']:
   assert len(point['state'])==8 and len(point['strain'])==6
   assert all(isinstance(x,(int,float)) and math.isfinite(x) for x in point['state']+point['strain']+[point['control']])
 assert mod.same_response(*responses)
 paircounts.append(len(responses[0]['points']))
source_errors=[]
refs=read(P/'triaxial-reference-results.json')['cases'];bounds=read(P/'triaxial-policy.json')['native_final_reference_bounds']
for i in (1,3):
 row=f['records'][i];rr=read(ROOT/row['stdout']['path']);pt=rr['points'][-1];target=float(row['command'][row['command'].index('--target')+1])
 ref=next(x['reference'] for x in refs if x['set']=='dense' and x['reference']['axial_strain']==target)
 errors={'relative_axial_stress':abs(pt['state'][0]-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(pt['strain'][1]-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(pt['state'][7]-ref['wp'])/max(1,abs(ref['wp']))}
 assert all(errors[k]<=v for k,v in bounds.items());source_errors.append({'target':target,'errors':errors})
r={'passed':True,'independent_reference_spotchecks':source_errors,'build_pins' :len(build['files']),'source_mirror_files':count,'helper_results':summ,'strict_fullresponse_pairs':3,'points_per_response':paircounts,'limitation':'Saved helper/fidelity evidence only; no hardcase, full source campaign or backend qualification inferred','pins':pins}
(P/'independent-review/saved-helper-check-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['pins','helper_results']}))
