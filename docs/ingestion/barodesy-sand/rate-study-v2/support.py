"""Operational Python binary64 support classifier, not an ideal source oracle.

No Atlas imports. These finite numerical margins are project choices unchanged
from v1. Boundary classifications are not certified equivalent across compilers.
"""
import math
ORDER=('c1','c2','c3','c4','c5','ec0','emin')
BOUNDS={'c1':(-2.,-.1),'c2':(0.,1.5),'c3':(-5.,-.1),'c4':(1000.,1e8),'c5':(.1,100.),'ec0':(.1,2.),'emin':(0.,1.)}
MARGIN=64*math.ulp(1.)


def real(x):
    if type(x)not in(int,float):raise ValueError('finite non-Boolean binary64 required')
    try:y=float(x)
    except(OverflowError,ValueError)as exc:raise ValueError('finite binary64 required')from exc
    if not math.isfinite(y)or y!=x:raise ValueError('finite exact binary64 input required')
    return y


def case_values(case):
    if type(case)is not dict or set(case)!={'id','state','loading','parameters'}or type(case['id'])is not str:raise ValueError('exact case keys required')
    if type(case['parameters'])is not dict or set(case['parameters'])!=set(ORDER):raise ValueError('exact parameter names required')
    p={n:real(case['parameters'][n])for n in ORDER}
    for n,(lo,hi)in BOUNDS.items():
        if not lo<=p[n]<=hi:raise ValueError('parameter envelope:'+n)
    def vector(v,n):
        if type(v)not in(list,tuple)or len(v)!=n:raise ValueError('vector arity')
        return [real(x)for x in v]
    return p,vector(case['state'],7),vector(case['loading'],6)


def validate(case):
    p,z,d=case_values(case)
    try:
        if not(p['ec0']>p['emin']and z[6]>p['emin']and z[6]-p['emin']>=1e-8 and z[6]<=3):raise ValueError('operational density interior')
        scaled=[x/p['c4']for x in z[:6]];s=math.sqrt(sum(x*x for x in scaled))
        if not(1e-10<=s<=1e10):raise ValueError('operational stress norm')
        x,y,t,u,v,w=[x/s for x in scaled]
        minor=x*y-u*u/2;det=x*y*t-(x*v*v+y*w*w+t*u*u)/2+u*v*w/math.sqrt(2)
        if not(x>0 and y>0 and t>0 and minor>MARGIN and det>MARGIN):raise ValueError('operational SPD margin')
        speed=math.sqrt(sum(x*x for x in d));nonzero=any(x!=0 for x in d)
        if speed>1000 or(nonzero and speed<1e-140):raise ValueError('operational loading envelope; no underflow-to-zero continuation')
        B=(p['ec0']-p['emin'])/(p['ec0']+1)*math.exp(-(1+p['emin'])/p['c5']*math.log1p(p['c5']*s))
        ec=(p['emin']+B)/(1-B)
        if not(0<B<1 and ec>p['emin']):raise ValueError('operational rounded critical density')
        v=math.fsum(d[:3])/speed if speed else 0.;arg=abs(p['c1'])*math.exp(-p['c2']*v)if speed else 0.
        if not(math.isfinite(arg)and arg<=64):raise ValueError('operational expm envelope')
        return dict(stress_measure=s,loading_measure=speed,B=B,ec_binary64=ec,argument_norm=arg)
    except(ArithmeticError,OverflowError)as exc:raise ValueError('nonrepresentable operational support')from exc
