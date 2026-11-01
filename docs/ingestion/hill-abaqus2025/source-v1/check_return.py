#!/usr/bin/env python3
"""Additional independent oracle identities; preserves first algebra run."""
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
from check_algebra import endpoint, matrix, action, square


def main():
    with localcontext() as ctx:
        ctx.prec=80
        d=Decimal
        p={k:d(v) for k,v in dict(F='.7',Gh='.5',Hh='.3',L='1.2',M='1.7',N='2',K='20000000',Gmod='12000000',sigma_y='60000').items()}
        a=matrix(p);checks=0;worst=d(0)
        paths=[['.01','-.003','.002','.004','-.002','.003'],['-.01','.003','-.002','-.004','.002','-.003'],['0','0','0','.02','0','0'],['0','0','0','0','.02','0'],['0','0','0','0','0','.02']]
        for raw in paths:
            e=list(map(d,raw));out=endpoint(p,[0]*6,e);s=out[:6];g=out[6]
            ev=sum(e[:3]);t=[2*p['Gmod']*(e[i]-ev/3 if i<3 else e[i])+(p['K']*ev if i<3 else 0) for i in range(6)]
            residual=[s[i]-t[i]+2*p['Gmod']*g*v/p['sigma_y'] for i,v in enumerate(action(a,s))]
            error=max(map(abs,residual));worst=max(worst,error)
            assert error<d('1e-60')
            assert abs(square(a,s)-p['sigma_y']**2)<d('1e-60')
            assert g>0
            # Discrete dissipation on the active endpoint is Y*gamma.
            work=sum(s[i]*g*v/p['sigma_y'] for i,v in enumerate(action(a,s)))
            assert abs(work-p['sigma_y']*g)<d('1e-60')
            checks+=4
        u=list(map(d,['1','-2','3','4','5','-6']));v=list(map(d,['-3','2','-1','6','-5','4']))
        for raw in ['0','.1','.3','.5','.9','1']:
            w=d(raw);mixed=[w*x+(1-w)*y for x,y in zip(u,v)]
            # Convex quadratic and its exact Jensen gap.
            gap=w*square(a,u)+(1-w)*square(a,v)-square(a,mixed)
            expected=w*(1-w)*square(a,[x-y for x,y in zip(u,v)])
            assert gap==expected and gap>=0;checks+=1
        print(json.dumps({'status':'pass','checks':checks,'maximum_endpoint_stress_residual_Pa':str(worst),'precision':80,'compiled_calls':0,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':
    main()
