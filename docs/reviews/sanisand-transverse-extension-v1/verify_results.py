"""Saved-only verification of terminal study and independent discrete findings."""
import importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(P))
from covariance import load,sha

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify():
 for name,expected in load(P/'results-manifest.json')['files'].items():assert sha(P/name)==expected,name
 module('checkpoint_verifier',P/'verify.py').verify()
 data=load(P/'continuous-v1/study.json.gz');process=load(P/'continuous-v1/process.json')
 assert process['returncode']==2 and len(process['stdout'].splitlines())==26
 assert len(data['variational'])==18 and len(data['nonlinear'])==8
 assert sum(r['status']=='completed' for r in data['variational'])==15
 assert all(r['status']=='completed' for r in data['nonlinear'])
 assert all(r.get('exception')=="ValueError('diagnostic minimum step')" for r in data['variational'] if r['status']=='failed')
 original=module('original_study_audit',P/'assess_study.py')
 try:original.audit(data,load(P/'policy.json'))
 except ValueError as exc:assert str(exc)=='study run failed'
 else:raise AssertionError('original failed study must not pass')
 assert load(P/'continuous-v1/original-audit-process.json')['returncode']==1
 summary=module('continuous_summary',P/'continuous-v1/summarize.py').summarize(data)
 assert summary==load(P/'continuous-v1/summary.json') and summary['overall_original_audit_pass'] is False
 sys.path.insert(0,str(P/'discrete-v1'))
 import audit,precision
 actual=audit.audit();assert actual==load(P/'discrete-v1/assessment.json')
 assert precision.replay()==load(P/'discrete-v1/precision-assessment.json')
 assert load(P/'discrete-v1/tests-process.json')['returncode']==0
 return {'saved_results_valid':True,'independent_full_study_pass':False,'completed_variational_runs':15,'expected_variational_runs':18,'completed_nonlinear_runs':8,'independent_discrete_derivative_components':135,'arithmetic_gain_replay_pass':True,'original_native_qualification_pass':False,'process_status':'terminal','scientific_signature':None}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
