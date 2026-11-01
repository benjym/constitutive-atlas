"""Independent pre-build tensor/energy/analytical identities (no Atlas imports)."""
import json,math
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
rng=np.random.default_rng(20261101)
def mat(v):
    a,b,c,d,e,f=v;return np.array([[a,d/2**.5,f/2**.5],[d/2**.5,b,e/2**.5],[f/2**.5,e/2**.5,c]])
def dev(a):return a-np.trace(a)*np.eye(3)/3
checks=0
for _ in range(100):
    K,g,h,tau=10**rng.uniform(3,9,4);e=mat(rng.normal(size=6)*.001);q=dev(mat(rng.normal(size=6)*1e3));D=mat(rng.normal(size=6)*.001)
    ed=dev(e);qd=2*h*dev(D)-q/tau;stress=K*np.trace(e)*np.eye(3)+2*g*ed+q
    # psi = bulk + equilibrium spring + Maxwell spring energies.
    psi_dot=K*np.trace(e)*np.trace(D)+2*g*np.sum(ed*dev(D))+np.sum(q*qd)/(2*h)
    loss=np.sum(stress*D)-psi_dot;expected=np.sum(q*q)/(2*h*tau)
    assert abs(loss-expected)<=1e-8*max(1,abs(loss),abs(expected));assert expected>=0
    rot,_=np.linalg.qr(rng.normal(size=(3,3)))
    er=rot@e@rot.T;qr=rot@q@rot.T
    sr=K*np.trace(er)*np.eye(3)+2*g*dev(er)+qr
    np.testing.assert_allclose(sr,rot@stress@rot.T,rtol=1e-11,atol=1e-6)
    dvec=rng.normal(size=6);assert abs(np.sum(mat(dvec)**2)-np.dot(dvec,dvec))<1e-12
    # Closed-form constant-rate derivative is the ODE at both endpoints.
    t=.7*tau;decay=math.exp(-t/tau);qt=q*decay+2*h*tau*(1-decay)*dev(D)
    qt_dot=-q*decay/tau+2*h*decay*dev(D)
    np.testing.assert_allclose(qt_dot,2*h*dev(D)-qt/tau,rtol=1e-10,atol=1e-6)
    checks+=4
result=dict(passed=True,seed=20261101,independent_identity_checks=checks,scope=['energy/dissipation','tensor rotation','Mandel contraction','analytic solution derivative'],compiled_calls=0)
(BASE/'reference-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
