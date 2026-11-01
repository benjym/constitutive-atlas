"""Read-only interpreter/type probes of existing generic minimum operations.

Synthetic in-memory elasticity copies are used only as type-validation carriers;
no model files are changed/generated and no candidate/compiled artifact is run.
"""
from pathlib import Path
import json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[6]))
from atlas.dsl import evaluate, parse, Sym, ValidationError
from atlas.model import load, migrate_formulation, validate

stress=[100000,60000,60000,0,0,0]
records=[]
for name in ['principal_min','principal_min_value','principal_max','principal_min_repeated']:
    expr=name+'(sigma)'
    try:
        result=evaluate(parse(expr),{'sigma':Sym(stress)})
        records.append({'expression':expr,'status':'returned','value':result})
    except Exception as exc:
        records.append({'expression':expr,'status':'rejected','exception':type(exc).__name__,'message':str(exc)})
# Validate both complete synthetic definitions, with all unchanged structural
# requirements supplied by an in-memory migration of an existing baseline.
for expr in ['sigma - sigma_n - principal_min(sigma)*I',
             'sigma - sigma_n - principal_min_value(sigma)*I',
             'sigma - sigma_n - principal_min_value(sigma_n)*I']:
    model=migrate_formulation(load('models/linear-elastic.json'))
    model['equations']['sigma']=expr
    try:
        validate(model)
        records.append({'residual_probe':expr,'status':'type-validation-passed'})
    except Exception as exc:
        records.append({'residual_probe':expr,'status':'rejected','exception':type(exc).__name__,'message':str(exc)})
assert records[0]['status']=='rejected' and records[0]['message']=='selected_eigenvalue_unresolved'
assert records[1]['value']==60000
assert records[2]['value']==100000
assert records[3]['value'] is True
assert records[4]['status']=='type-validation-passed'
assert all(r['status']=='rejected' for r in records[5:])
# Exact-valued lazy composition with a declared cluster-average generalized
# derivative policy; this probe checks only values and type acceptance.
repeat_safe = ('select(principal_min_repeated(sigma), '
               'select(principal_max_repeated(sigma), trace(sigma)/3, '
               '(trace(sigma)-principal_max(sigma))/2), principal_min(sigma))')
repeat_safe_probes=[]
for label,values,expected in [
    ('triaxial_compression',[100000,60000,60000,0,0,0],60000),
    ('hydrostatic',[60000,60000,60000,0,0,0],60000),
    ('distinct',[100000,70000,60000,0,0,0],60000),
    ('triaxial_extension',[100000,100000,60000,0,0,0],60000)]:
    value=evaluate(parse(repeat_safe),{'sigma':Sym(values)})
    assert value==expected
    repeat_safe_probes.append({'case':label,'input':values,'value':value})
model=migrate_formulation(load('models/linear-elastic.json'))
model['equations']['sigma']='sigma - sigma_n - ('+repeat_safe+')*I'
validate(model)
# At a repeated minimum S=diag(100,60,60), H=diag(0,1,-1),
# lambda_min(S+tH)=60-abs(t). Cluster-average derivative is0;
# actual one-sided directional derivative is-1. The average is a Clarke
# generalized choice, not the unique classical/directional derivative.
assert min(100,61,59)-60==-1
assert (1 + -1)/2==0
result={'id':'lade-original-v2-spectral-contract-probe','input_mandel_Pa':stress,
        'results':records,'conclusion':'Minimum primitive exists, but ordinary differentiable minimum rejects the repeated selected minimum in triaxial compression. Value-only minimum handles the value but cannot supply a numeric residual, including from committed state. No missing scalar spectral primitive is claimed.',
        'limitations':['Interpreter/type validation only','No generated or compiled code','Synthetic equations are type carriers, not a Lade candidate','Proposed cluster-average generalized branch is type/value-probed only; derivative/backend/path qualification remains pending'],'repeat_safe_proposal':{'expression':repeat_safe,'value_checks':repeat_safe_probes,'synthetic_residual_type_validation':'passed','generalized_policy':'(I-Pmax)/2 for a repeated lower pair; I/3 for hydrostatic triple','counterexample':{'S_diagonal':[100,60,60],'H_diagonal':[0,1,-1],'one_sided_min_directional_derivative':-1,'cluster_average_selected_derivative':0},'interpretation':'Exact value expression and a permissible Clarke generalized derivative policy. Does not assert a unique classical derivative, actual directional derivative or guaranteed Newton convergence.'}}
if __name__=='__main__':
    Path(__file__).with_name('spectral-contract-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
