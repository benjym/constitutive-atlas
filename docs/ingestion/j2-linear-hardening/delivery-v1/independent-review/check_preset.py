#!/usr/bin/env python3
"""Prospective exact-rational coaxial default path; no Atlas/oracle/backend imports."""
from fractions import Fraction as F
import json

def run():
    G=F(12000000);H=F(1200000);Y=F(60000);t=F(0);alpha=F(0)
    rows=[]
    for d in [F(3,2000),-F(3,2000),F(0)]:
        # sigma=(2t,-t,-t), de=(2d,-d,-d), pressure zero.
        trial=t+2*G*d;qt=3*abs(trial);g=max(F(0),(qt-Y-H*alpha)/(3*G+H))
        t=(1 if trial>=0 else -1)*(qt-3*G*g)/3
        alpha+=g
        sigma=[2*t,-t,-t,F(0),F(0),F(0)]
        q=3*abs(t)
        assert q<=Y+H*alpha and g>=0 and g*(q-Y-H*alpha)==0
        rows.append(dict(increment=[float(v) for v in (2*d,-d,-d,0,0,0)],
                         state=[float(v) for v in sigma+[alpha,g]],
                         exact_state=[str(v) for v in sigma+[alpha,g]]))
    assert rows[0]['exact_state'][6]=='1/775'
    assert rows[1]['exact_state'][6]=='1/775' and rows[1]['exact_state'][7]=='0'
    assert rows[1]['state']==rows[2]['state']
    return dict(method='exact rational axisymmetric deviator; source scalar consistency; no Atlas/study/backend import',
                parameters=[100000,20000000,12000000,60000,1200000],initial=[0]*8,rows=rows,
                interpretation='First row plastic; second reversed increment is elastic; final hold retains stress/alpha and zero temporary gamma.',compiled_calls=0)
if __name__=='__main__':print(json.dumps(run(),indent=2))
