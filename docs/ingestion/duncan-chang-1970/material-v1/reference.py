"""Independent source Eq15 compliance reference. Standard library only; no Atlas imports.
Decimal eigenanalysis acts on exact stored Mandel values. Decimal trig Taylor series,
Jacobi plane rotations and compliance differ from production stiffness/spectral code.
"""
from decimal import Decimal as Q, localcontext
import json, math, struct, hashlib
from pathlib import Path
B=Path(__file__).resolve().parent

def q(x):return Q.from_float(x) if isinstance(x,float) else Q(x)
def sin(x):
    term=x;total=x;k=1
    while True:
        term *= -x*x/q((2*k)*(2*k+1));old=total;total+=term
        if total==old:return total
        k+=1

def cos(x):
    term=Q(1);total=term;k=1
    while True:
        term *= -x*x/q((2*k-1)*(2*k));old=total;total+=term
        if total==old:return total
        k+=1

def eigen(v):
    a=[[q(v[i]) if i==j else Q(0) for j in range(3)] for i in range(3)]
    for i,j,k in [(0,1,3),(1,2,4),(0,2,5)]:a[i][j]=a[j][i]=q(v[k])/Q(2).sqrt()
    # Stable high precision symmetric Jacobi, stopping below requested arithmetic accuracy.
    for _ in range(150):
        i,j=max([(0,1),(0,2),(1,2)],key=lambda ij:abs(a[ij[0]][ij[1]]))
        if abs(a[i][j])<Q(10)**(-(__import__('decimal').getcontext().prec-15))*max(Q(1),*(abs(a[k][k]) for k in range(3))):break
        tau=(a[j][j]-a[i][i])/(2*a[i][j]);t=(1 if tau>=0 else -1)/(abs(tau)+(1+tau*tau).sqrt());c=1/(1+t*t).sqrt();s=t*c
        off=a[i][j];ai=a[i][i];aj=a[j][j];a[i][i]=ai-t*off;a[j][j]=aj+t*off;a[i][j]=a[j][i]=Q(0)
        for k in range(3):
            if k in (i,j):continue
            x=a[k][i];y=a[k][j];a[k][i]=a[i][k]=c*x-s*y;a[k][j]=a[j][k]=s*x+c*y
    else:raise ArithmeticError('Jacobi did not converge')
    return sorted(a[k][k] for k in range(3))

def quantities(current,previous,p):
    e=eigen(current[:6]);en=eigen(previous[:6]);D=e[-1]-e[0];Dn=en[-1]-en[0];c=(e[0]+en[0])/2
    sp=sin(q(p['phi']));cp=cos(q(p['phi']))
    F=2*(q(p['c_cohesion'])*cp+c*sp)/(1-sp);S=(D+Dn)/(2*F)
    if D<q(previous[6]):E=q(p['Kur'])*q(p['pa'])*(c/q(p['pa']))**q(p['n']);branch='unload_reload'
    elif S<1:E=q(p['K'])*q(p['pa'])*(c/q(p['pa']))**q(p['n'])*(1-q(p['Rf'])*S)**2;branch='primary'
    else:E=q(p['E_failure']);branch='postfailure'
    return D,E,branch,S

def compliance(current,previous,p):
    D,E,branch,S=quantities(current,previous,p);ds=[q(x)-q(y) for x,y in zip(current[:6],previous[:6])];nu=q(p['nu'])
    eps=[(ds[i]-nu*sum(ds[j] for j in range(3) if j!=i))/E for i in range(3)]+[(1+nu)*x/E for x in ds[3:]]
    return eps, max(q(previous[6]),D),branch,S,E

def residual(current,previous,de,p):
    eps,h,branch,S,E=compliance(current,previous,p)
    # Convert compliance defect to stress-coordinate residual using explicit Cartesian
    # Hooke inverse (already independently rationally established in source packet).
    defect=[q(x)-y for x,y in zip(de,eps)];nu=q(p['nu']);lam=E*nu/((1+nu)*(1-2*nu));mu2=E/(1+nu)
    tr=sum(defect[:3]);return [-mu2*x-(lam*tr if i<3 else 0) for i,x in enumerate(defect)]+[q(current[6])-h]

def history(stress,h=0):
    with localcontext() as c:
        c.prec=160; e=eigen(stress);D=e[-1]-e[0];x=float(max(q(h),D))
        if q(x)<D:x=math.nextafter(x,math.inf)
    return list(map(float,stress))+[x]

def bits(v):return struct.pack('>d',float(v)).hex()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    model=json.loads((B/'candidate.json').read_text());dense={k:v['default'] for k,v in model['parameters'].items()};loose=dense|{'K':295.,'Kur':1090.,'n':.65,'Rf':.90,'phi':30.4*math.pi/180}
    cases=[]
    def add(name,zn,z,p,kind='endpoint'):
        refs=[]
        for precision in (100,160):
            with localcontext() as c:
                c.prec=precision;eps,h,branch,S,E=compliance(z,zn,p);refs.append((eps,h,branch,S,E))
        convergence=max([abs(x-y) for x,y in zip(refs[0][0],refs[1][0])]+[abs(refs[0][1]-refs[1][1])/Q(100000)])
        assert convergence<Q('1e-70'),(name,convergence)
        de=list(map(float,refs[-1][0]));z=list(z);z[6]=float(refs[-1][1]);
        # h need only be a reference endpoint; exact source history retained separately.
        with localcontext() as c:
            c.prec=160;r=residual(z,zn,de,p)
        cases.append(dict(id=name,kind=kind,parameters=p,initial=zn,target=z,de=de,branch=refs[-1][2],Sbar=str(refs[-1][3]),modulus=str(refs[-1][4]),reference_convergence=str(convergence),exact_history=str(refs[-1][1]),history_encoding_error=str(q(z[6])-refs[-1][1]),wire_residual=[str(x) for x in r],wire={k:[bits(x) for x in v] for k,v in {'initial':zn,'target':z,'de':de,'parameters':list(p.values())}.items()}))
    for label,p in [('dense',dense),('loose',loose)]:
        zn=history([100000]*3+[0]*3)
        for i,a in enumerate([150000,200000,250000,200000,150000,200000,250000,275000]):
            z=history([a,100000,100000,0,0,0],zn[6]);add(f'{label}-history-{i}',zn,z,p);zn=z
        # Retain mixed change, then explicit fixed-D confinement transitions.
        z=history([175000,125000,125000,0,0,0],zn[6]);add(f'{label}-mixed-confinement',zn,z,p)
        zn=history([150000,100000,100000,0,0,0],175000.)
        for c in [125000,75000]:
            z=history([c+50000,c,c,0,0,0],zn[6]);add(f'{label}-confinement-{c}',zn,z,p);zn=z
        for name,s in [('hydro',[125000]*3+[0]*3),('extension',[100000,150000,150000,0,0,0]),('distinct',[180000,140000,100000,16000,-9000,12000]),('six',[160000,110000,130000,-8000,11000,17000])]:
            z=history(s);add(f'{label}-{name}',history([100000]*3+[0]*3),z,p)
        # signed coordinate swaps preserve exact Mandel representation.
        s=[180000.,140000.,100000.,16000.,-9000.,12000.]
        add(f'{label}-signed-permutation',history([100000]*3+[0]*3),history([s[1],s[0],s[2],-s[3],s[5],-s[4]]),p)
        # Exact stored equality and neighboring history branches, independent source predictions.
        for name,h in [('below',math.nextafter(50000.,-math.inf)),('equal',50000.),('above',math.nextafter(50000.,math.inf))]:
            add(f'{label}-history-equality-{name}',history([120000,100000,100000,0,0,0],h),history([150000,100000,100000,0,0,0],h),p)
        # Cohesion isolates exact strength equality without transcendental rounding.
        cohesive=p|{'c_cohesion':100000.,'phi':0.}
        for name,d in [('below',math.nextafter(320000.,-math.inf)),('equal',320000.),('above',math.nextafter(320000.,math.inf))]:
            add(f'{label}-strength-equality-{name}',history([280000,100000,100000,0,0,0]),history([d,100000,100000,0,0,0]),cohesive)
        with localcontext() as c:
            c.prec=160
            sp=sin(q(p['phi']));F=2*Q(100000)*sp/(1-sp)
        for coefficient in (1.,10.,100.):
            pp=p|{'E_failure':coefficient*(4.4482216152605/.3048**2)}
            for factor in (.99,1.,1.01):
                # For c=0 fixedconfinement, averaged D=F*factor up to binary rounding.
                d0=float(F)*.9;d1=float(F)*(2*factor-.9)
                zn=history([100000+d0,100000,100000,0,0,0]);z=history([100000+d1,100000,100000,0,0,0],zn[6]);add(f'{label}-failure-{coefficient}-{factor}',zn,z,pp)
        # Explicit identity holds on all major branches (including virgin).
        for name,D,h in [('virgin',0.,0.),('memory',25000.,75000.),('primary',50000.,50000.),('failed',float(F)*1.1,float(F)*1.1)]:
            z=history([100000+D,100000,100000,0,0,0],h);add(f'{label}-hold-{name}',z,z,p,'hold')
    # Smooth residual Jacobian verification: source-coordinate central differences at
    # four frozen scales; base/current/previous/control all exact binary values.
    derivatives=[]
    for branch,h in [('primary',20000.),('unload_reload',200000.)]:
        current=history([180000,140000,100000,16000,-9000,12000],h);previous=history([150000,120000,100000,4000,3000,-2000],h)
        with localcontext() as c:
            c.prec=160;de=list(map(float,compliance(current,previous,dense)[0]))
            rows=[]
            for exponent in (12,16,20,24):
                columns=[]
                for j in range(20): # current7, previous7, strain6
                    cc=list(current);nn=list(previous);dd=list(de);pp=dict(dense);scale=100000. if j<14 else (1. if j<20 else max(abs(list(pp.values())[j-20]),1.))
                    step=q(2)**(-exponent)*q(scale);plus=[list(map(q,cc)),list(map(q,nn)),list(map(q,dd))];minus=[x[:] for x in plus];block=0 if j<7 else 1 if j<14 else 2;idx=j if j<7 else j-7 if j<14 else j-14;plus[block][idx]+=step;minus[block][idx]-=step
                    rp=residual(*plus,pp);rm=residual(*minus,pp);columns.append([str((x-y)/(2*step)*q(scale)/Q(100000)) for x,y in zip(rp,rm)])
                rows.append(dict(exponent=exponent,columns=columns))
            derivatives.append(dict(id=branch,current=current,previous=previous,de=de,parameters=dense,sweeps=rows))
    return dict(identity='duncan-material-reference-v1',candidate_sha256=sha(B/'candidate.json'),method='independent Decimal Eq15 compliance and Cartesian Jacobi; exact stored binary input',cases=cases,derivatives=derivatives)
if __name__=='__main__':
    out=build();(B/'references.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cases':len(out['cases']),'derivative_states':len(out['derivatives']),'sha256':sha(B/'references.json')}))
