"""Bind the independent finite-law oracle to exact stored binary64 controls.

Failures are retained as results; this diagnostic never edits a candidate.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
sys.path.insert(0,str(BASE.parents[3]))
from atlas.model import load, defaults, evaluation_environment
spec=importlib.util.spec_from_file_location('independent_scalar',HERE/'check_constraints.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
model=load(BASE/'candidate-v03.json');pars=defaults(model)


def dec(f):
    return D(f.numerator)/D(f.denominator)


def exact_parts(values):
    a=list(map(F.from_float,values))
    mean=sum(a[:3],F(0))/3
    s=[x-mean if i<3 else x for i,x in enumerate(a)]
    return mean,s


def expected(z,de):
    if not any(de):return tuple(z)
    with localcontext() as ctx:
        ctx.prec=110
        mean,s=exact_parts(z[:6])
        emean,dd=exact_parts(de)
        pn=dec(mean)/D(str(pars['pref']))
        xn=pn.ln();vn=D.from_float(z[6])
        sn=[dec(x)/D(str(pars['pref'])) for x in s]
        qn=(D('1.5')*sum(x*x for x in sn)).sqrt()
        E=3*dec(emean)
        dd=list(map(dec,dd))
        r=(D(2)/3*sum(x*x for x in dd)).sqrt()
        v,x,q,L,branch,_=ref.oracle(vn,xn,E,r,qn)
        p=x.exp()*D(str(pars['pref']))
        if r:
            out=[D(2)/3*q/r*d*D(str(pars['pref'])) for d in dd]
        elif qn:
            out=[t*q/qn*D(str(pars['pref'])) for t in sn]
        else:out=[D(0)]*6
        return tuple(float(t+p if i<3 else t) for i,t in enumerate(out))+(float(v),)


def actual(z,de):
    old={'sigma':z[:6],'v':z[6]}
    env=evaluation_environment(model,old,old,de,pars)
    return tuple(env['sigma_end'].v)+(env['v_end'],),env


def check(name,z,de):
    ex=expected(z,de);ac,en=actual(z,de)
    err=max(abs(a-b)/max(pars['pref'],abs(b)) for a,b in zip(ac,ex))
    mean=sum(ac[:3])/3
    return dict(name=name,old=z,stored_de=de,expected=ex,actual=ac,
                error=err,passed=err<=2e-10,
                target_pressure=en['p_end'],output_mean=mean,
                normalized_deviator=en['deviator_unitbox'].v)


def main():
    cases=[]
    failure=json.loads((BASE/'failed-rotation-v1/failure.json').read_text())
    cases.append(check('retained rotated actual wire input',failure['rotated_old'],failure['rotated_stored_de']))
    corpus=json.loads((HERE/'constraint-results.json').read_text())['cases']
    for i,row in enumerate(corpus):
        xn,gap,E,r=[D(row[k]) for k in ('xn','gap','E','r')]
        vn=ref.GA+ref.LA-ref.K-ref.LA*xn-(ref.LA-ref.K)*gap
        p=float(xn.exp())*pars['pref'];q=float(ref.M*xn.exp()*gap*D('.6'))*pars['pref']
        z=(p+2*q/3,p-q/3,p-q/3,0.,0.,0.,float(vn))
        de=(float(E)/3+float(r),float(E)/3-float(r)/2,float(E)/3-float(r)/2,0.,0.,0.)
        cases.append(check('corpus '+str(i),z,de))
    p=50000.;pc=100000.;d=pars['lambda_c']-pars['kappa']
    v=pars['Gamma']+d*(1-math.log(pc/pars['pref']))-pars['kappa']*math.log(p/pars['pref'])
    z=(p,p,p,0.,0.,0.,v)
    for shear in (1e-12,1e-100,1e-200,float.fromhex('0x0.0000000000001p-1022')):
        cases.append(check('pure tiny shear '+str(shear),z,(0.,0.,0.,shear,0.,0.)))
    # Adjacent floating diagonal values are real stored distortions, however small.
    for hydro in (-.03333333333333333,.01):
        de=(hydro,hydro,math.nextafter(hydro,math.inf),0.,0.,0.)
        cases.append(check('adjacent diagonal '+str(hydro),z,de))
    files=[BASE/'candidate-v03.json',BASE/'check_candidate.py',BASE/'prospective.json',BASE/'failed-rotation-v1/failure.json',HERE/'check_constraints.py']
    result=dict(identity='occ-candidate-exact-stored-input-review-v1',
                bindings={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
                budget=2e-10,count=len(cases),passed=all(c['passed'] for c in cases),
                failures=[c for c in cases if not c['passed']],cases=cases,
                compiled_calls=0)
    # Bind outputs to exact bytes even if implementation changes concurrently.
    digest=result['bindings'][str(BASE/'candidate-v03.json')][:12]
    out=HERE/('candidate-review-results-'+digest+'.json')
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(result_file=str(out),count=len(cases),passed=result['passed'],
                          failures=[dict(name=c['name'],error=c['error']) for c in result['failures']]),indent=2))


if __name__=='__main__':main()
