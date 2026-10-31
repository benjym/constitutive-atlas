"""Independent Cartesian AppendixC/Eq40 oracle; no Atlas imports or integration."""
import math

SOURCE_SHA256='8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3'
SOURCE_PARAMETERS=('phi_c','lambda_star','kappa_star','N','r')
POLICY={'stress_relative_to_scale':2e-12,'stress_absolute_floor_Pa':1e-10,'void_relative_to_scale':2e-13,'void_absolute_floor':1e-15,'nonisotropic_certified_corpus_j2_min':1e-8,'raw_lode_allowance':64*math.ulp(1.),'j2_support_floor':1e-100}


def scalar(x):
    if type(x) not in (int,float) or not math.isfinite(x):raise ValueError('finite numeric input required; bools rejected')
    return float(x)


def matrix(a):
    if not isinstance(a,(list,tuple)) or len(a)!=3 or any(not isinstance(row,(list,tuple)) or len(row)!=3 for row in a):raise ValueError('3x3 required')
    a=[[scalar(x) for x in row]for row in a]
    if any(a[i][j]!=a[j][i]for i in range(3)for j in range(3)):raise ValueError('exact symmetry required')
    return a


def det(a):
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])


def trace(a):return math.fsum(a[i][i]for i in range(3))
def dot(a,b):return math.fsum(a[i][j]*b[i][j]for i in range(3)for j in range(3))
def mul(a,b):return [[math.fsum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def norm(a):return math.sqrt(dot(a,a))

def from_mandel(v):
    if len(v)!=6:raise ValueError('six values required')
    x,y,z,u,v,w=map(scalar,v);q=math.sqrt(2)
    return [[x,u/q,w/q],[u/q,y,v/q],[w/q,v/q,z]]


def to_mandel(a):return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]


def rotate(a,R):
    # One symmetric Cartesian tensor constructed; no independent lower-triangle roundoff.
    b=[[0.]*3 for _ in range(3)]
    for i in range(3):
        for j in range(i,3):
            b[i][j]=b[j][i]=math.fsum(R[i][k]*a[k][l]*R[j][l]for k in range(3)for l in range(3))
    return b


def rate(stress,stretching,e,*,phi_c,lambda_star,kappa_star,N,r):
    sigma,E=matrix(stress),matrix(stretching)
    e,phi,lam,kap,N,r=map(scalar,(e,phi_c,lambda_star,kappa_star,N,r))
    if not (e>=0 and .01<=phi<=1.4 and .0001<=lam<=1 and .00001<=kap<lam and lam<=1 and -10<=N<=10 and .01<=r<=10):raise ValueError('outside declared research support')
    try:return _rate(sigma,E,e,phi,lam,kap,N,r)
    except (ArithmeticError,ValueError) as exc:raise ValueError('undefined or nonrepresentable source rate: '+str(exc))from exc


def _rate(sigma,E,e,phi,lam,kap,N,r):
    p=trace(sigma)/3
    if p<=0:raise ValueError('positive mean stress required')
    s=[[v/p for v in row]for row in sigma]
    if not(s[0][0]>0 and s[0][0]*s[1][1]-s[0][1]**2>0 and det(s)>0):raise ValueError('strict SPD compression required')
    exact_sphere=(sigma[0][0]==sigma[1][1]==sigma[2][2] and all(sigma[i][j]==0 for i in range(3)for j in range(3)if i!=j))
    T=[[-x for x in row]for row in s]
    I1=trace(T);I2=(dot(T,T)-I1*I1)/2;I3=det(T)
    H=[[x/trace(sigma)for x in row]for row in sigma]
    # Direct Cartesian source route; cancellation near sphere is NOT certified.
    Hdev=[[H[i][j]-(1/3 if i==j else 0)for j in range(3)]for i in range(3)]
    j2=dot(Hdev,Hdev)
    a=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi));Q=3+a*a
    alpha=math.log((lam-kap)/(lam+kap)*Q/(a*math.sqrt(3)))/math.log(2)
    Delta=Q-2**alpha*a*math.sqrt(3);c1=2*Delta/(9*r);c2=1+(1-c1)*3/a**2
    if not(alpha>0 and Delta>0 and c1>0 and c1+c2*a*a*dot(H,H)>0):raise ValueError('coefficient/stiffness support failed')
    Yi=math.sqrt(3)*a/Q
    if exact_sphere:
        j2=0.;Y=Yi;F=1.;raw_lode=0.;m=[[-a/Q if i==j else 0. for j in range(3)]for i in range(3)]
    else:
        if j2<1e-100:raise ValueError('nonzero deviator below project j2 support floor')
        raw_lode=-math.sqrt(6)*trace(mul(mul(Hdev,Hdev),Hdev))/j2**1.5
        if abs(raw_lode)>1+64*math.ulp(1):raise ValueError('raw Lode outside supported roundoff margin')
        Y=(Yi-1)*(I1*I2+9*I3)*math.cos(phi)**2/(8*I3*math.sin(phi)**2)+Yi
        tanpsi=math.sqrt(3*j2)
        F=math.sqrt(tanpsi*tanpsi/8+(2-tanpsi*tanpsi)/(2+math.sqrt(2)*tanpsi*raw_lode))-tanpsi/(2*math.sqrt(2))
        hnorm=dot(H,H)
        m=[[-a/F*(H[i][j]+Hdev[i][j]-H[i][j]/3*(6*hnorm-1)/((F/a)**2+hnorm))for j in range(3)]for i in range(3)]
    if not(F>0 and Y>0 and norm(m)>0):raise ValueError('flow support failed')
    unit=[[x/norm(m)for x in row]for row in m]
    # Explicit Cartesian fourth-order stiffness, separate from DSL tensor action.
    L=[[[[3*(c1*((1 if i==k and j==l else 0)+(1 if i==l and j==k else 0))/2+c2*a*a*H[i][j]*H[k][l])for l in range(3)]for k in range(3)]for j in range(3)]for i in range(3)]
    def act(X):return [[math.fsum(L[i][j][k][l]*X[k][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)]
    pe=1000*math.exp((N-math.log1p(e))/lam);fd=(2*p/pe)**alpha;fs=3*p/(lam*Delta)
    if not(pe>0 and fd>0 and fs>0):raise ValueError('positive representable density/stiffness required')
    A,B=act(E),act(unit)
    result=[[fs*(A[i][j]+fd*Y*B[i][j]*norm(E))for j in range(3)]for i in range(3)]
    er=-(1+e)*trace(E)
    diagnostic=dict(p=p,a=a,alpha=alpha,Delta=Delta,c1=c1,c2=c2,Y=Y,F=F,fd=fd,fs=fs,j2=j2,raw_lode=raw_lode,exact_sphere=exact_sphere)
    if any(not math.isfinite(x)for x in to_mandel(result)+[er]+[v for v in diagnostic.values()if type(v)is float]):raise ValueError('nonfinite output/intermediate')
    if norm(result)>1000*1e250 or abs(er)>1e250:raise ValueError('output outside numeric research bound')
    return dict(stress_rate=result,e_rate=er,diagnostics=diagnostic)


def cases():
    base=dict(phi_c=math.radians(22.6),lambda_star=.11,kappa_star=.016,N=1.375,r=.4)
    rows=[]
    def add(name,sigma,e,E,params=None,**tags):
        rows.append(dict(id=name,parameters=dict(params or base),state=to_mandel(sigma)+[e],increment=to_mandel(E),tags=tags))
    E=from_mandel([.001,-.0003,.0002,.0004,-.0002,.0001])
    directions={'mixed':E,'reversed':[[-v for v in row]for row in E],'zero':[[0.]*3 for _ in range(3)],'xy_shear':from_mandel([0,0,0,.001,0,0]),'yz_shear':from_mandel([0,0,0,0,.001,0]),'xz_shear':from_mandel([0,0,0,0,0,.001])}
    sigmas=[from_mandel([120000,90000,80000,3000,-2000,1000]),from_mandel([80000,110000,140000,-4000,7000,2000])]
    for i,sigma in enumerate(sigmas):
        for name,d in directions.items():add(f'nonisotropic-{i}-{name}',sigma,.8,d,nonisotropic=True)
    for p in (.3,100000,9247007.657539926):
        e=math.expm1(base['N']-base['lambda_star']*math.log(p/1000))
        for name,d in {'load':from_mandel([.001]*3+[0]*3),'unload':from_mandel([-.001]*3+[0]*3),**directions}.items():add(f'sphere-{p:g}-{name}',[[p if i==j else 0. for j in range(3)]for i in range(3)],e,d,exact_sphere=True)
    R=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
    for name in ('mixed','reversed','yz_shear'):
        add('rotated-'+name,rotate(sigmas[0],R),.8,rotate(directions[name],R),rotation_of='nonisotropic-0-'+name,rotation=R)
    for i,updates in enumerate([dict(phi_c=math.radians(30),lambda_star=.12,kappa_star=.025,r=.7),dict(phi_c=math.radians(18),lambda_star=.2,kappa_star=.02,r=.3)]):
        add(f'other-parameters-{i}',sigmas[0],.8,E,base|updates,nonisotropic=True)
    return rows


def evaluate(case):
    z=case['state'];E=case['increment']
    result=rate(from_mandel(z[:6]),from_mandel(E),z[6],**case['parameters'])
    return case|dict(expected=to_mandel(result['stress_rate'])+[result['e_rate']],diagnostics=result['diagnostics'],stress_scale=max(1,math.hypot(*z[:6]))*math.hypot(*E),void_scale=max(1,(1+z[6])*math.hypot(*E)))


def build_reference():
    return dict(version='clay2005-appc-eq40-rate-reference-0.1',source_sha256=SOURCE_SHA256,source_selection='Appendix C and Eq40/41; conflicting printed Eq38 not silently repaired',basis='Atlas Mandel [xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz]',zero_spin=True,policy=POLICY,cases=[evaluate(c)for c in cases()],limitations=['Direct determinant source oracle not certified near isotropy; only exact sphere and nonisotropic j2>=1e-8 are comparison witnesses','No integration, final-publisher equivalence or admission'])


if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    args.output.write_text(json.dumps(build_reference(),indent=2,allow_nan=False)+'\n')
