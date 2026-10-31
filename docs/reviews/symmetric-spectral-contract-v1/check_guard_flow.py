"""Source-only candidate qualifier examples, not shape/dimension/engine tests."""
import json
from guard_flow import dependencies,require_numeric_sink

def run():
    aliases={}
    aliases['a_guard']=dependencies('principal_max_value(A)',aliases)
    aliases['gamma_guard']=dependencies('(a_guard-trace(A))/E',aliases)
    aliases['safe_numeric']=dependencies('select(gamma_guard>0,trace(A),principal_min(A))',aliases)
    good=['select(principal_mid_value(A)>0,principal_upper_sum(A),principal_lower_sum(A))','trace(A)','principal_max(A)','projector_min(A)',
          'select(principal_min_value(A)>0,trace(A),0)',
          'select(gamma_guard>0,principal_max(A),trace(A))',
          'select(gamma_guard>0,select(a_guard>1,principal_min(A),0),trace(A))',
          'safe_numeric','select(principal_max_value(A)>principal_min_value(A),A,0*A)']
    bad=['principal_mid_value(A)','principal_upper_sum(sym(principal_mid_value(A),0,0,0,0,0))','principal_max_value(A)','0*principal_max_value(A)',
         'a_guard-a_guard','gamma_guard','trace(A)*a_guard',
         'select(a_guard>0,gamma_guard,trace(A))',
         'select(a_guard>0,trace(A),principal_min_value(A))',
         'sym(a_guard,0,0,0,0,0)','trace(sym(0,0,0,a_guard,0,0))',
         'principal_max(sym(a_guard,0,0,0,0,0))',
         'projector_min(sym(a_guard,0,0,0,0,0))',
         'select(a_guard>0,select(gamma_guard>0,0,a_guard),0)',
         '0*select(a_guard>0,a_guard,0)']
    for expr in good:require_numeric_sink(expr,aliases)
    for expr in bad:
        try:require_numeric_sink(expr,aliases)
        except ValueError as e:assert 'value-only dependency reaches numeric output' in str(e)
        else:raise AssertionError(expr)
    assert dependencies('principal_max_value(A)>0',aliases)==frozenset()
    assert aliases['a_guard']==frozenset({'principal_max_value'})
    assert aliases['gamma_guard']==aliases['a_guard'] and not aliases['safe_numeric']
    return {'accepted_numeric_sinks':len(good),'rejected_numeric_leaks':len(bad),'alias_and_predicate_assertions':4,'compiled_calls':0,'production_DSL_modified':False,'complete_expression_validation':False}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
