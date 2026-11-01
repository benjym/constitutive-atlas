"""Portable source/DSL candidate checks; no compiled calls.

The scalar oracle is authored by the separate reviewing agent and solves the
uneliminated finite equations by Decimal bisection. Candidate expressions are
interpreted by the ordinary Atlas loader. Production model code is not an oracle.
"""
from decimal import Decimal as Dec
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from atlas.model import load,defaults,evaluation_environment,interpret
from atlas.initialization import initialize_state

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('occ_independent',BASE/'independent-review/check_constraints.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
model=load(BASE/'candidate-v03.json'); pars=defaults(model)
policy=json.loads((BASE/'prospective.json').read_text())

def env(z,de,p=pars):
    state={'sigma':z[:6],'v':z[6]}
    return evaluation_environment(model,state,state,de,p)

def target(z,de,p=pars):
    e=env(z,de,p)
    return tuple(e['sigma_end'].v)+(e['v_end'],)

def matrix(a):
    r=math.sqrt(2)
    return [[a[0],a[3]/r,a[5]/r],[a[3]/r,a[1],a[4]/r],[a[5]/r,a[4]/r,a[2]]]

def rotate(a):
    q=[[.6,-.8,0.],[.8,.6,0.],[0.,0.,1.]];t=matrix(a)
    x=[[math.fsum(q[i][k]*t[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return (x[0][0],x[1][1],x[2][2],math.sqrt(2)*x[0][1],math.sqrt(2)*x[1][2],math.sqrt(2)*x[0][2])

def main():
    corpus=json.loads((BASE/'independent-review/constraint-results.json').read_text())['cases']
    cases=[];worst=0.
    for row in corpus:
        xn,gap,E,r=[Dec(row[n]) for n in ('xn','gap','E','r')]
        vn=ref.GA+ref.LA-ref.K-ref.LA*xn-(ref.LA-ref.K)*gap
        qn=ref.M*xn.exp()*gap*Dec('.6')
        rr=ref.oracle(vn,xn,E,r,qn)
        p0=float(xn.exp())*pars['pref'];q0=float(qn)*pars['pref']
        z=(p0+2*q0/3,p0-q0/3,p0-q0/3,0.,0.,0.,float(vn))
        de=[float(E)/3+float(r),float(E)/3-float(r)/2,float(E)/3-float(r)/2,0.,0.,0.]
        actual=target(z,de)
        pp=float(rr[1].exp())*pars['pref'];qq=float(rr[2])*pars['pref']
        expected=(pp+2*qq/3,pp-qq/3,pp-qq/3,0.,0.,0.,float(rr[0]))
        # E=r=0 has exact identity rather than bisection roundoff.
        if E==0 and r==0:expected=z
        err=max(abs(a-b)/max(1.,abs(b)) for a,b in zip(actual,expected))
        # If a tiny r is added to nonzero E, de's stored diagonal differences can
        # round away. Oracle must be bound to actual stored controls, not ideal r.
        # Such a request is a true zero-distortion increment in the wire format.
        stored_dev=[de[i]-math.fsum(de[:3])/3 for i in range(3)]
        if r and not any(stored_dev):
            actual_r=Dec(0)
            rr=ref.oracle(vn,xn,E,actual_r,qn)
            pp=float(rr[1].exp())*pars['pref'];qq=float(rr[2])*pars['pref']
            expected=(pp+2*qq/3,pp-qq/3,pp-qq/3,0.,0.,0.,float(rr[0]))
            err=max(abs(a-b)/max(1.,abs(b)) for a,b in zip(actual,expected))
        assert err<=policy['physical_residual_relative_budget'], (row,err,actual,expected)
        residual=interpret(model,{'sigma':actual[:6],'v':actual[6]},{'sigma':z[:6],'v':z[6]},de,pars)
        assert max(abs(x) for x in residual['sigma'].v)<1e-7
        assert abs(residual['v'])<1e-12
        worst=max(worst,err)
        cases.append(dict(case=row,stored_de=de,reference_expected=expected,actual=actual,relative_error=err))
    # Explicitly preserve a pure shear smaller than sqrt(min-normal) and the
    # smallest subnormal wire component: zero detection uses extracted components.
    p0=50000.;pc0=100000.;d=pars['lambda_c']-pars['kappa']
    v=pars['Gamma']+d*(1-math.log(pc0/pars['pref']))-pars['kappa']*math.log(p0/pars['pref'])
    z=(p0,p0,p0,0.,0.,0.,v)
    tiny=[]
    for value in [1e-12,1e-100,1e-200,float.fromhex('0x0.0000000000001p-1022')]:
        out=target(z,[0.,0.,0.,value,0.,0.])
        assert abs(out[3])>1000 and all(math.isfinite(x) for x in out)
        tiny.append(dict(mandel_shear=value,state=out))
    hold=(51000.,49500.,49500.,200.,-300.,100.,v)
    assert target(hold,[0.]*6)==hold
    rotations=[]
    for i in [0,10,20,50,80,100,125,150,200,250,300,350,399]:
        c=cases[i];row=c['case'];x=Dec(row['xn']);gap=Dec(row['gap'])
        p0=float(x.exp())*pars['pref'];q0=float(ref.M*x.exp()*gap*Dec('.6'))*pars['pref']
        vn=float(ref.GA+ref.LA-ref.K-ref.LA*x-(ref.LA-ref.K)*gap)
        old=(p0+2*q0/3,p0-q0/3,p0-q0/3,0.,0.,0.,vn)
        wanted=rotate(c['actual'][:6])+(c['actual'][6],)
        actual=target(rotate(old[:6])+(vn,),rotate(c['stored_de']))
        err=max(abs(a-b)/max(pars['pref'],abs(b)) for a,b in zip(actual,wanted))
        assert err<policy['rotation_relative_budget'],(i,err)
        rotations.append(dict(case=i,error=err))
    default={f['name']:f['initial'] for f in model['state']}
    initialize_state(model,default,pars)
    invalid=[]
    for name,st in [('negative volume',{'sigma':list(z[:6]),'v':-1}),('negative pressure',{'sigma':[-1.]*3+[0.]*3,'v':v}),('outside yield',{'sigma':[2e5,-2.5e4,-2.5e4,0.,0.,0.],'v':v})]:
        try: initialize_state(model,st,pars)
        except (ValueError,ArithmeticError):invalid.append(name)
        else: raise AssertionError(('invalid initialization accepted',name))
    for bad in [[-1.]*3+[0.]*3,[float('nan'),0.,0.,0.,0.,0.]]:
        try: target(z,bad)
        except (ValueError,ArithmeticError): pass
        else: raise AssertionError('invalid loading accepted')
    result=dict(passed=True,candidate_sha256=hashlib.sha256((BASE/'candidate-v03.json').read_bytes()).hexdigest(),independent_scalar_cases=len(cases),maximum_relative_error=worst,cases=cases,tiny_shears=tiny,exact_nonisotropic_hold=True,rotations=rotations,initialization_rejections=invalid,compiled_calls=0)
    (BASE/'candidate-checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','tiny_shears','rotations')},indent=2))

if __name__=='__main__':main()
