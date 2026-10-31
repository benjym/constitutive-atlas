"""Capture previously failed interpreted-v1 hold parents; not independent reference generation."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,math,hashlib
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/mc-declarative-design-v1';sys.path.insert(0,str(P/'frozen'))
from atlas.model import load,evaluation_environment
m=load(P/'model.json');assert hashlib.sha256((P/'model.json').read_bytes()).hexdigest()=='89aa849126ec775a808e819cb21794d22434a1184b8b7cbe87c0062e20441f38'
cert=json.loads((P/'frozen/docs/ingestion/mohr-coulomb/results.json').read_text());params={'E':2.25,'nu':.125,'c':5.,'phi':math.asin(.6),'psi':math.asin(1/3),'p_ref':1.}
mandel=lambda a:[float(a[0][0]),float(a[1][1]),float(a[2][2]),math.sqrt(2)*float(a[0][1]),math.sqrt(2)*float(a[1][2]),math.sqrt(2)*float(a[0][2])]
rows=[]
for c in cert['certificates']:
 if c['case']not in ('left_to_apex_boundary','right_to_apex_boundary'):continue
 t=list(map(F,c['source_tension_principal_trial']));de=[-((x-sum(t)/3)/2+sum(t)/9)for x in t]
 modes={'diagonal':[float(x)for x in de]+[0.]*3,'rotated':mandel([[F(x)for x in row]for row in c['compression_cartesian_increment']])}
 for form,loading in modes.items():
  env=evaluation_environment(m,{'sigma':[0.]*6},{'sigma':[0.]*6},loading,params);parent=[-x for x in env['returned_source'].v]
  try:evaluation_environment(m,{'sigma':parent},{'sigma':parent},[0.]*6,params)
  except ValueError as e:assert str(e)=='selected_eigenvalue_unresolved';failure=str(e)
  else:raise AssertionError('failed-v1 hold unexpectedly passed')
  rows.append({'id':c['case']+'/'+form,'parent':[x.hex()for x in parent],'parameters':{k:v.hex()for k,v in params.items()},'failure':failure})
print(json.dumps({'identity':'mc-retained-v1-failed-hold-literal-capture','model_sha256':hashlib.sha256((P/'model.json').read_bytes()).hexdigest(),'candidate_interpreter_capture_calls':8,'compiled_observations':0,'cases':rows},indent=2))
