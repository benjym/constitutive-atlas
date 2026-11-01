#!/usr/bin/env python3
"""Independent original-1997 fixed-coaxial interior-Lode reference; no Atlas import."""
import math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
S=math.sqrt(2/3); M=.05

def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def transpose(a):return list(map(list,zip(*a)))
def direction(cos3):
    a,b,c=.37,.51,.23
    rz=[[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]
    ry=[[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]]
    rx=[[1,0,0],[0,math.cos(c),-math.sin(c)],[0,math.sin(c),math.cos(c)]]
    q=mm(mm(rz,ry),rx);theta=math.acos(cos3)/3
    eig=[S*math.cos(theta+2*k*math.pi/3) for k in range(3)]
    mat=mm(mm(q,[[eig[i] if i==j else 0 for j in range(3)] for i in range(3)]),transpose(q))
    n=[mat[0][0],mat[1][1],mat[2][2],math.sqrt(2)*mat[0][1],math.sqrt(2)*mat[1][2],math.sqrt(2)*mat[0][2]]
    n3=mm(mm(mat,mat),mat)
    observed=math.sqrt(6)*sum(n3[i][i] for i in range(3))
    assert abs(sum(n[:3]))<1e-12 and abs(sum(x*x for x in n)-1)<1e-12
    assert abs(observed-cos3)<1e-12 and min(abs(x) for x in n)>1e-8
    return {'cos3theta':cos3,'observed_cos3theta':observed,'theta_rad':theta,'n_mandel':n,'rotation':q,'eigenvalues':eig}
def g(c,cos3):return 2*c/((1+c)-(1-c)*cos3)
def rhs(y,e0,cs):
    p,beta,x=y
    assert p>0
    psi=e0-(.8-.025*math.log(p/160))
    bb=S*(g(1,cs)*1.14+g(2/3.975,cs)*3.975*max(-psi,0)-M)
    bd=S*(g(1,cs)*1.14+g(.07/4.2,cs)*4.2*psi-M)
    b=bb-beta; bref=2*S*(1.14+3.975*max(-psi,0)-M)
    assert bref>abs(b)
    h=1200*abs(b)/(bref-abs(b))
    D=2.64*(bd-beta)
    if psi>0 and D<0:D=0
    G=31400*(p/100)**.6;K=G
    L=2*G/(p*h*b+2*G-K*D*x)
    assert L>=0 and math.isfinite(L)
    pd=-K*D*L;betad=L*h*b
    # Independent source stress-amplitude derivative from s'=2G(1-L)n.
    xd=(2*G*(1-L)-pd*x)/p
    return [pd,betad,xd]
def rk4(y,h,e,cs):
    a=rhs(y,e,cs);b=rhs([v+h*w/2 for v,w in zip(y,a)],e,cs)
    c=rhs([v+h*w/2 for v,w in zip(y,b)],e,cs);d=rhs([v+h*w for v,w in zip(y,c)],e,cs)
    return [v+h*(aa+2*bb+2*cc+dd)/6 for v,aa,bb,cc,dd in zip(y,a,b,c,d)]
def snap(t,y,e,n):
    p,beta,x=y
    return {'t':t,'p_Pa':p*1000,'beta':beta,'x':x,'e':e,'strain':[t*v for v in n],
     'sigma_Pa':[(p*(1 if i<3 else 0)+p*x*v)*1000 for i,v in enumerate(n)],'alpha':[beta*v for v in n]}
def solve(e,cs,step,n):
    y=[160.,0.,S*M];t=0.;rows=[snap(t,y,e,n)];drift=0.
    for goal in [.0005,.001,.002,.005,.01]:
      count=math.ceil((goal-t)/step);h=(goal-t)/count
      for _ in range(count):
        y=rk4(y,h,e,cs);t+=h;drift=max(drift,abs(y[2]-y[1]-S*M))
      t=goal;rows.append(snap(t,y,e,n))
    assert drift<=2e-5
    return {'checkpoints':rows,'max_yield_drift':drift}
def main():
    r={'identity':'md1997-independent-interior-lode-reference-v1','cases':{},'failures':[]}
    for e in [.65,.85]:
     for cs in [0.,.5,-.5]:
      name=f"{'dense' if e==.65 else 'loose'}-cos3theta-{cs:+g}"
      try:
       di=direction(cs);n=di['n_mandel'];coarse=solve(e,cs,2e-6,n);fine=solve(e,cs,1e-6,n)
       errors={'stress_Pa':0.,'alpha':0.,'e':0.}
       for a,b in zip(coarse['checkpoints'],fine['checkpoints']):
        for aa,bb in zip(a['sigma_Pa'],b['sigma_Pa']):
         error=abs(aa-bb);errors['stress_Pa']=max(errors['stress_Pa'],error)
         assert error<=5+2e-5*max(1000,abs(bb))
        for aa,bb in zip(a['alpha'],b['alpha']):
         error=abs(aa-bb);errors['alpha']=max(errors['alpha'],error);assert error<=2e-6
        assert abs(a['e']-b['e'])<=2e-7
       r['cases'][name]={'e0':e,**di,'g_M':g(1,cs),'g_kb':g(2/3.975,cs),'g_kd':g(.07/4.2,cs),'refinement_errors':errors,**fine}
      except Exception as ex:r['failures'].append({'case':name,'error':repr(ex)})
    r['passed']=len(r['cases'])==6 and not r['failures']
    (P/'reference-results.json').write_text(json.dumps(r,indent=2)+'\n')
    req={'identity':'md1997-interior-lode-source-targets-v1','policy':'POLICY.md','cases':[{'name':name,**case} for name,case in r['cases'].items()]}
    (P/'requests.json').write_text(json.dumps(req,indent=2)+'\n')
    manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'}
    (P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'passed':r['passed'],'cases':len(r['cases']),'failures':r['failures'],'max_stress_refinement_Pa':max((c['refinement_errors']['stress_Pa'] for c in r['cases'].values()),default=None)},indent=2))
if __name__=='__main__':main()
