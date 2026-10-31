"""Analytical Original Cam-clay ingestion diagnostics; no general material update."""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = 2e-12
ABS = 2e-12


def finite(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + ' must be a finite real number, excluding bool')
    return float(value)


def parameters(M=1.2, lam=.2, kap=.04, Gamma=2.5, p_ref=1000.):
    values = dict(M=M, lam=lam, kap=kap, Gamma=Gamma, p_ref=p_ref)
    values = {key:finite(key,value) for key,value in values.items()}
    if not (values['M'] > 0 and values['lam'] > values['kap'] > 0 and values['p_ref'] > 0):
        raise ValueError('require M,p_ref>0 and lambda>kappa>0')
    return values


def yield_f(p, q, pc, M):
    p,q,pc,M = [finite(k,v) for k,v in zip(['p','q','pc','M'],[p,q,pc,M])]
    if min(p,pc,M) <= 0:
        raise ValueError('positive pressure/pc/M required')
    # Difference of logs prevents an otherwise avoidable ratio overflow/underflow.
    result=abs(q)+M*p*(math.log(p)-math.log(pc))
    if not math.isfinite(result):
        raise ValueError('nonrepresentable yield value')
    return result


def virgin_undrained(eps_s, p0=100000., **kwargs):
    """Source6.30-6.31 conventional monotone compression only, arbitrary fixture inputs."""
    P = parameters(**kwargs)
    eps_s, p0 = finite('eps_s',eps_s), finite('p0',p0)
    if eps_s < 0 or p0 <= 0:
        raise ValueError('nonnegative compression distortion and positive p0 required')
    M,lam,kap,Gamma,pref = [P[k] for k in ['M','lam','kap','Gamma','p_ref']]
    v0 = Gamma+lam-kap-lam*(math.log(p0)-math.log(pref))
    if not math.isfinite(v0) or v0 <= 0:
        raise ValueError('positive finite initial specific volume required')
    L = 1-kap/lam
    A = M*v0/(kap*L)
    if not math.isfinite(A) or not math.isfinite(A*eps_s):
        raise ValueError('nonrepresentable decay argument')
    decay = math.exp(-A*eps_s)
    # p0*exp(L*(decay-1)) is equivalent to source pu*exp(L*decay).
    p = p0*math.exp(L*math.expm1(-A*eps_s))
    q = M*p*(-math.expm1(-A*eps_s))
    wk = v0+kap*(math.log(p)-math.log(pref))
    logpc = math.log(pref)+1+(Gamma-wk)/(lam-kap)
    try:
        pc = math.exp(logpc)
    except OverflowError as exc:
        raise ValueError('pc overflow') from exc
    pdot = -p*L*A*decay
    Evp = -kap*pdot/(v0*p)
    values = dict(eps_s=eps_s,p=p,q=q,v=v0,w_kappa=wk,p_c=pc,p_prime=pdot,
                  plastic_volumetric_rate=Evp,source_flow_rhs=M-q/p,
                  dissipation=p*Evp+q,expected_dissipation=M*p)
    if not all(math.isfinite(x) for x in values.values()) or min(p,pc) <= 0:
        raise ValueError('nonrepresentable final analytical state')
    return values


def verify_source(source):
    expected=json.loads((HERE/'source-receipt.json').read_text())['source']['sha256']
    if hashlib.sha256(Path(source).read_bytes()).hexdigest() != expected:
        raise ValueError('private source hash mismatch')
    return expected


def diagnostics(source=None):
    rows=[]
    def check(name, passed, details):
        if not passed:
            raise AssertionError(name)
        rows.append(dict(name=name,passed=True,details=details))
    if source is not None:
        check('source-hash',bool(verify_source(source)),verify_source(source))
    P=parameters(); M,lam,kap,Gamma,pref=[P[k] for k in ['M','lam','kap','Gamma','p_ref']]
    trajectory=[]
    for eps in [0.,1e-12,1e-6,.001,.01,.05,.2,1.]:
        x=virgin_undrained(eps);trajectory.append(x)
        scale=max(1.,abs(x['q']),M*x['p'])
        f=yield_f(x['p'],x['q'],x['p_c'],M)
        check('undrained-yield:'+str(eps),abs(f)<=REL*scale,{'residual_Pa':f,'scale_Pa':scale})
        check('undrained-flow:'+str(eps),math.isclose(x['plastic_volumetric_rate'],x['source_flow_rhs'],rel_tol=REL,abs_tol=ABS),x)
        check('undrained-dissipation:'+str(eps),math.isclose(x['dissipation'],x['expected_dissipation'],rel_tol=REL,abs_tol=ABS),{'value':x['dissipation'],'expected':x['expected_dissipation']})
    # Exact repeated recovery path returns v and packing, including an interior q change.
    v,p=2.,50000.
    start=v; wk0=v+kap*math.log(p/pref)
    for pnew in [30000.,90000.,45000.,50000.]:
        v-=kap*math.log(pnew/p);p=pnew
        check('kappa-packing:'+str(p),math.isclose(v+kap*math.log(p/pref),wk0,rel_tol=REL,abs_tol=ABS),{'v':v,'w_kappa':v+kap*math.log(p/pref)})
    check('kappa-cycle',math.isclose(v,start,rel_tol=0.,abs_tol=ABS),{'v_start':start,'v_end':v})
    # Unit reference transform preserves all actual volumes and derived critical pressures.
    new_ref=1.; new_Gamma=Gamma-lam*math.log(new_ref/pref)
    oldv=Gamma-lam*math.log(70000./pref)
    newv=new_Gamma-lam*math.log(70000./new_ref)
    check('reference-pressure-transform',math.isclose(oldv,newv,rel_tol=0.,abs_tol=ABS),{'old_ref_Pa':pref,'new_ref_Pa':new_ref,'old_Gamma':Gamma,'new_Gamma':new_Gamma,'old_v':oldv,'new_v':newv})
    # Two mirrored smooth yield branches; central finite differences at fixed pc.
    for sign in [-1.,1.]:
        p=60000.;eta=.7;pc=p*math.exp(eta/M);q=sign*eta*p
        fp=M*(math.log(p/pc)+1);fq=sign
        step=.1
        nump=(yield_f(p+step,q,pc,M)-yield_f(p-step,q,pc,M))/(2*step)
        numq=(yield_f(p,q+step,pc,M)-yield_f(p,q-step,pc,M))/(2*step)
        check('signed-smooth-gradient:'+str(sign),math.isclose(nump,fp,rel_tol=0.,abs_tol=3e-8) and math.isclose(numq,fq,rel_tol=0.,abs_tol=3e-8),{'analytic':[fp,fq],'finite_difference':[nump,numq],'step_Pa':step,'absolute_tolerance':3e-8})
        check('signed-flow-dissipation:'+str(sign),math.isclose(p*(M-abs(q)/p)+q*sign,M*p,rel_tol=REL,abs_tol=ABS),{'q':q,'source_dilatancy':M-abs(q)/p})
    # Cartesian axisymmetric work identity and actual nonnegative invariant q*.
    for axial,radial,dl,dr in [(150000.,60000.,.01,-.002),(60000.,150000.,-.002,.01)]:
        p=(axial+2*radial)/3;q=axial-radial
        Ev=dl+2*dr;Es=2*(dl-dr)/3
        cart=axial*dl+2*radial*dr;scalar=p*Ev+q*Es
        qstar=math.sqrt(((axial-radial)**2+(radial-radial)**2+(radial-axial)**2)/2)
        check('axisymmetric-work:'+str(q),math.isclose(cart,scalar,rel_tol=REL,abs_tol=ABS) and qstar==abs(q),{'Cartesian_work_Pa':cart,'scalar_work_Pa':scalar,'q_signed_Pa':q,'q_invariant_Pa':qstar})
    # Original hydrostatic vertex at pc; critical pressure is pc/e, not MCC pc/2.
    pc=100000.;px=pc/math.e
    check('OCC-vertex-and-critical',yield_f(pc,0.,pc,M)==0. and abs(yield_f(px,M*px,pc,M))<=REL*M*px,{'isotropic_intercept_Pa':pc,'OCC_critical_Pa':px,'MCC_ellipse_critical_Pa':pc/2,'same_critical_pressure':False})
    for vals in [(True,0.,1.,1.),(math.nan,0.,1.,1.),(0.,0.,1.,1.),(1.,0.,-1.,1.)]:
        try:yield_f(*vals)
        except ValueError:continue
        raise AssertionError('invalid scalar accepted')
    check('invalid-inputs-rejected',True,{'cases':4,'categories':['bool','nonfinite','zero pressure','negative pc']})
    return {'version':'occ-analytical-ingestion-0.1','model_id':'original-cam-clay','source_fidelity':'electronic transcription; original print edition not authenticated','compiled_calls':0,'general_constitutive_evaluator':False,'acceptance':{'algebra_relative':REL,'algebra_absolute':ABS,'finite_difference_gradient_absolute':3e-8},'fixture_parameters':P,'source_checks':rows,'virgin_undrained_trajectory':trajectory,'passed':True}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.write_text(json.dumps(diagnostics(a.source),indent=2,allow_nan=False)+'\n')
