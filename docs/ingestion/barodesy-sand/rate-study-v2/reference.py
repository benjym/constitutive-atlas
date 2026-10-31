"""Independent Decimal Cartesian rate oracle for the explicitly bounded2015 law.

No Atlas imports. Forward matrix power series, no Horner18/scaling-squaring reuse.
Actual binary64 Mandel inputs -> exact Decimal floats -> Decimal sqrt2 conversion.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
import support
import json
import math
from pathlib import Path

VERSION='barodesy-sand-2015-cartesian-decimal-series-exact-volume-v2'
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


def exact_volume(case):
    _,z,d=support.case_values(case)
    trace_fraction=sum((Fraction.from_float(x)for x in d[:3]),Fraction(0))
    void_fraction=-(1+Fraction.from_float(z[6]))*trace_fraction
    return trace_fraction,void_fraction


def exact_decimal(value):
    # Binary64 sums/products have power-of-two denominators; exact terminating decimal.
    n,d=value.numerator,value.denominator
    if d&(d-1):raise ValueError('binary rational required')
    k=d.bit_length()-1;digits=n*5**k
    with localcontext()as ctx:
        ctx.prec=max(1,len(str(abs(digits))))
        return Decimal(digits).scaleb(-k)


def ideal_source_rate(case,precision=80):
    """Ideal mathematical source interior; NOT operational binary64 acceptance.

    Source parameters remain inside the research envelope, but no numerical
    stress/loading/density margins are imposed. Rate80/120 agreement is empirical.
    Void rate is correctly rounded directly from exact actual-binary64 rationals.
    """
    if type(precision)is not int or precision<50:raise ValueError('precision>=50 integer required')
    support.case_values(case)
    trace_fraction,void_fraction=exact_volume(case)
    with localcontext() as ctx:
        ctx.prec=precision
        p={name:real(case['parameters'][name]) for name in ORDER}
        for name,(lo,hi) in BOUNDS.items():
            if not real(lo)<=p[name]<=real(hi): raise ValueError('parameter envelope:'+name)
        z=vector(case['state'],7)
        load=vector(case['loading'],6)
        e=z[-1]
        if not (p['ec0']>p['emin'] and e>p['emin']):
            raise ValueError('ideal density/parameter interior')
        # Work in source tension-positive Cartesian convention independently.
        t=unpack([-x for x in z[:6]])
        d=unpack([-x for x in load])
        sn=norm(t)
        scaled=sn/p['c4']
        if not scaled>0:
            raise ValueError('ideal nonzero stress required')
        s=[[-x/sn for x in row] for row in t]
        minor=s[0][0]*s[1][1]-s[0][1]*s[0][1]
        det=(s[0][0]*(s[1][1]*s[2][2]-s[1][2]*s[2][1])
             -s[0][1]*(s[1][0]*s[2][2]-s[1][2]*s[2][0])
             +s[0][2]*(s[1][0]*s[2][1]-s[1][1]*s[2][0]))
        if any(s[i][i]<=0 for i in range(3)) or minor<=0 or det<=0:
            raise ValueError('ideal SPD stress required')
        speed=norm(d)
        zero=not any(load)
        if not zero and not speed: raise ValueError('loading lost')
        u=[[x/speed if speed else Decimal(0) for x in row] for row in d]
        delta=-exact_decimal(trace_fraction)/speed if speed else Decimal(0)
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
        ec_gap=b*(1+p['emin'])/(1-b)
        ec=p['emin']+ec_gap
        h=-(p['c4']+p['c5']*sn)/(e-p['emin'])
        f=delta+p['c3']*ec
        g=-p['c3']*e
        td=[[h*(-f*positive[i][j]/rn+g*t[i][j]/sn)*speed for j in range(3)] for i in range(3)]
        stress=pack([[-x for x in row] for row in td])
        ed=exact_decimal(void_fraction)
        values=stress+[ed]
        if not all(x.is_finite() for x in values): raise ValueError('nonfinite result')
        return {'values':[float(x) for x in stress]+[float(void_fraction)],
                'decimal_values':[str(x) for x in values],
                'ec':float(ec),'ideal_ec_gap_decimal':str(ec_gap),'void_exact_fraction':{'numerator':str(void_fraction.numerator),'denominator':str(void_fraction.denominator)},'argument_norm':float(argnorm),'terms':terms,
                'precision':precision,'zero_loading_extension':zero}


def read_inputs():
    return json.loads(Path(__file__).with_name('inputs.json').read_text())


def build_reference(inputs=None):
    inputs=read_inputs()if inputs is None else inputs
    records=[]
    for c in inputs['valid']+inputs['additional_operational_valid']:
        operational=support.validate(c)
        lo,hi=ideal_source_rate(c,80),ideal_source_rate(c,120)
        if lo['values'][6]!=hi['values'][6]:raise ValueError('exact void mismatch')
        records.append({'id':c['id'],'oracle80':lo,'oracle120':hi,'operational_support':operational,'binary64_precision_difference':[abs(x-y)for x,y in zip(lo['values'],hi['values'])]})
    failures=[]
    for c in inputs['invalid']+inputs['additional_operational_invalid']:
        try:support.validate(c)
        except(ValueError,ArithmeticError)as exc:message=str(exc)
        else:raise ValueError('operational invalid accepted:'+c['id'])
        try:ideal={'accepted':True,'result':ideal_source_rate(c,120)}
        except(ValueError,ArithmeticError)as exc:ideal={'accepted':False,'message':str(exc)}
        failures.append({'id':c['id'],'operational_rejected':True,'message':message,'ideal_source':ideal})
    return {'version':VERSION,'records':records,'invalid':failures,'scope':'Ideal Cartesian source rates separated from operational binary64 support; exact rational volumetric channel; no integration or admission'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--check',type=Path);args=parser.parse_args()
    result=build_reference()
    if args.check and json.loads(args.check.read_text())!=result:raise SystemExit('reference mismatch')
    if args.output:
        if args.output.exists():raise SystemExit('fresh output required')
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if args.check:print('exact-volume independent reference replay: PASS')
