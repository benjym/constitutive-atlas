"""Source-mapped Cartesian rate and independent RK4 verification of VW96.

No DSL evaluator, generated tensor primitives or production integration method
is used to compute reference values. This does not supply independent authorship.
"""
import argparse
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.evidence import sha256

RATE_STRESS_ATOL=1e-4
RATE_STATE_ATOL=1e-11
RATE_RTOL=1e-9
PATH_STRESS_ATOL=1.
PATH_STATE_ATOL=1e-8
PATH_RTOL=2e-5
REFERENCE_STRESS_ATOL=.001
REFERENCE_STATE_ATOL=1e-11
REFERENCE_RTOL=1e-10
MODEL='hypoplastic-sand-vw96'


def csv(values): return ','.join(format(v,'.17g') for v in values)
def matrix(v):
    r=math.sqrt(2)
    return [[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]
def mandel(a): return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
def trace(a): return sum(a[i][i] for i in range(3))
def inner(a,b): return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def multiply(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def reference_rate(state,strain,parameters):
    """Evaluate Fellin's source in its tension-positive Cartesian convention."""
    _,phi,hs,n,ed0,ec0,ei0,alpha,beta=parameters
    T=[[-x for x in row] for row in matrix(state)]
    D=[[-x for x in row] for row in matrix(strain)]
    tr=trace(T);p=-tr/3;e=state[6]
    if p<=0: raise ValueError('positive effective mean pressure required')
    hat=[[x/tr for x in row] for row in T]
    star=[[hat[i][j]-(1/3 if i==j else 0) for j in range(3)] for i in range(3)]
    j2=inner(star,star);psi=math.sqrt(3*j2)
    cos3=-math.sqrt(6)*trace(multiply(multiply(star,star),star))/j2**1.5 if j2 else 0
    F=math.sqrt(psi*psi/8+(2-psi*psi)/(2+math.sqrt(2)*psi*cos3))-psi/(2*math.sqrt(2))
    a=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi))
    compression=math.exp(-(3*p/hs)**n)
    ed,ec,ei=(x*compression for x in (ed0,ec0,ei0))
    if not ed<e<ei: raise ValueError('density outside declared atlas domain')
    fd=((e-ed)/(ec-ed))**alpha;fe=(ec/e)**beta
    fb=hs/n*(ei0/ec0)**beta*(1+ei)/ei*(3*p/hs)**(1-n)/(3+a*a-a*math.sqrt(3)*((ei0-ed0)/(ec0-ed0))**alpha)
    scalar=fb*fe/inner(hat,hat);projection=inner(hat,D);norm=math.sqrt(inner(D,D))
    Tdot=[[scalar*(F*F*D[i][j]+a*a*hat[i][j]*projection+fd*a*F*(hat[i][j]+star[i][j])*norm) for j in range(3)] for i in range(3)]
    # Reversing stress AND stretching changes the sign of the norm contribution.
    return [-x for x in mandel(Tdot)]+[(1+e)*trace(D)]


def compare(actual,expected,stress_atol,state_atol,rtol):
    if len(actual)!=len(expected) or not all(math.isfinite(x) for x in actual): return False,None
    ratios=[abs(a-b)/((stress_atol if i<6 else state_atol)+rtol*abs(b)) for i,(a,b) in enumerate(zip(actual,expected))]
    ratio=max(ratios,default=0)
    return ratio<=1,ratio


def rk4(initial,strain,parameters,steps):
    z=initial.copy();h=1/steps
    def shifted(z,k,f): return [a+h*f*b for a,b in zip(z,k)]
    for _ in range(steps):
        a=reference_rate(z,strain,parameters)
        b=reference_rate(shifted(z,a,.5),strain,parameters)
        c=reference_rate(shifted(z,b,.5),strain,parameters)
        d=reference_rate(shifted(z,c,1),strain,parameters)
        z=[x+h*(w+2*y+2*t+u)/6 for x,w,y,t,u in zip(z,a,b,c,d)]
    return z


def execute(solver):
    description=json.loads(subprocess.check_output([str(solver),'--describe'],text=True))
    definition=json.loads((ROOT/'models'/f'{MODEL}.json').read_text())
    if definition!=next(m for m in description['models'] if m['id']==MODEL): raise ValueError('Rebuild solver: embedded model differs')
    parameters=[item['default'] for item in definition['parameters'].values()]
    cases=[]
    def invoke(mode,state,strain,params):
        args=['--model',MODEL,'--mode',mode,'--parameters',csv(params),'--strain',csv(strain)]
        if mode=='evaluate': args+=['--current',csv(state),'--initial',csv(state)]
        else: args+=['--initial',csv(state)]
        p=subprocess.run([str(solver),*args],capture_output=True,text=True,timeout=30)
        return args,p.returncode,json.loads(p.stdout)
    directions=([0]*6,[.001]*3+[0]*3,[-.001]*3+[0]*3,[.001,-.0005,-.0005,0,0,0],[-.001,.0005,.0005,0,0,0],[0,0,0,.001,0,0],[0,0,0,0,.001,0],[0,0,0,0,0,.001],[.001,-.0003,.0002,.0004,-.0002,.0001])
    for pressure in (2e4,1e5,1e6):
        compression=math.exp(-(3*pressure/parameters[2])**parameters[3])
        for fraction in (.3,.7):
            e=compression*(parameters[4]+fraction*(parameters[6]-parameters[4]))
            for shape,stress in enumerate(([pressure]*3+[0]*3,[1.8*pressure,.6*pressure,.6*pressure,0,0,0],[.6*pressure,1.2*pressure,1.2*pressure,0,0,0],[1.5*pressure,.9*pressure,.6*pressure,.08*pressure,-.05*pressure,.03*pressure])):
                state=list(stress)+[e]
                for j,strain in enumerate(directions):
                    expected=reference_rate(state,strain,parameters)
                    args,code,result=invoke('evaluate',state,strain,parameters)
                    passed,ratio=compare(result.get('values',[]),expected,RATE_STRESS_ATOL,RATE_STATE_ATOL,RATE_RTOL)
                    cases.append(dict(id=f'rate-p{pressure}-density{fraction}-shape{shape}-D{j}',kind='cartesian-source-rate',arguments=args,expected=expected,actual=result.get('values'),max_tolerance_ratio=ratio,passed=passed and code==0 and result.get('ok') is True))
    # Oblique fixed-frame covariance, distinct from finite-spin objectivity.
    base=[150000,90000,60000,8000,-5000,3000,.7]
    deformation=[.001,-.0003,.0002,.0004,-.0002,.0001]
    base_args,base_code,base_result=invoke('evaluate',base,deformation,parameters)
    def rotate(v,Q):
        transpose=[list(row) for row in zip(*Q)]
        return mandel(multiply(multiply(Q,matrix(v)),transpose))+list(v[6:])
    for axis,angle in enumerate((.37,-.63,1.12)):
        c=math.cos(angle);t=math.sin(angle)
        Q=([[1,0,0],[0,c,-t],[0,t,c]] if axis==0 else [[c,0,t],[0,1,0],[-t,0,c]] if axis==1 else [[c,-t,0],[t,c,0],[0,0,1]])
        state=rotate(base,Q);strain=rotate(deformation,Q)
        args,code,result=invoke('evaluate',state,strain,parameters)
        expected=reference_rate(state,strain,parameters)
        source_ok,source_ratio=compare(result.get('values',[]),expected,RATE_STRESS_ATOL,RATE_STATE_ATOL,RATE_RTOL)
        covariance=rotate(base_result['values'],Q)
        cov_ok,cov_ratio=compare(result.get('values',[]),covariance,RATE_STRESS_ATOL,RATE_STATE_ATOL,RATE_RTOL)
        cases.append(dict(id=f'oblique-covariance-axis{axis}',kind='fixed-frame-covariance',arguments=args,rotation=Q,base_arguments=base_args,base_result=base_result,expected=expected,covariance_expected=covariance,actual=result.get('values'),source_tolerance_ratio=source_ratio,covariance_tolerance_ratio=cov_ratio,passed=source_ok and cov_ok and code==0 and base_code==0 and result.get('ok') is True))
    initial=[1e5]*3+[0,0,0,.7]
    histories={
        'isotropic-compression':[[.001]*3+[0]*3],
        'isotropic-unloading':[[-.001]*3+[0]*3],
        'isochoric-compression':[[.002,-.001,-.001,0,0,0]],
        'isochoric-extension':[[-.002,.001,.001,0,0,0]],
        'simple-shear':[[0,0,0,.002,0,0]],
        'mixed':[[.001,-.0003,-.0002,.0004,.0001,-.0002]],
        'reversal':[[.001,-.0005,-.0005,0,0,0],[-.001,.0005,.0005,0,0,0]],
    }
    for name,history in histories.items():
        actual=initial.copy();reference=initial.copy();segments=[];passed=True
        for strain in history:
            levels=[];previous=None;converged=False;reference_ratio=None
            for steps in (128,256,512,1024,2048,4096):
                fine=rk4(reference,strain,parameters,steps)
                if previous is not None:
                    converged,reference_ratio=compare(previous,fine,REFERENCE_STRESS_ATOL,REFERENCE_STATE_ATOL,REFERENCE_RTOL)
                levels.append(dict(steps=steps,state=fine,comparison_to_previous=reference_ratio,converged=converged))
                if converged:break
                previous=fine
            coarse=levels[-2]['state']
            args,code,result=invoke('integrate',actual,strain,parameters)
            valid,ratio=compare(result.get('state',[]),fine,PATH_STRESS_ATOL,PATH_STATE_ATOL,PATH_RTOL)
            passed=passed and converged and valid and code==0 and result.get('ok') is True
            segments.append(dict(arguments=args,reference_steps=[level['steps'] for level in levels],reference_levels=levels,reference_converged=converged,reference_tolerance_ratio=reference_ratio,coarse=coarse,expected=fine,actual=result.get('state'),max_tolerance_ratio=ratio,diagnostics=result.get('diagnostics'),passed=converged and valid and code==0 and result.get('ok') is True))
            actual=result['state'];reference=fine
        cases.append(dict(id='path-'+name,kind='independent-rk4-reference',initial=initial,strain_segments=history,segments=segments,passed=passed))
    for label,state in [('tensile',[-1e5]*3+[0,0,0,.7]),('too-dense',[1e5]*3+[0,0,0,.1]),('too-loose',[1e5]*3+[0,0,0,1.1])]:
        args,code,result=invoke('integrate',state,[.001,0,0,0,0,0],parameters)
        cases.append(dict(id='rollback-'+label,kind='invalid-initial-state',arguments=args,initial=state,result=result,passed=code!=0 and result.get('ok') is False and result.get('state')==state))
    return dict(kind='hypoplasticity-verification-report',model=MODEL,catalogue_hash=description['sha256'],parameters=parameters,
        oracle='Tension-positive Cartesian source equations transformed to atlas conventions; fixed-step RK4 histories. No DSL evaluation or shared integration method.',
        tolerances=dict(rate=dict(stress_absolute_Pa=RATE_STRESS_ATOL,state_absolute=RATE_STATE_ATOL,relative=RATE_RTOL),path=dict(stress_absolute_Pa=PATH_STRESS_ATOL,state_absolute=PATH_STATE_ATOL,relative=PATH_RTOL),rk4_convergence=dict(stress_absolute_Pa=REFERENCE_STRESS_ATOL,state_absolute=REFERENCE_STATE_ATOL,relative=REFERENCE_RTOL)),
        runtime=dict(python=platform.python_version(),platform=platform.platform(),solver_sha256=sha256(solver)),cases=cases,passed=all(c['passed'] for c in cases))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--solver',type=Path,default=ROOT/'build/atlas_solver');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=execute(args.solver.resolve());args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in report['cases'])}/{len(report['cases'])} hypoplasticity checks passed; {args.output}")
    for case in report['cases']:
        if not case['passed']:print('FAILED '+case['id'])
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
