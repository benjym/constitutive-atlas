"""Independent scalar diagnostics only; no production DSL, kernel or author code.

Run from any directory: python3 /absolute/path/check_packet.py
Outputs stable JSON to stdout; does not mutate retained evidence.
"""
import json, math
from decimal import Decimal, localcontext

def close(a,b,tol=2e-12):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)

def evaluate():
    checks=[]
    N=.772; lam=.06; nt=-.01; tr=25.; temp=60.; p=200000.; pr=1000.
    theta=math.log(temp/tr)
    n=N+nt*theta
    eT=math.expm1(n-lam*math.log(p/pr))
    close(N+nt*math.log(tr/tr),N)
    close(math.expm1(N-lam*math.log(p/pr)),math.exp(N-lam*math.log(p/pr))-1)
    checks.append({'id':'reference-ncl-and-pressure-unit','passed':True,'eT_60_coordinate_C':eT,'p_over_pr':p/pr})
    celsius=math.log(60/20); kelvin=math.log(333.15/293.15)
    assert abs(celsius-kelvin)>.9
    checks.append({'id':'temperature-zero-point-witness','passed':True,'log_C_ratio':celsius,'log_K_ratio':kelvin,'delta_N_for_nT_minus_point009_C':-.009*celsius,'delta_N_same_parameter_K':-.009*kelvin,'claim':'Calibration changes under affine temperature conversion; no preferred interpretation selected.'})
    pSBS=120000.; po=pSBS; kap=.002
    nstar=n-(lam-kap)*math.log(po/pSBS)
    close(nstar,n)
    checks.append({'id':'anisotropic-equation-isotropic-reduction','passed':True})
    # At the anchor p=po, O is on NCL; Eq5 shifts TSL below O on heating.
    ct=.5; logvO=n-lam*math.log(p/pr); logvOp=logvO+ct*nt*theta
    assert logvOp<logvO
    close(logvOp-logvO,ct*nt*theta)
    checks.append({'id':'anchor-tsl-gap','passed':True,'log_specific_volume_gap':logvOp-logvO,'qualification':'Uses declared NCL anchor reading, not an established anchor-update algorithm.'})
    gamma=.1
    def fu(x):return max(x,0.)**gamma
    close(fu(-1),0);close(fu(0),0);close(fu(1),1)
    assert 0<fu(.5)<1 and fu(2)>1
    checks.append({'id':'collapse-factor-no-upper-clip','passed':True,'eta_half':fu(.5),'eta_two':fu(2)})
    # Algebraically exact rather than floating-point cancellation: T=Tr, p=po.
    with localcontext() as ctx:
        ctx.prec=60
        logv=Decimal('.772')-Decimal('.06')*(Decimal(200).ln())
        logv_star=logv+Decimal('.5')*Decimal('-.01')*(Decimal(1).ln())
        numerator=logv.exp()-logv_star.exp();denominator=numerator
        assert numerator==denominator==0
    checks.append({'id':'reference-nc-zero-over-zero','passed':True,'numerator':'0','denominator':'0','continuation_selected':False})
    # d(fu)/deta=gamma*eta^(gamma-1); does not approach finite derivative.
    ds=[gamma*x**(gamma-1) for x in [1e-3,1e-6,1e-12]]
    assert ds[0]<ds[1]<ds[2]
    checks.append({'id':'threshold-tangent-divergence','passed':True,'one_sided_derivatives':ds,'claim':'No zero/threshold AD tangent chosen.'})
    # Independently differentiate Eq1 along an arbitrary positive temperature coordinate.
    lt=.001; tt=50.; rr=25.; lamb=lam+lt*math.log(tt/rr); nn=N+nt*math.log(tt/rr)
    v=math.exp(nn-lamb*math.log(p/pr)); deriv=v*(nt-lt*math.log(p/pr))/tt
    def vfun(x):return math.exp(N+nt*math.log(x/rr)-(lam+lt*math.log(x/rr))*math.log(p/pr))
    eps=1e-3;fd=(vfun(tt+eps)-vfun(tt-eps))/(2*eps);close(deriv,fd,1e-11)
    checks.append({'id':'ncl-temperature-derivative','passed':True,'analytic_dv_dT':deriv,'central_difference':fd})
    alpha=3.5e-5; dtemp=35.;e0=.6
    epsv_TE=-alpha*dtemp
    # Integrated host Eq8 for pure reversible thermal strain: mechanical difference0.
    e_correct=e0
    e_wrong=(1+e0)*math.exp(-epsv_TE)-1
    assert e_wrong>e_correct
    checks.append({'id':'reversible-thermal-void-correction','passed':True,'compression_positive_total_volumetric_strain':epsv_TE,'e_correct':e_correct,'isothermal_transport_incorrect_e':e_wrong,'qualification':'Kinematic identity, not a full constrained host-model solution.'})
    return {'schema_version':'0.1','kind':'independent-bounded-ingestion-diagnostics','task_id':'ING-hypoplastic-thermal-ma-2017','groups':len(checks),'passed':True,'compiled_execution':False,'full_model_verified':False,'checks':checks}
if __name__=='__main__':print(json.dumps(evaluate(),indent=2,allow_nan=False))
