#!/usr/bin/env python3
"""Original-1997 scalar axisymmetric reference. No Atlas dependencies.
Stress units kPa internally. Run from any directory; outputs alongside script.
"""
import math, json, hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
SQ=math.sqrt(2/3)
G0=K0=31400.; PAT=100.; AEXP=.6; M=1.14; H0=1200.; M0=.05; AD=2.64

def mod(p): return G0*(p/PAT)**AEXP

def yield_point(z,kind):
    p0=160.; g=mod(p0)
    if kind=='undrained': return abs(M0*p0/(3*g)),[p0,z*M0*p0,0.,0.,-z*abs(M0*p0/(3*g))/2]
    p=3*p0/(3-z*M0)
    axial=4*PAT**AEXP/(3*K0*(1-AEXP))*(p**(1-AEXP)-p0**(1-AEXP))
    return abs(axial),[p,3*(p-p0),0.,0.,-axial/8]

def rhs(y,z,kind,e0):
    p,q,alpha,e,rad=y
    if p<=0: raise ValueError('nonpositive pressure')
    psi=e-(.8-.025*math.log(p/160))
    B=M+(3.975 if z==1 else 2.)*max(-psi,0)-M0
    Di=M+(4.2 if z==1 else .07)*psi-M0
    b=SQ*(B-z*alpha); bref=2*SQ*(M+3.975*max(-psi,0)-M0)
    if bref<=abs(b): raise ValueError('bref distance violated')
    h=H0*abs(b)/(bref-abs(b)); D=AD*SQ*(Di-z*alpha)
    if psi>0 and D<0: D=0.
    C=h*(z*B-alpha); g=mod(p); k=g; eta=q/p
    if kind=='undrained':
        L=(3*g*z)/(math.sqrt(6)*g*z-eta*k*D+p*C)
        pd=-k*L*D; qd=3*g*z-math.sqrt(6)*g*z*L
        rd=-z/2; vd=0
    else:
        # sigma_rad fixed -> q'=3p'; axial strain compatibility closes L.
        T=p*C/(3-eta)
        L=z/(T*(1/(3*k)+1/g)+z*SQ+D/3)
        pd=T*L; qd=3*pd
        rd=pd/(3*k)-qd/(6*g)+L*(-z/math.sqrt(6)+D/3)
        vd=z+2*rd
    if L < -1e-14: raise ValueError('negative monotonic multiplier')
    return [pd,qd,L*C,-(1+e0)*vd,rd]

def rk4(y,h,z,kind,e0):
    a=rhs(y,z,kind,e0)
    b=rhs([v+h*w/2 for v,w in zip(y,a)],z,kind,e0)
    c=rhs([v+h*w/2 for v,w in zip(y,b)],z,kind,e0)
    d=rhs([v+h*w for v,w in zip(y,c)],z,kind,e0)
    return [v+h*(aa+2*bb+2*cc+dd)/6 for v,aa,bb,cc,dd in zip(y,a,b,c,d)]

def state(t,y,z):
    p,q,alpha,e,rad=y
    return {'axial_strain':z*t,'radial_strain':rad,'p_Pa':p*1000,'q_Pa':q*1000,
      'sigma_Pa':[(p+2*q/3)*1000,(p-q/3)*1000,(p-q/3)*1000,0,0,0],
      'alpha':[2*alpha/3,-alpha/3,-alpha/3,0,0,0],'alpha_scalar':alpha,'e':e,
      'strain':[z*t,rad,rad,0,0,0]}

def solve(z,kind,e0,step):
    ty,y=yield_point(z,kind)
    # Integrate source fixed-e0 infinitesimal void ratio relation during elastic leg.
    y[3]=e0-(1+e0)*(z*ty+2*y[4])
    rows=[state(0,[160,0,0,e0,0],z),state(ty,y,z)]
    maxdrift=0.; t=ty
    for goal in [.0005,.001,.002,.005,.01,.02]:
        n=math.ceil((goal-t)/step); h=(goal-t)/n
        for _ in range(n):
            y=rk4(y,h,z,kind,e0); t+=h
            maxdrift=max(maxdrift,abs(y[1]/y[0]-y[2]-z*M0))
        t=goal; rows.append(state(t,y,z))
    return {'first_yield_abs_axial':ty,'checkpoints':rows,'max_yield_drift':maxdrift}

def main():
    report={'identity':'md1997-source-scalar-reference-v1','units':'Pa serialized; kPa calculation', 'cases':{},'failures':[]}
    for e0 in [.65,.85]:
      for kind in ['undrained','drained']:
       for z in [1,-1]:
        name=f"{kind}-{'dense' if e0==.65 else 'loose'}-{'compression' if z==1 else 'extension'}"
        try:
          coarse=solve(z,kind,e0,2e-6); fine=solve(z,kind,e0,1e-6)
          errors={'stress_Pa':0.,'alpha':0.,'e':0.,'radial_strain':0.}
          for c,f in zip(coarse['checkpoints'],fine['checkpoints']):
            for x,y in zip(c['sigma_Pa'],f['sigma_Pa']):
              err=abs(x-y); errors['stress_Pa']=max(errors['stress_Pa'],err)
              assert err <= 5+2e-5*max(1000,abs(y)),(name,'stress',err)
            for key,tol in [('alpha_scalar',2e-6),('e',2e-7),('radial_strain',2e-7)]:
              err=abs(c[key]-f[key]); ek='alpha' if key=='alpha_scalar' else key
              errors[ek]=max(errors[ek],err); assert err<=tol,(name,key,err)
          assert fine['max_yield_drift']<=2e-5,(name,'yield drift',fine['max_yield_drift'])
          report['cases'][name]={'e0':e0,'protocol':kind,'axial_sign':z,'max_refinement_errors':errors,**fine}
        except Exception as ex: report['failures'].append({'case':name,'error':str(ex)})
    # Analytic hydrostatic powers and an elastic undrained quarter-yield cycle.
    hydro=[]
    for ev in [-.001,.001]:
      p=(160**(1-AEXP)+(1-AEXP)*K0/PAT**AEXP*ev)**(1/(1-AEXP))
      pn=160.
      h=ev/1000
      for _ in range(1000):
        a=mod(pn); b=mod(pn+h*a/2); c=mod(pn+h*b/2); d=mod(pn+h*c)
        pn+=h*(a+2*b+2*c+d)/6
      assert abs(pn-p)<1e-9
      hydro.append({'volumetric_strain':ev,'p_Pa':p*1000,'e':.65-1.65*ev,'rk4_error_Pa':abs(pn-p)*1000})
    peak=M0*160/(12*mod(160)); qcycle=0.
    for de in [peak,-peak]:
      qcycle+=3*mod(160)*de
      assert abs(qcycle/160)<M0
    assert qcycle==0.
    report['analytic']={'elastic_cycle_evaluated_return_q_Pa':qcycle*1000,'hydrostatic':hydro,'elastic_cycle':{'axial_peak':M0*160/(12*mod(160)),'q_peak_Pa':M0*160*1000/4,'return_sigma_Pa':[160000]*3+[0]*3,'return_alpha':[0]*6,'return_e':.65}}
    report['passed']=len(report['cases'])==8 and not report['failures']
    (P/'reference-results.json').write_text(json.dumps(report,indent=2)+'\n')
    manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'}
    (P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'cases':len(report['cases']),'failures':report['failures'],'max_stress_refinement_Pa':max((c['max_refinement_errors']['stress_Pa'] for c in report['cases'].values()),default=None)},indent=2))
if __name__=='__main__':main()
