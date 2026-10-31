"""Bounded independent equation/domain witnesses, not a material-point implementation."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA = '43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9'
TOL = 1e-12  # Set before observing floating kernel witnesses; no numerical admission gate.

def root(x):
    assert x >= 0
    n,d = math.isqrt(x.numerator), math.isqrt(x.denominator)
    assert n*n == x.numerator and d*d == x.denominator
    return F(n,d)

def equivalent(p, Q, A, m):
    if p <= 0 or Q <= 0:
        raise ValueError('compressive magnitudes must be positive')
    if m == 0:
        base = Q+A*(p-Q)
        if base <= 0: raise ValueError('nonpositive real-power base')
        return base
    assert m == F(1,2)
    base = root(Q)+A*(root(p)-root(Q))
    if base <= 0: raise ValueError('nonpositive real-power base before squaring')
    return base*base

def soft(Q, delta, m, K=F(2), pref=F(100)):
    # Exact selected-exponent witnesses, not a general integration algorithm.
    if m == 0:
        base = Q-K*pref*delta
        if base <= 0: raise ValueError('exhausted softening domain')
        return base
    assert m == F(1,2)
    base = root(Q)-K*root(pref)*delta/2
    if base <= 0: raise ValueError('exhausted softening domain before squaring')
    return base*base

def kernel(r, length):
    if length <= 0 or r < 0: raise ValueError('invalid distance/length')
    return r/length**2*math.exp(-(r/length)**2)

def average(values, weights, volumes):
    if any(x < 0 for x in weights) or any(x <= 0 for x in volumes):
        raise ValueError('invalid neighbourhood weights/volumes')
    den = sum(w*v for w,v in zip(weights,volumes))
    if den <= 0: raise ValueError('empty effective neighbourhood; no local fallback')
    return sum(x*w*v for x,w,v in zip(values,weights,volumes))/den

def rejects(fn):
    try: fn()
    except ValueError: return
    raise AssertionError('expected domain rejection')

def run():
    checks=[]
    for m in [F(0),F(1,2)]:
        assert equivalent(F(100),F(100),F(1,2),m)==100
        assert equivalent(F(25),F(100),F(0),m)==100
        assert equivalent(F(25),F(100),F(1),m)==25
        assert equivalent(F(100),F(400),F(1,2),m)==4*equivalent(F(25),F(100),F(1,2),m)
    rejects(lambda: equivalent(F(25),F(100),F(3),F(1,2)))
    checks.append(dict(id='equivalent-pressure-endpoints-homogeneity-domain',status='pass',
                       rejected_half_power_inner_base='-5',limitation='m=1 requires a separate limiting definition'))
    p,Q,M,tcs,te,A=F(60),F(100),F(3,5),F(4,5),F(2,5),F(1,2)
    qe=equivalent(p,Q,A,F(0));tau=p*tcs
    assert p*p/(Q*Q)+tau*tau/(M*M*Q*Q)==1
    Bpositive=tau/qe;c=Bpositive*(1-te/tcs)
    assert tau-p*te-c*qe==0
    assert Bpositive==F(3,5) and tau/(-qe)==-Bpositive
    assert ((-p)*tcs)/(-qe)==Bpositive
    checks.append(dict(id='cap-CSL-Hvorslev-intersection-and-C5-sign',status='pass_with_retained_source_failure',
                       p=str(p),qe=str(qe),tau=str(tau),C5_first_ratio=str(tau/(-qe)),C5_second_ratio=str(Bpositive),
                       limitation='No implicit correction of the printed signed equality'))
    # Differentiate the explicit m=0 and m=1/2 forms independently.
    for m in [F(0),F(1,2)]:
        p,Q,A,te,c=F(25),F(100),F(1,2),F(2,5),F(1,10)
        qe=equivalent(p,Q,A,m)
        dqdp=A if m==0 else A*root(qe)/root(p)
        source_factor=F(1) if m==0 else root(qe/p)
        assert te+c*dqdp==te+c*A*source_factor
        # df/dSN is positive because SN=-p and f=tau-p*te-c*qe.
        assert te+c*dqdp>0
        assert -((te+c*dqdp))<0  # compression-positive normal derivative
    checks.append(dict(id='B28-normal-gradient-sign-conversion',status='pass',witnesses=2,
                       limitation='B30/B32 are frozen-state algorithmic partials; no full consistent tangent'))
    Q=F(100);peak=F(1,10);current=F(11,100);h=F(3)
    assert soft(Q,h*(peak-peak),F(0))==Q
    qstar=soft(Q,h*(current-peak),F(0));assert qstar==94
    assert soft(Q,h*(current-peak),F(0))==qstar
    wrong_repeated=soft(qstar,h*(current-peak),F(0));assert wrong_repeated==88
    candidate=F(105,1000)-peak;old=current-peak
    retained=max(candidate,old);assert soft(Q,h*retained,F(0))==94
    rejects(lambda:soft(Q,F(11,10),F(1,2)))
    checks.append(dict(id='derived-soft-cap-peak-hold-monotone-domain',status='pass',
                       derived_from_hard_cap=str(qstar),incorrect_reapplication=str(wrong_repeated),
                       limitation='Required history semantics witness, not source runtime verification'))
    w=[F(1,3),F(1,6)];hv=[F(1,100),F(3,100)];h=F(6)
    damage=sum(x*y for x,y in zip(hv,w));local=[h*damage*y for y in w]
    redistributed=sum(x*y for x,y in zip(local,w))
    assert damage==F(1,120) and redistributed==F(1,144)
    assert redistributed/damage==h*sum(y*y for y in w)==F(5,6)
    signed=(F(1,100)-F(1,50))*w[0];positive_cone=F(1,100)*w[0]
    assert signed==F(-1,300) and positive_cone==F(1,300)
    checks.append(dict(id='plane-redistribution-and-damage-definition-distinction',status='pass_with_retained_source_ambiguity',
                       h_sum_weights_squared=str(redistributed/damage),literal_Eq146_increment=str(signed),D_positive_cone_increment=str(positive_cone),
                       limitation='Synthetic weights; no renormalization or conservation identity assumed'))
    l=1.;weights=[kernel(0,l),kernel(1,l),kernel(1,l)]
    assert weights[0]==0 and weights[1]>0 and kernel(2,l)>0
    out=average([1e9,2.,6.],weights,[1.,1.,3.]);assert abs(out-5)<TOL
    assert abs(average([7.]*3,weights,[1.,1.,3.])-7)<TOL
    assert abs(average([1e9,2.,6.],[x*19 for x in weights],[100.,100.,300.])-out)<TOL
    rejects(lambda:average([1.],[kernel(0,l)],[1.]))
    rejects(lambda:kernel(0,0))
    checks.append(dict(id='spatial-normalization-self-exclusion-and-empty-neighbourhood',status='pass',
                       weighted_average=out,kernel_at_2l=kernel(2,l),
                       limitation='Radius2l truncation is a separate support policy; a lone self point cannot supply Eq147'))
    # Two sites, each with only the other site in its positive-weight neighbourhood.
    committed=[F(1),F(3)];held=[committed[1],committed[0]]
    trial=[committed[0]+2,committed[1]+4]
    assert held==[F(3),F(1)] and trial==[F(3),F(7)]
    next_step=[trial[1],trial[0]];assert next_step==[F(7),F(3)] and next_step!=held
    peak_zero=F(0);has_reached=True
    assert has_reached and peak_zero==0 and not (peak_zero>=F(1,10**12))
    checks.append(dict(id='lagged-step-and-zero-peak-sentinel-witness',status='pass_with_retained_source_gap',
                       held_damage=list(map(str,held)),next_committed_step_damage=list(map(str,next_step)),
                       limitation='Explicit activation is distinguishable from peak value; printed numeric sentinel cannot represent all zero-peak events'))
    return {'scope':'Seven bounded independent groups; retained source failures/gaps remain open.',
            'source_sha256':SOURCE_SHA,'floating_absolute_tolerance':TOL,'checks':checks,
            'executable_model':False,'scientific_admission':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
    if a.source:assert hashlib.sha256(a.source.read_bytes()).hexdigest()==SOURCE_SHA
    result=json.dumps(run(),indent=2)+'\n'
    if a.output:a.output.write_text(result)
    else:print(result,end='')
