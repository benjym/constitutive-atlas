"""Independent Decimal Cartesian rate oracle for the explicitly bounded2015 law.

No Atlas imports. Forward matrix power series, no Horner18/scaling-squaring reuse.
Actual binary64 Mandel inputs -> exact Decimal floats -> Decimal sqrt2 conversion.
"""
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path

VERSION='barodesy-sand-2015-cartesian-decimal-series-v1'
ORDER=('c1','c2','c3','c4','c5','ec0','emin')
BOUNDS={'c1':(-2.,-.1),'c2':(0.,1.5),'c3':(-5.,-.1),'c4':(1000.,1e8),
        'c5':(.1,100.),'ec0':(.1,2.),'emin':(0.,1.)}
DEFAULTS=dict(c1=-1.0246,c2=1.,c3=-2.3,c4=465000.,c5=28.,ec0=.87,emin=.35)
MARGIN=Decimal.from_float(64*math.ulp(1.))


def real(x):
    if type(x) not in (int,float) or not math.isfinite(x):
        raise ValueError('finite non-Boolean real required')
    return Decimal.from_float(float(x))


def vector(x,n):
    if type(x) not in (list,tuple) or len(x)!=n:
        raise ValueError('invalid vector shape')
    return [real(v) for v in x]


def unpack(v):
    x,y,z,u,v,w=v
    r=Decimal(2).sqrt()
    return [[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]


def pack(a):
    r=Decimal(2).sqrt()
    return [a[0][0],a[1][1],a[2][2],r*a[0][1],r*a[1][2],r*a[0][2]]


def norm(a):
    return sum((x*x for row in a for x in row),Decimal(0)).sqrt()


def multiply(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(3)),Decimal(0))
             for j in range(3)] for i in range(3)]


def expm_series(a):
    # Direct differentiated terms are unnecessary for this rate-only scope.
    # Stop only when a geometric tail majorant is <10^(-precision+10).
    from decimal import getcontext
    one=Decimal(1)
    out=[[Decimal(i==j) for j in range(3)] for i in range(3)]
    term=[row[:] for row in out]
    anorm=max(sum(abs(x) for x in row) for row in a)
    target=Decimal(10)**(-getcontext().prec+10)
    for k in range(1,1200):
        term=[[x/Decimal(k) for x in row] for row in multiply(term,a)]
        out=[[out[i][j]+term[i][j] for j in range(3)] for i in range(3)]
        termnorm=max(sum(abs(x) for x in row) for row in term)
        ratio=anorm/Decimal(k+1)
        if ratio<one and termnorm*ratio/(one-ratio)<target:
            return out,k
    raise ValueError('independent series did not converge')


def evaluate(case,precision=80):
    if type(precision) is not int or precision<50:
        raise ValueError('precision>=50 integer required')
    if type(case) is not dict or set(case)!= {'id','state','loading','parameters'} or type(case['id']) is not str:
        raise ValueError('exact case keys required')
    if type(case['parameters']) is not dict or set(case['parameters'])!=set(ORDER):
        raise ValueError('exact physical parameter keys required')
    with localcontext() as ctx:
        ctx.prec=precision
        p={name:real(case['parameters'][name]) for name in ORDER}
        for name,(lo,hi) in BOUNDS.items():
            if not real(lo)<=p[name]<=real(hi): raise ValueError('parameter envelope:'+name)
        z=vector(case['state'],7)
        load=vector(case['loading'],6)
        e=z[-1]
        if not (p['ec0']>p['emin'] and e>p['emin'] and e-p['emin']>=Decimal('1e-8') and e<=3):
            raise ValueError('density/parameter interior')
        # Work in source tension-positive Cartesian convention independently.
        t=unpack([-x for x in z[:6]])
        d=unpack([-x for x in load])
        sn=norm(t)
        scaled=sn/p['c4']
        if not Decimal('1e-10')<=scaled<=Decimal('1e10'):
            raise ValueError('nonzero bounded stress required')
        s=[[-x/sn for x in row] for row in t]
        minor=s[0][0]*s[1][1]-s[0][1]*s[0][1]
        det=(s[0][0]*(s[1][1]*s[2][2]-s[1][2]*s[2][1])
             -s[0][1]*(s[1][0]*s[2][2]-s[1][2]*s[2][0])
             +s[0][2]*(s[1][0]*s[2][1]-s[1][1]*s[2][0]))
        if any(s[i][i]<=0 for i in range(3)) or minor<=MARGIN or det<=MARGIN:
            raise ValueError('conservative normalized SPD interior')
        speed=norm(d)
        if speed>1000 or (speed and speed<Decimal('1e-140')):
            raise ValueError('loading numerical support')
        zero=not any(load)
        if not zero and not speed: raise ValueError('loading lost')
        u=[[x/speed if speed else Decimal(0) for x in row] for row in d]
        delta=sum(u[i][i] for i in range(3))
        a=p['c1']*(p['c2']*delta).exp()
        arg=[[a*x for x in row] for row in u]
        argnorm=norm(arg)
        if argnorm>64: raise ValueError('expm envelope')
        positive,terms=expm_series(arg)
        # R=-expm(arg); normalize negative matrix and T as source defines.
        rn=norm(positive)
        b=(p['ec0']-p['emin'])/(p['ec0']+1)*(
            -(1+p['emin'])/p['c5']*(1+p['c5']*scaled).ln()).exp()
        if not 0<b<1: raise ValueError('critical density branch')
        ec=(p['emin']+b)/(1-b)
        h=-(p['c4']+p['c5']*sn)/(e-p['emin'])
        f=delta+p['c3']*ec
        g=-p['c3']*e
        td=[[h*(-f*positive[i][j]/rn+g*t[i][j]/sn)*speed for j in range(3)] for i in range(3)]
        stress=pack([[-x for x in row] for row in td])
        ed=(1+e)*sum(d[i][i] for i in range(3))
        values=stress+[ed]
        if not all(x.is_finite() for x in values): raise ValueError('nonfinite result')
        return {'values':[float(x) for x in values],
                'decimal_values':[str(x) for x in values],
                'ec':float(ec),'argument_norm':float(argnorm),'terms':terms,
                'precision':precision,'zero_loading_extension':zero}


def read_inputs():
    return json.loads(Path(__file__).with_name('inputs.json').read_text())


def build_reference(inputs=None):
    inputs=read_inputs() if inputs is None else inputs
    records=[]
    for c in inputs['valid']:
        lo,hi=evaluate(c,80),evaluate(c,120)
        differences=[abs(x-y) for x,y in zip(lo['values'],hi['values'])]
        # Decimal absolute differences are retained even when floats round equal.
        with localcontext() as ctx:
            ctx.prec=140
            decdiff=[str(abs(Decimal(x)-Decimal(y))) for x,y in zip(lo['decimal_values'],hi['decimal_values'])]
        records.append({'id':c['id'],'oracle80':lo,'oracle120':hi,
                        'binary64_precision_difference':differences,
                        'decimal_precision_difference':decdiff})
    failures=[]
    for c in inputs['invalid']:
        try: evaluate(c)
        except (ValueError,ArithmeticError) as exc:
            failures.append({'id':c['id'],'rejected':True,'message':str(exc)})
        else: raise ValueError('invalid fixture unexpectedly accepted:'+c['id'])
    return {'version':VERSION,'records':records,'invalid':failures,
            'scope':'independent instantaneous Cartesian rates only; no AD, finite integration or admission'}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',type=Path)
    args=parser.parse_args()
    result=build_reference()
    if args.check and json.loads(args.check.read_text())!=result: raise SystemExit('reference mismatch')
    if args.output: args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if args.check: print('independent reference replay: PASS')
