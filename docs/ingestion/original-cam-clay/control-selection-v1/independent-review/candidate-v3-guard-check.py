"""Portable representability guard/conditioning witnesses; no compiled calls."""
from pathlib import Path
import hashlib,json,math,sys
P=Path(__file__).resolve().parent;B=P.parent
sys.path.insert(0,str(B.parents[3]))
from atlas.model import load,defaults,evaluation_environment,interpret

def main():
    a,b=[load(B/f'candidate-v03-{v}.json') for v in ('v2','v3')]
    p=defaults(b);pressure=50000.;pc=100000.
    v=p['Gamma']+(p['lambda_c']-p['kappa'])*(1-math.log(pc/p['pref']))-p['kappa']*math.log(pressure/p['pref'])
    old={'sigma':[pressure]*3+[0.]*3,'v':v}
    underflow=[-.3333]*3+[0.]*3
    e=evaluation_environment(a,old,old,underflow,p)
    assert e['p_end']==0
    try:evaluation_environment(b,old,old,underflow,p)
    except ValueError as ex:rejection=str(ex)
    else:raise AssertionError('v3 admitted zero target pressure')
    # This illustrates the remaining absolute-residual conditioning limitation,
    # rather than claiming to have observed an additional compiled failure.
    de=[-.3]*3+[0.]*3
    target=evaluation_environment(b,old,old,de,p)
    small={'sigma':[1e-48]*3+[0.]*3,'v':target['v_end']}
    rr=interpret(b,small,old,de,p)
    scaled_residual=max(max(abs(x)/p['pref'] for x in rr['sigma'].v),abs(rr['v']))
    assert 0<target['p_end']<1e-100 and scaled_residual<1e-11
    recovery_error=sum(de[:3])-p['kappa']/small['v']*math.log(1e-48/pressure)
    assert abs(recovery_error)>.5
    out=dict(passed=True,compiled_calls=0,
             inputs={str(B/f'candidate-v03-{v}.json'):hashlib.sha256((B/f'candidate-v03-{v}.json').read_bytes()).hexdigest() for v in ('v2','v3')},
             underflow_guard=dict(stored_de=underflow,v2_target_pressure=e['p_end'],v3_rejection=rejection),
             conditioning_only=dict(stored_de=de,positive_target_pressure=target['p_end'],hypothetical_state=small,scaled_equation_residual=scaled_residual,uneliminated_elastic_recovery_error=recovery_error,
                                    claim='Portable residual-conditioning witness only; no compiled outcome or changed gate.'))
    (P/'candidate-v3-guard-results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
