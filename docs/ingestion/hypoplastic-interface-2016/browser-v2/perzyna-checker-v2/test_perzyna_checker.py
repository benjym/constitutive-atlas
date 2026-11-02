"""Prospective checker proof using retained historical bytes and memory-only synthetic mutations."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];REV='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
spec=importlib.util.spec_from_file_location('prospective_perzyna_checker',HERE/'check_perzyna_exports.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def git(path):return subprocess.check_output(['git','show',REV+':'+path],cwd=ROOT)
policy,refs=C.frozen_inputs(Path('/private/tmp/atlas-interface2016-delivery-v1/release-v3')); sourcepins=[];runs={}
for mode in ['relaxation','creep','rate']:
 path='docs/ingestion/perzyna-comsol63/browser-v1/artifacts/'+mode+'.json';raw=git(path);runs[mode]=json.loads(raw);sourcepins.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest()})
runs['reset']=copy.deepcopy(runs['relaxation']);runs['replay']=copy.deepcopy(runs['relaxation']);old=runs['relaxation']['provenance'];failures=[]
def rejected(label,fn):
 try:fn()
 except (ValueError,KeyError,TypeError) as e:failures.append({'case':label,'rejected':True,'reason':str(e)});return
 raise AssertionError('Fault accepted: '+label)
rejected('unchanged_historical_exports_reject_new_revision',lambda:C.assess(old,runs,REV,policy,refs))
historical=C.assess(old,runs,old['release_revision'],policy,refs);assert historical['frozen_component_comparisons']==342
# Only memory copies get the new revision: this is a synthetic transport baseline, never new browser evidence.
synthetic=copy.deepcopy(runs)
for run in synthetic.values():run['provenance']['release_revision']=REV
identity=copy.deepcopy(old);identity['release_revision']=REV
baseline=C.assess(identity,synthetic,REV,policy,refs);assert baseline['frozen_component_comparisons']==342
for mode in ['relaxation','creep','rate']:
 for field,n in [('state',13),('observables',6)]:
  for j in range(n):
   for name,value in [('nan',float('nan')),('positive_infinity',float('inf')),('negative_infinity',-float('inf'))]:
    bad=copy.deepcopy(synthetic);bad[mode]['result']['points'][2][field][j]=value
    rejected(f'{mode}/{field}{j}/{name}',lambda b=bad:C.assess(identity,b,REV,policy,refs))
mutations={
 'short_state':lambda b:b['creep']['result']['points'][2]['state'].pop(),
 'short_stress':lambda b:b['rate']['result']['points'][2]['observables'].pop(),
 'missing_point':lambda b:b['rate']['result']['points'].pop(),
 'wrong_time':lambda b:b['rate']['result']['points'][2].update(time=.6),
 'wrong_segment':lambda b:b['rate']['result']['points'][2].update(segment=-1),
 'bool_state':lambda b:b['creep']['result']['points'][2]['state'].__setitem__(0,True),
 'null_state':lambda b:b['creep']['result']['points'][2]['state'].__setitem__(0,None),
 'string_stress':lambda b:b['creep']['result']['points'][2]['observables'].__setitem__(0,'200000'),
 'nonfinite_diagnostic':lambda b:b['rate']['result']['points'][2].update(temporal_error_norm=float('nan')),
 'wrong_identity':lambda b:b['rate']['provenance'].update(model_sha256='0'*64),
 'wrong_request':lambda b:b['rate']['request']['args'].__setitem__(8,1e-6),
 'alternate_CSV_format':lambda b:b['rate']['request']['args'].__setitem__(1,'2e7,1e7,100000,0.002,2'),
 'wrong_controls':lambda b:b['rate']['controls'].update(duration=1),
 'wrong_solver':lambda b:b['rate']['result']['solver'].update(maximum_step=.1),
 'wrong_state_binding':lambda b:b['rate']['result']['points'][2]['strain'].__setitem__(0,0),
 'stress_beyond_frozen_bound':lambda b:b['rate']['result']['points'][2]['observables'].__setitem__(0,1e9),
 'unresolved_rate_wrong_event':lambda b:b['creep']['result']['points'][2].update(strain_rate=[None]*6),
 'wrong_initial':lambda b:b['rate']['result']['points'][0]['state'].__setitem__(0,.02),
 'changed_reset':lambda b:b['reset']['controls'].update(duration=1),
 'changed_replay':lambda b:b['replay']['result']['points'][2]['state'].__setitem__(0,.02),
}
for label,mutate in mutations.items():
 bad=copy.deepcopy(synthetic);mutate(bad);rejected(label,lambda b=bad:C.assess(identity,b,REV,policy,refs))
# Review B1 witnesses: every prescribed/initial rate component must be bound.
for mode in ['relaxation','rate','creep']:
 indices=range(6) if mode!='creep' else [0]
 for i in indices:
  for j in range(6):
   bad=copy.deepcopy(synthetic);bad[mode]['result']['points'][i]['strain_rate'][j]=1e99
   rejected(f'{mode}/point{i}/prescribed_strain_rate{j}',lambda b=bad:C.assess(identity,b,REV,policy,refs))
for j in range(6):
 bad=copy.deepcopy(synthetic);bad['creep']['result']['points'][1]['strain_rate'][j]=0
 rejected(f'creep/right_unresolved_component{j}',lambda b=bad:C.assess(identity,b,REV,policy,refs))
report={'kind':'prospective-offline-checker-proof-v2','passed':True,'checker_sha256':C.digest(HERE/'check_perzyna_exports.py'),'input_commit':REV,'source_export_pins':sourcepins,'historical_revision':old['release_revision'],'unchanged_historical_exports_rejected_for_new_revision':True,'historical_baseline_components':historical['frozen_component_comparisons'],'memory_only_synthetic_revision_baseline_components':baseline['frozen_component_comparisons'],'rejected_faults':len(failures),'faults':failures,'new_actual_exports_observed':False,'browser_acceptance_claimed':False,'new_browser_module_material_package_compiler_remote_calls':0,'scope':'Historical saved bytes and memory-only synthetic transport/fault checks, not composed browser qualification.'}
(HERE/'perzyna-checker-proof.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['faults','source_export_pins']},indent=2))
