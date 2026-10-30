"""Independent scalar/closed-form oracles for two restricted plasticity laws.

Reference calculations do not evaluate the DSL or use its nonlinear solver.
These are verification tools, not alternative production model kernels.
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

# Declared before running the comparisons. Failure cases must roll back exactly.
STRESS_ATOL=1e-4
STATE_ATOL=1e-9
REL_TOL=1e-9


def csv(values): return ','.join(format(v,'.17g') for v in values)
def mean(stress): return sum(stress[:3])/3
def deviator(stress):
    p=mean(stress)
    return [v-p if i<3 else v for i,v in enumerate(stress[:6])]
def q_value(stress): return math.sqrt(1.5*sum(v*v for v in deviator(stress)))


def dp_reference(initial,de,parameters):
    _,E,nu,M,Md,c=parameters
    K=E/(3*(1-2*nu));G=E/(2*(1+nu))
    volume=sum(de[:3]);p_trial=mean(initial)+K*volume
    s0=deviator(initial);ddev=deviator(de)
    trial=[a+2*G*b for a,b in zip(s0,ddev)]
    q_trial=math.sqrt(1.5*sum(v*v for v in trial))
    excess=q_trial-M*p_trial-c
    gamma=max(0,excess/(3*G+M*K*Md))
    q=q_trial-3*G*gamma
    if q < 0:
        if M<=0 or Md<=0: raise ValueError('No hydrostatic apex correction for this potential')
        gamma=(-c/M-p_trial)/(K*Md)
        p=-c/M;s=[0]*6;branch='apex-limit'
    else:
        p=p_trial+K*Md*gamma
        s=[v*q/q_trial for v in trial] if q_trial else [0]*6
        branch='smooth-plastic' if gamma>0 else 'elastic'
    state=[v+p if i<3 else v for i,v in enumerate(s)]
    return state+[(1+initial[6])*math.exp(-volume)-1,gamma],branch


def bisect(function,lo,hi):
    flo,fhi=function(lo),function(hi)
    if flo>0 or fhi<0: raise ValueError('Independent scalar root is not bracketed')
    for _ in range(100):
        mid=(lo+hi)/2
        if function(mid)>0: hi=mid
        else: lo=mid
    return (lo+hi)/2


def mcc_reference(initial,de,parameters,branch):
    _,M,lam,kappa,nu=parameters
    p0=mean(initial);pc0=initial[7];V=sum(de[:3]);v=(1+initial[6])*math.exp(-V)
    if branch=='isotropic-plastic':
        # q=0 => p=pc. Eliminate plastic volume and solve ONE scalar equation.
        def residual(p): return math.log(p/pc0)-(v*V-kappa*(1-p0/p))/(lam-kappa)
        p=bisect(residual,max(p0,pc0),pc0*math.exp(v*V/(lam-kappa)))
        plastic_volume=V-kappa/v*(1-p0/p)
        gamma=plastic_volume*pc0/(M*M*p)
        return [p]*3+[0,0,0,v-1,p,gamma]
    if branch=='critical-shear':
        # At p=pc/2, |q|=M*pc/2: no plastic volume, no hardening.
        return initial[:8]+[abs(de[0])/M]
    if branch!='elastic': raise ValueError('Unknown reference branch')
    p=p0/(1-v*V/kappa)
    K=v*p/kappa;G=3*K*(1-2*nu)/(2*(1+nu))
    stress=[a+2*G*b for a,b in zip(deviator(initial),deviator(de))]
    return [s+p if i<3 else s for i,s in enumerate(stress)]+[v-1,pc0,0]


def compare(actual,expected):
    if len(actual)!=len(expected) or not all(math.isfinite(x) for x in actual): return False,None
    limits=[(STRESS_ATOL if i<6 or len(expected)==9 and i==7 else STATE_ATOL)+REL_TOL*abs(x) for i,x in enumerate(expected)]
    ratios=[abs(a-b)/limit for a,b,limit in zip(actual,expected,limits)]
    return max(ratios,default=0)<=1,max(ratios,default=0)


def execute(solver,model):
    definitions=json.loads(subprocess.check_output([str(solver),'--describe'],text=True))
    local=json.loads((ROOT/'models'/(model+'.json')).read_text())
    if local!=next(m for m in definitions['models'] if m['id']==model):
        raise ValueError('Rebuild solver: embedded definition differs from current source')
    cases=[]
    parameters=[1e5,3e7,.25,1.2,.2,1e4] if model=='drucker-prager' else [1e5,1.2,.2,.04,.25]
    def invoke(initial,de,params):
        args=['--model',model,'--mode','integrate','--parameters',csv(params),'--initial',csv(initial),'--strain',csv(de)]
        process=subprocess.run([str(solver),*args],text=True,capture_output=True,timeout=30)
        result=json.loads(process.stdout)
        return args,process.returncode,result
    def case(ident,initial,de,params=None,branch=None,expected_failure=False,reference_steps=1):
        params=parameters if params is None else params
        expected,method=(initial,'exact-rollback') if expected_failure else (dp_reference(initial,de,params) if model=='drucker-prager' else (mcc_reference(initial,de,params,branch),branch))
        if reference_steps>1:
            expected=initial.copy()
            for _ in range(reference_steps):
                expected=mcc_reference(expected,[x/reference_steps for x in de],params,branch)
            method=branch+'-composed-'+str(reference_steps)+'-steps'
        args,code,result=invoke(initial,de,params)
        if expected_failure:
            passed=code!=0 and result.get('ok') is False and result.get('state')==initial;ratio=None
        else:
            passed,ratio=compare(result.get('state',[]),expected)
            passed=passed and code==0 and result.get('ok') is True
        cases.append(dict(id=ident,method=method,arguments=args,initial=initial,strain_increment=de,
            expected=expected,actual=result.get('state'),expected_failure=expected_failure,reference_steps=reference_steps,
            returncode=code,solver_ok=result.get('ok'),message=result.get('message'),diagnostics=result.get('diagnostics'),
            max_tolerance_ratio=ratio,passed=passed))
        return expected
    if model=='drucker-prager':
        initial=[1e5]*3+[0,0,0,.7,0]
        case('elastic-isotropic',initial,[.0001]*3+[0]*3)
        for sign,label in [(1,'compression'),(-1,'extension')]:
            case('elastic-'+label,initial,[sign*.001,sign*-.0005,sign*-.0005,0,0,0])
            case('plastic-'+label,initial,[sign*.01,sign*-.005,sign*-.005,0,0,0])
        for shear in range(3,6):
            de=[0]*6;de[shear]=.01
            case('plastic-shear-'+str(shear),initial,de)
        case('mixed-nonzero-initial-shear',[120000,110000,90000,1400,-600,900,.7,0],[.009,-.003,-.002,.001,.0005,-.0008])
        for Md,label in [(0,'nondilatant'),(1.2,'associated')]:
            params=parameters.copy();params[4]=Md
            case(label,initial,[.01,-.005,-.005,0,0,0],params)
        params=parameters.copy();params[3]=params[4]=0
        case('pressure-independent-j2',initial,[.002,-.001,-.001,0,0,0],params)
        plastic=case('preload-for-unloading',initial,[.01,-.005,-.005,0,0,0])
        case('unloading-resets-local-multiplier',plastic,[-.001,.0005,.0005,0,0,0])
        case('load-reversal',plastic,[-.02,.01,.01,0,0,0])
        case('hydrostatic-apex-limit',initial,[-.002]*3+[0]*3)
        case('near-apex-with-shear',initial,[-.002]*3+[.00001,0,0])
        params=parameters.copy();params[4]=0
        case('nondilatant-hydrostatic-tension-rollback',initial,[-.002]*3+[0]*3,params,expected_failure=True)
        case('inadmissible-start-rollback',[4e5,1e5,1e5,0,0,0,.7,0],[.001,0,0,0,0,0],expected_failure=True)

        # Apex branch, all shear planes and both axial deviatoric directions.
        # Reference remains the independent invariant return, not the DSL target.
        for Md in (.05,.2,1.2):
            for c in (0.,1e4):
                params=parameters.copy();params[4]=Md;params[5]=c
                for j,direction in enumerate(([1,-.5,-.5,0,0,0],[-1,.5,.5,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1],[1,-.5,-.5,.3,-.2,.1])):
                    de=[(-.002 if i<3 else 0)+1e-5*x for i,x in enumerate(direction)]
                    case(f'apex-Md{Md}-c{c}-direction{j}',initial,de,params)
                # Approach the smooth/apex junction from each side, including it.
                K=params[1]/(3*(1-2*params[2]));G=params[1]/(2*(1+params[2]))
                q_boundary=3*G*(-c/params[3]-(mean(initial)-.006*K))/(K*Md)
                for factor in (.9,1.,1.1):
                    de=[-.002]*3+[factor*q_boundary/(math.sqrt(1.5)*2*G),0,0]
                    case(f'apex-junction-Md{Md}-c{c}-factor{factor}',initial,de,params)

    else:
        initial=[1e5]*3+[0,0,0,.7,2e5,0]
        for V,label in [(.003,'compression'),(-.003,'unloading')]:
            case('elastic-isotropic-'+label,initial,[V/3]*3+[0]*3,branch='elastic')
        for shear in range(3,6):
            de=[0]*6;de[shear]=.0005
            case('elastic-shear-'+str(shear),initial,de,branch='elastic')
        case('elastic-mixed',initial,[.0003,-.0001,.0002,.0002,-.0001,.00015],branch='elastic')
        normal=initial.copy();normal[7]=1e5
        for V in (.001,.003,.009):
            case('normally-consolidated-volume-'+str(V),normal,[V/3]*3+[0]*3,branch='isotropic-plastic')
        case('overconsolidated-yield-crossing',initial,[.01]*3+[0]*3,branch='isotropic-plastic')
        case('overconsolidated-two-half-step-reference',initial,[.01]*3+[0]*3,branch='isotropic-plastic',reference_steps=2)
        for sign,label in [(1,'compression'),(-1,'extension')]:
            pc=2e5;p=pc/2;q=sign*parameters[1]*pc/2
            critical=[p+2*q/3,p-q/3,p-q/3,0,0,0,.7,pc,0]
            case('critical-state-'+label,critical,[sign*.001,sign*-.0005,sign*-.0005,0,0,0],branch='critical-shear')
        loaded=case('preload-for-unloading',normal,[.001]*3+[0]*3,branch='isotropic-plastic')
        case('elastic-unloading-keeps-pc',loaded,[-.0005]*3+[0]*3,branch='elastic')
        case('invalid-tensile-start',[-1e5]*3+[0,0,0,.7,2e5,0],[0]*6,expected_failure=True)
        case('outside-yield-start',[3e5]*3+[0,0,0,.7,2e5,0],[0]*6,expected_failure=True)
        bad=parameters.copy();bad[2]=bad[3]
        case('invalid-compression-indices',initial,[0]*6,bad,expected_failure=True)
        # Continuum isotropic solutions use v=v0 exp(-V), not the step residuals.
        for branch,V,start,denominator in [('elastic',.003,initial,parameters[3]),('plastic',.03,normal,parameters[2])]:
            v0=1+start[6];v=v0*math.exp(-V)
            exact=mean(start)*math.exp((v0-v)/denominator)
            levels=[]
            for n in (8,16,32,64):
                state=start.copy();failures=[]
                for step in range(n):
                    args,code,result=invoke(state,[V/(3*n)]*3+[0]*3,parameters)
                    if code or not result.get('ok'):
                        failures.append(dict(step=step,arguments=args,result=result,returncode=code));break
                    state=result['state']
                error=abs(mean(state)-exact)/exact
                levels.append(dict(steps=n,final_state=state,relative_pressure_error=error,failed_steps=failures))
            errors=[level['relative_pressure_error'] for level in levels]
            orders=[math.log(a/b,2) if a>0 and b>0 else None for a,b in zip(errors,errors[1:])]
            passed=not any(level['failed_steps'] for level in levels) and all(order is not None and order>.8 for order in orders) and errors[-1]<5e-4
            cases.append(dict(id='continuum-'+branch+'-refinement',method='independent-continuum-isotropic-solution',initial=start,
                total_volumetric_strain=V,expected_pressure=exact,levels=levels,observed_orders=orders,
                acceptance=dict(minimum_order=.8,maximum_final_relative_error=5e-4),passed=passed))
    return dict(kind='plasticity-verification-report',model=model,catalogue_hash=definitions['sha256'],
        oracle='Closed-form radial return and scalar invariant reductions; no DSL evaluation or shared nonlinear solve.',
        tolerances=dict(stress_absolute_Pa=STRESS_ATOL,other_state_absolute=STATE_ATOL,relative=REL_TOL),
        runtime=dict(python=platform.python_version(),platform=platform.platform(),solver_sha256=sha256(solver)),
        cases=cases,passed=all(c['passed'] for c in cases))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=['drucker-prager','modified-cam-clay'],required=True)
    parser.add_argument('--solver',type=Path,default=ROOT/'build/atlas_solver')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=execute(args.solver.resolve(),args.model)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in report['cases'])}/{len(report['cases'])} {args.model} verification cases passed; {args.output}")
    for case in report['cases']:
        if not case['passed']: print('FAILED '+case['id'])
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__':main()
