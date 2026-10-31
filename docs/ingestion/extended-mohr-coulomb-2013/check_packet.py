"""Bounded EMC source/algebra diagnostics; no constitutive solver or author code.
Run with --write only when intentionally freezing a new packet; normal run replays.
"""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

def checks():
    results=[]
    def add(name,loc,inputs,outputs,meaning):
        results.append(dict(id=name,source_locator=loc,inputs=inputs,outputs=outputs,interpretation=meaning))
    # Engineering shear and Mandel are dual transports, not the same six-vector.
    G,nu=4000000.,.25
    strain=[.001,-.002,.003,.004,-.005,.006] # xx yy zz xy yz xz engineering
    lam=2*G*nu/(1-2*nu)
    stress=[2*G*x+lam*sum(strain[:3]) for x in strain[:3]]+[G*x for x in strain[3:]]
    engwork=sum(x*y for x,y in zip(stress,strain))
    stressM=stress[:3]+[math.sqrt(2)*x for x in stress[3:]]
    strainM=strain[:3]+[x/math.sqrt(2) for x in strain[3:]]
    mandelwork=sum(x*y for x,y in zip(stressM,strainM))
    assert math.isclose(engwork,mandelwork,rel_tol=1e-15)
    add('engineering-Mandel-work','Eqs1-3 p662',dict(G=G,mu=nu,strain_engineering_named_order='xx yy zz xy yz xz',strain=strain),dict(stress=stress,engineering_work=engwork,mandel_work=mandelwork),'Independent linear elasticity and work mapping; Appendix shear permutation must be handled by names.')
    peak,initial,beta=math.radians(30),math.radians(1),.005
    alpha=initial/(peak-initial)
    def phi(eps):
        z=eps/beta+alpha
        return peak*z/(1+z)
    def eps(angle):
        return beta*(angle/(peak-angle)-alpha)
    x=.007
    angle=phi(x)
    h=1e-7
    fd=(phi(x+h)-phi(x-h))/(2*h)
    exact=(peak-angle)**2/(beta*peak)
    assert abs(eps(angle)-x)<1e-17
    assert math.isclose(fd,exact,rel_tol=1e-9)
    assert math.isclose(phi(0),initial,rel_tol=1e-15)
    assert math.isclose(phi(beta)/peak,(1+alpha)/(2+alpha),rel_tol=1e-15)
    add('hardening-inverse-and-derivative','Eqs12-15 p664',dict(peak=peak,initial=initial,beta=beta,plastic_scalar=x),dict(phi=angle,inverse=eps(angle),derivative=exact,centered_difference=fd,half_condition_ratio=phi(beta)/peak),'Rational hardening identity and derivative; no finite-path material integration claimed.')
    values=[phi(x) for x in [0.,.005,.05,.5]]
    assert all(initial<=v<peak for v in values) and values==sorted(values)
    add('hardening-asymptote','Eqs12/15 p664',dict(plastic_scalar=[0.,.005,.05,.5]),dict(phi=values,gaps=[peak-v for v in values]),'Monotone asymptotic peak for beta>0; exact peak remains a separate singular endpoint in Eq12.')
    s=[-.2,.05,.15]
    J=math.sqrt(sum(v*v for v in s)/2)
    D=math.prod(s)
    literal=-3*math.sqrt(3)*D/(2*J)
    homogeneous=-3*math.sqrt(3)*D/(2*J**3)
    literal_scaled=-3*math.sqrt(3)*(1000*D)/(2*10*J)
    assert math.isclose(literal_scaled,100*literal,rel_tol=1e-15)
    assert abs(literal)<1 and abs(literal_scaled)>1 and abs(homogeneous)<1
    add('printed-Lode-dimensions','Eqs20-21 p671',dict(deviator=s,scale=10.),dict(J=J,determinant=D,printed_argument=literal,printed_scaled_argument=literal_scaled,derived_dimensionless_argument=homogeneous),'The printed denominator2J changes the argument by scale squared. Cubic denominator shown only as diagnostic alternative, not admitted source correction.')
    s=[-1.,0.,1.]
    J2=sum(v*v for v in s)/2
    cof=[s[1]*s[2],s[0]*s[2],s[0]*s[1]]
    printed=[v/(2*J2)+1/3 for v in cof]
    determinant_gradient=[v+J2/3 for v in cof]
    assert math.isclose(sum(printed),.5) and abs(sum(determinant_gradient))<1e-15
    add('printed-third-basis-hydrostatic-defect','Eq26c p672 vs Eq21 p671',dict(deviator=s),dict(printed_diagonal=printed,printed_hydrostatic_directional_derivative=sum(printed),independent_det_dev_gradient=determinant_gradient,correct_hydrostatic_derivative=sum(determinant_gradient)),'det(dev(sigma)) cannot change under a hydrostatic stress shift; the printed vector does.')
    theta,J,fy,fc=.1,2.,math.radians(10),math.radians(35)
    printed=-J*(math.sin(theta)+math.cos(theta)*math.sin(fy)/math.sqrt(3))
    derived=-J*(math.sin(theta)+math.cos(theta)*math.sin(fc)/math.sqrt(3))
    def K(t,f):return math.cos(t)-math.sin(t)*math.sin(f)/math.sqrt(3)
    fd=J*(K(theta+1e-6,fc)-K(theta-1e-6,fc))/(2e-6)
    assert math.isclose(fd,derived,rel_tol=1e-9) and abs(printed-derived)>.4
    add('potential-angle-conflict','Eq41 p672 vs Eq11 p664',dict(theta=theta,J=J,phi_y=fy,phi_cv=fc),dict(printed_phi_y_value=printed,derived_phi_cv_value=derived,finite_difference_JK_cv=fd),'Printed potential theta derivative uses a different angle from the potential and adjacent instruction.')
    # Corrected-invariant diagnostic, independently equivalent to principal face values.
    phi_y=math.radians(30)
    samples=[]
    for principal in ([3.,2.,1.],[3.,1.,1.],[3.,3.,1.]):
        mean=sum(principal)/3
        dev=[-v+mean for v in principal] # source compression-negative
        j=math.sqrt(sum(v*v for v in dev)/2)
        arg=-3*math.sqrt(3)*math.prod(dev)/(2*j**3)
        assert abs(arg)<=1+1e-14
        # Exact repeated-principal fixtures have known Lode endpoints.
        # asin near +/-1 loses angle accuracy; this is not an epsilon material branch.
        if principal[0]==principal[1]:t=-math.pi/6
        elif principal[1]==principal[2]:t=math.pi/6
        else:t=math.asin(arg)/3
        invariant=-mean*math.sin(phi_y)+j*K(t,phi_y)
        face=.5*((max(principal)-min(principal))-(max(principal)+min(principal))*math.sin(phi_y))
        assert abs(invariant-face)<2e-15
        samples.append(dict(principal_compression_positive=principal,raw_invariant_argument=arg,theta_source=t,invariant_value=invariant,principal_face_value=face))
    add('face-and-edge-value-diagnostic','Eqs4-5/18-21 pp663/671',dict(phi_y=phi_y),dict(samples=samples),'Cubic-denominator diagnostic matches independent principal face criterion, both repeated-principal edges. This is a criterion identity only, not a full EMC model or edge return.')
    tt=math.radians(25)
    def rounded(t,f):
        sign=1 if t>0 else -1
        A=math.cos(tt)/3*(3+math.tan(tt)*math.tan(3*tt)+sign/math.sqrt(3)*(math.tan(3*tt)-3*math.tan(tt))*math.sin(f))
        B=(sign*math.sin(tt)+math.sin(f)*math.cos(tt)/math.sqrt(3))/(3*math.cos(3*tt))
        return A-B*math.sin(3*t),-3*B*math.cos(3*t)
    at=[]
    for sign in [-1,1]:
        t=sign*tt
        ka,dka=rounded(t,phi_y)
        dk=-math.sin(t)-math.cos(t)*math.sin(phi_y)/math.sqrt(3)
        assert abs(ka-K(t,phi_y))<5e-16 and abs(dka-dk)<5e-16
        at.append(dict(theta=t,K=K(t,phi_y),Ka=ka,derivative_exact=dk,derivative_round=dka))
    t=math.radians(29)
    ka,_=rounded(t,phi_y)
    c1_exact=math.sin(phi_y)
    c1_source=ka/K(t,phi_y)*math.sin(phi_y)
    assert abs(c1_exact-c1_source)>1e-4
    add('rounding-threshold-and-hydrostatic-normal','Eqs33-38 p672',dict(theta_t=tt,phi_y=phi_y,interior_corner_theta=t),dict(threshold_checks=at,C1_exact=c1_exact,C1_source_rescaled=c1_source),'Rounded Ka is C1 at threshold, but rescaled C1 outside differs from actual hydrostatic derivative of exact yield value.')
    # A full Cartesian diagnostic using mathematically differentiated invariant potential.
    # Diagonal source sigma(-3,-2,-1) has p=-2,J=1,theta=0.
    fc=math.radians(20)
    qp=.5-math.sin(fc)
    qtheta=-math.sin(fc)/math.sqrt(3)
    gradJ=[-.5,0.,.5]
    gradtheta=[-math.sqrt(3)/6,math.sqrt(3)/3,-math.sqrt(3)/6]
    flow=[qp/3+g+qtheta*t for g,t in zip(gradJ,gradtheta)]
    meanflow=sum(flow)/3
    normscalar=math.sqrt(2*sum((v-meanflow)**2 for v in flow))
    workscalar=-flow[0]+flow[2] # s:flow/J, J=1
    assert math.isclose(workscalar,1.,rel_tol=1e-15)
    assert normscalar>workscalar+.01
    add('nonradial-shear-scalar-distinction','Eqs8-11 pp663-664; Eq51 p672',dict(source_sigma=[-3.,-2.,-1.],phi_cv=fc,Lambda=1.),dict(derived_diagonal_potential_flow=flow,work_conjugate_scalar=workscalar,positive_norm_scalar_Eq9=normscalar),'Even the dimensionally consistent differentiated potential has nonradial deviatoric flow. Work scalar Lambda*Q_J and Euclidean norm differ; accumulator semantics require a declared source decision.')
    assert len(results)==9
    return dict(schema_version='0.1',kind='independent-bounded-source-diagnostics',groups=len(results),all_passed=True,scope='Algebra and inconsistency witnesses only. No full constitutive integration, production DSL, author code, native or Wasm checks.',development_failure='Initial repeated-principal value witness used asin of a rounded endpoint argument and failed the 2e-15 value-identity gate. Exact endpoint angles are now supplied only for analytically repeated-principal fixtures; no tolerance change or material continuation.',checks=results)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=checks(); data=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.write:(HERE/'check-results.json').write_text(data)
    else:assert (HERE/'check-results.json').read_text()==data,'retained diagnostics differ'
    print(f"{result['groups']} bounded diagnostic groups pass; retained results match")
