"""Independent identities implied by the inspected readable dataset, not VIBE validation."""
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
import json

def check():
    count=0
    for q in [F(-1,4), F(0),F(1,10),F(1),F(17,3)]:
        for x in [[F(i+j+1,7) for i in range(3)] for j in range(7)]:
            # B:X=X+q tr(X) I; inverse eigenvalue is 1/(1+3q).
            y=[a-q/(1+3*q)*sum(x) for a in x]
            assert [a+q*sum(y) for a in y]==x
            count+=3
    with localcontext() as c:
        c.prec=70
        # Analytic derivative of S=1-exp[-(se/s)^lambda], positive physical suction.
        se=D(2000);s=D(10000);lam=D('1.1');h=D('1e-15')
        def sat(v):return 1-(-(lam*(se/v).ln()).exp()).exp()
        S=sat(s)
        analytic=(1-S)*lam*(1-S).ln()/s
        numerical=(sat(s+h)-sat(s-h))/(2*h)
        assert abs(analytic-numerical)<D('1e-40')
        assert analytic<0
    return {'status':'pass','scope':'rank-one inverse exact identities and WRC derivative only; no model integration or scientific admission', 'exact_fraction_component_identities':count,'wrc_derivative_absolute_error':str(abs(analytic-numerical))}
if __name__=='__main__':print(json.dumps(check(),indent=2))
