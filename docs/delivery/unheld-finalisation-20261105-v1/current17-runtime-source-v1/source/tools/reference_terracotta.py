"""Generate auditable Terracotta references with pinned, unmodified author RHS.

SciPy/NumPy are optional research dependencies, never runtime dependencies.
Read docs/models/terracotta-2024-transcription.md before interpreting the results.
"""
import argparse,hashlib,importlib.util,json,platform
from pathlib import Path

SOURCE_SHA256='6f1d7bbc9e805cfa38230b1277a1b55a02f27ab4581e973f5a61c495262a0711'
SOURCE_URL='https://raw.githubusercontent.com/MaxWiebicke/Terracotta-pq/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_functions.py'

def generate(source):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SOURCE_SHA256:raise ValueError('author source hash mismatch')
    import numpy as np
    import scipy
    from scipy.integrate import solve_ivp
    spec=importlib.util.spec_from_file_location('pinned_terracotta',source);author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
    p=dict(K=13e6,G=5e6,omega=.6,M=.73,p1=.543e6,Lambda=10,eta=150,alpha=6e5,gamma=6e5,beta=0,Gamma=1)
    ev,es=author.initialElasticStrains([100,0],.423,p)
    initial=np.array([0,0,100,0,ev,es,0,0,0,.423],dtype=float)
    # Each reference stage has constant prescribed rates, avoiding the known
    # mixed-control temperature discrepancy and outer acceleration approximation.
    histories=[('txu-low', [('txu',2e-5,1000),('relaxation',0,100)]),
               ('txu-rate-jump',[('txu',2e-5,10),('txu',2e-4,10),('relaxation',0,10)]),
               ('txu-extension',[('txu',-2e-5,100)]),
               ('isotropic',[('iso',2e-5,100)]),('oedometer',[('oed',2e-5,100)])]
    atol=[1e-13,1e-13,1e-10,1e-10,1e-13,1e-13,1e-14,1e-10,1e-10,1e-13]
    def run(stages,method,rtol):
        z=initial.copy();points=[];time=0;work=0
        for index,(kind,rate,duration) in enumerate(stages):
            D=author.testControl(rate,kind)
            # Algebraic one-sided outputs at rate boundaries, not an acceleration
            # ramp spread over an arbitrary author outer interval.
            z[7:9]=2*np.array([p['alpha'],p['gamma']])*z[6]*D/p['Gamma']
            times=np.linspace(duration/4,duration,4)
            sol=solve_ivp(author.stateVarRatesComplexLoading,(0,duration),z,method=method,rtol=rtol,atol=atol,t_eval=times,args=(p,kind,D,duration,rate,0))
            if not sol.success:raise RuntimeError(sol.message)
            work+=sol.nfev
            for t,y in zip(sol.t,sol.y.T):
                pe=y[9]**6*(p['K']*y[4]**2+3*p['G']*y[5]**2)/2
                qe=3*p['G']*y[9]**6*y[4]*y[5]
                if max(abs(pe-y[2]),abs(qe-y[3]))>1e-5:raise AssertionError('reference elastic stress drift')
                pressure=1000*(y[2]+y[7]+y[6]**2/p['Gamma']);q=1000*(y[3]+y[8])
                points.append(dict(time=float(time+t),segment=index,state=[float(y[i]) for i in [4,5,6,9]],pressure=float(pressure),signed_q=float(q)))
            z=sol.y[:,-1];time+=duration
        return points,work
    cases=[]
    for name,stages in histories:
        points,work=run(stages,'DOP853',1e-11);check,other_work=run(stages,'BDF',1e-10)
        stress_difference=max(abs(a[k]-b[k]) for a,b in zip(points,check) for k in ['pressure','signed_q'])
        if stress_difference>.01:raise AssertionError('reference method disagreement exceeds .01 Pa')
        cases.append(dict(id=name,stages=[dict(kind=k,rate=rate,duration=d) for k,rate,d in stages],points=points,nfev=work,bdf_nfev=other_work,maximum_reference_stress_difference_Pa=stress_difference))
    return dict(kind='author-rhs-reference',source_url=SOURCE_URL,source_sha256=SOURCE_SHA256,
                source_license='MIT (author repository LICENSE)',python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                parameter_units='author kPa convention, output pressure/stress converted to Pa',parameters=p,
                method='DOP853',relative_tolerance=1e-11,absolute_tolerances=atol,crosscheck_method='BDF',crosscheck_relative_tolerance=1e-10,
                boundary_policy='reset viscous stresses algebraically; dStrainPrev equals prescribed stage rate; no mixed-control author routine',
                interpretation='Author RHS numerical comparison with explicit boundary adaptation; not reproduction of integratePath defaults, independent equation review, or experimental validation.',cases=cases)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--author-functions',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    data=generate(args.author_functions);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(f"Saved {len(data['cases'])} source-pinned histories to {args.output}")
if __name__=='__main__':main()
