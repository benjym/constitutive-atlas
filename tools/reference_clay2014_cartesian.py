"""Independent Cartesian Mašín-2014 printed-Am/Eq49 diagnostic rate; zero spin, no integration.

No Atlas imports, reduced implementation or IGS law. Literal four-index L.
Inputs: symmetric3x3 compression-positive stress/stretching, stressPa, angle radians.
Source: author manuscript pp2-3 Eqs2-15 and pp9-10 Eqs34-50; inherited void closure.
"""
import math

SOURCE_SHA256 = '2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202'
SOURCE_URL = 'https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf'
DOI = 'https://doi.org/10.1680/geot.13.P.065'


def _finite(value):
    try:
        return type(value) in (int,float) and math.isfinite(value)
    except OverflowError:
        return False


def _matrix(value, label):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ValueError(label+':3x3 matrix required')
    if any(not isinstance(row,(list,tuple)) or len(row)!=3 for row in value):
        raise ValueError(label+':3x3 matrix required')
    if not all(_finite(x) for row in value for x in row):
        raise ValueError(label+':finite numeric entries required')
    if any(value[i][j]!=value[j][i] for i in range(3) for j in range(3)):
        raise ValueError(label+':exactly symmetric input required; no silent symmetrization')
    return [[float(x) for x in row] for row in value]


def determinant(a):
    """Direct Cartesian cofactor determinant, independent of cubic trace identity."""
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def _trace(a):
    return math.fsum(a[i][i] for i in range(3))


def _multiply(a,b):
    return [[math.fsum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _contract(c,a):
    return [[math.fsum(c[i][j][k][l]*a[k][l] for k in range(3) for l in range(3))
             for j in range(3)] for i in range(3)]


def _require_finite(values,label):
    if not all(_finite(x) for x in values):
        raise ValueError(label+':nonfinite arithmetic result')


def _parameters(e,phi_c,lambda_star,kappa_star,N,nu):
    if not all(_finite(x) for x in (e,phi_c,lambda_star,kappa_star,N,nu)):
        raise ValueError('finite explicit parameters and void ratio required')
    if not (e>=0 and lambda_star>kappa_star>0 and -1<nu<.5 and 0<phi_c<math.pi/2):
        raise ValueError('outside conservative clay2014 diagnostic parameter/state scope')


def coefficients(nu,g,E,v):
    if not all(_finite(x)for x in(nu,g,E,v))or not(-1<nu<.5 and min(g,E,v)>0):raise ValueError('anisotropy parameter support')
    B=1-nu-2*E*nu*nu/(v*v)
    c=[E*B,E*nu*(1+E*nu/(v*v)),E*nu*(1/v+nu/v-1-E*nu/(v*v)),E*B*(1-g)/g,E*(1-E*nu*nu/(v*v))+1-nu*nu-2*E*nu*(1+nu)/v-2*E/g*B]
    Am=nu*nu*(4*E/v-2*E*E+2*E*E/(v*v)-1)+nu*(4*E/v+2*E)+2*E+1
    trace=3*c[0]+9*c[1]+6*c[2]+2*c[3]+c[4]
    if not all(_finite(x)for x in(*c,Am,trace))or B<=0 or Am<=0:raise ValueError('coefficient arithmetic/support')
    return c,Am,trace

def plane(axis):
    if not isinstance(axis,(list,tuple))or len(axis)!=3 or not all(_finite(x)for x in axis):raise ValueError('finite axis3')
    n=list(map(float,axis));q=math.fsum(x*x for x in n)
    if not _finite(q)or abs(q-1)>64*math.ulp(1.):raise ValueError('unit axis required; no normalization')
    return [[n[i]*n[j]for j in range(3)]for i in range(3)]

def stiffness(coefficients,P):
    a1,a2,a3,a4,a5=coefficients
    d=lambda i,j:float(i==j)
    return [[[[a1/4*(d(i,k)*d(j,l)+d(i,l)*d(j,k)+d(j,l)*d(i,k)+d(j,k)*d(i,l))
         +a2*d(i,j)*d(k,l)+a3*(P[i][j]*d(k,l)+d(i,j)*P[k][l])
         +a4/2*(P[i][k]*d(j,l)+P[i][l]*d(j,k)+P[j][l]*d(i,k)+P[j][k]*d(i,l))+a5*P[i][j]*P[k][l]
         for l in range(3)]for k in range(3)]for j in range(3)]for i in range(3)]

def rate(stress,stretching,e,axis,*,phi_c,lambda_star,kappa_star,N,nu_pp,alpha_G,alpha_E,alpha_nu,source_a=.3):
    _parameters(e,phi_c,lambda_star,kappa_star,N,nu_pp)
    if not _finite(source_a)or source_a!=.3:raise ValueError('selected source_a=.3 variant only')
    sigma=_matrix(stress,'stress');E=_matrix(stretching,'stretching');P=plane(axis)
    try:return _rate(sigma,E,e,phi_c,lambda_star,kappa_star,N,nu_pp,P,alpha_G,alpha_E,alpha_nu,source_a)
    except(OverflowError,ZeroDivisionError)as exc:raise ValueError('clay2014 arithmetic failure')from exc

def _rate(sigma,E,e,phi_c,lambda_star,kappa_star,N,nu,P,alpha_G,alpha_E,alpha_nu,source_a):
    p=math.fsum(sigma[i][i]/3 for i in range(3))
    if not _finite(p) or p<=0:
        raise ValueError('strictly positive mean compression required')
    normalized_sigma=[[x/p for x in row] for row in sigma]
    # Sylvester criterion in Cartesian coordinates. No eigenvalue clipping.
    minor2=normalized_sigma[0][0]*normalized_sigma[1][1]-normalized_sigma[0][1]*normalized_sigma[1][0]
    det_sigma=determinant(normalized_sigma)
    if not (normalized_sigma[0][0]>0 and minor2>0 and det_sigma>0):
        raise ValueError('strictly positive-definite compression stress required')
    T=[[-x for x in row] for row in sigma]; D=[[-x for x in row] for row in E]
    t=[[-x for x in row] for row in normalized_sigma]
    I1=_trace(t)
    I2=(math.fsum(x*x for row in t for x in row)-I1*I1)/2
    I3=determinant(t)
    invariant_denominator=I3+I1*I2
    if invariant_denominator==0:
        raise ValueError('singular Matsuoka-Nakai invariant denominator')
    isotropic=(sigma[0][0]==sigma[1][1]==sigma[2][2] and
               all(sigma[i][j]==0 for i in range(3) for j in range(3) if i!=j))
    # Exact spherical branch uses the algebraic Fm=0, not a rounded quotient.
    Fm=0. if isotropic else (9*I3+I1*I2)/invariant_denominator
    if not _finite(Fm) or not 0<=Fm<1:
        raise ValueError('Fm outside conservative real/singular-free domain [0,1)')
    sine=math.sin(phi_c); cosine=math.cos(phi_c); sine2=sine*sine
    log_cos2=math.log1p(-sine2) if sine2<.5 else 2*math.log(cosine)
    omega=-log_cos2/math.log(2)+source_a*(Fm-sine2)
    xi=1.7+3.9*sine2
    pe=1000*math.exp((N-math.log1p(e))/lambda_star)
    coeff,Am,Am_trace=coefficients(nu,alpha_G,alpha_E,alpha_nu)
    L=stiffness(coeff,P)
    fs=9*p/(2*Am)*(1/lambda_star+1/kappa_star)
    af=math.sqrt(3)*(3-sine)/(2*math.sqrt(2)*sine)
    log_argument=(lambda_star-kappa_star)/(lambda_star+kappa_star)*(3+af*af)/(af*math.sqrt(3))
    if not _finite(log_argument)or log_argument<=0:raise ValueError('Eq49 log argument')
    alpha_f=math.log(log_argument)/math.log(2)
    if not _finite(alpha_f)or alpha_f<=0:raise ValueError('positive alpha_f diagnostic restriction')
    if not (omega>0 and pe>0 and fs>0):
        raise ValueError('nonpositive omega/equivalent pressure/stiffness')
    fd=(2*p/pe)**alpha_f
    fdA=2**alpha_f*(1-Fm)**(alpha_f/omega)
    _require_finite((omega,xi,pe,fs,fd,fdA),'source scalar factors')
    if fdA<=0 or fd<=0:
        raise ValueError('source density factor underflows or becomes singular')
    That=[[t[i][j]/I1-float(i==j)/3 for j in range(3)] for i in range(3)]
    if isotropic:
        d=[[-float(i==j)/math.sqrt(3) for j in range(3)] for i in range(3)]
        cos3theta=None
    else:
        square=_multiply(That,That); cube=_multiply(square,That)
        dev_square=math.fsum(x*x for row in That for x in row)
        if dev_square<=0:
            raise ValueError('nonisotropic deviator unresolved in arithmetic')
        cos3theta=-math.sqrt(6)*_trace(cube)/(dev_square**1.5)
        if not _finite(cos3theta) or not -1<=cos3theta<=1:
            raise ValueError('Lode cosine outside [-1,1]; no clipping')
        sine_xi=sine**xi
        if 1-sine_xi<=0:
            raise ValueError('singular asymptotic-direction angle denominator')
        X=(2/3-(cos3theta+1)*Fm**.25/4)*(Fm**(xi/2)-sine_xi)/(1-sine_xi)
        dA=[[-That[i][j]+float(i==j)*X for j in range(3)] for i in range(3)]
        magnitude=math.hypot(*(x for row in dA for x in row))
        if not _finite(magnitude) or magnitude<=0:
            raise ValueError('singular/nonfinite asymptotic direction')
        d=[[x/magnitude for x in row] for row in dA]
    A=[[[[fs*L[i][j][k][l]+T[i][j]/lambda_star*float(k==l)
           for l in range(3)] for k in range(3)] for j in range(3)] for i in range(3)]
    _require_finite((x for a in A for b in a for c_row in b for x in c_row),'fourth-order A')
    LD=_contract(L,D); Ad=_contract(A,d)
    norm_D=math.hypot(*(x for row in D for x in row))
    multiplier=fd/fdA*norm_D
    # Negation converts source T_circle back to compression-positive rate.
    answer=[[-(fs*LD[i][j]-multiplier*Ad[i][j]) for j in range(3)] for i in range(3)]
    e_rate=-(1+e)*_trace(E)
    _require_finite((norm_D,multiplier,e_rate,*[x for row in answer for x in row]),'returned rates')
    return {'stress_rate':answer,'e_rate':e_rate,
            'diagnostics':{'p':p,'pe':pe,'Fm':Fm,'omega':omega,'xi':xi,'fd':fd,'fdA':fdA,'fs':fs,
                           'cos3theta':cos3theta,'d_source':d,'norm_D':norm_D,
                           'L_contract_D_source':LD,'A_contract_d_source':Ad,
                           'source_invariants_normalized_by_p':[I1,I2,I3],
                           'branch':'exact_isotropic' if isotropic else 'nonisotropic',
                           'source_sha256':SOURCE_SHA256,'zero_spin':True,'Am_printed':Am,'Am_trace':Am_trace,'alpha_f':alpha_f,'coefficients':coeff,'projector':P}}


PARAMETER_ORDER=['p_ref','p_scale','phi_c','lambda_star','kappa_star','N','nu_pp','alpha_G','alpha_E','alpha_nu','n1','n2','n3','source_a','lode_roundoff_allowance','orientation_allowance','stress_interior_margin']
POLICY={'stress_scaled_bound':2e-12,'stress_absolute_floor_Pa':1e-10,'stress_scale':'max(1Pa,Frobenius(actual supplied stress))*Frobenius(actual supplied loading)','void_scaled_bound':2e-13,'void_absolute_floor':1e-15,'void_scale':'max(1, (1+e)*Frobenius(actual supplied loading))','zero_loading_rates':'all seven exactly zero','observable_scaled_bound':2e-12,'covariance_scaled_bound':2e-12,'purpose':'instantaneous zero-spin printed-Eq14/Eq49 base research only; no IGS/AD/integration/admission'}
def from_mandel(v):
    r=math.sqrt(2);return [[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]
def to_mandel(m):
    r=math.sqrt(2);return [m[0][0],m[1][1],m[2][2],r*m[0][1],r*m[1][2],r*m[0][2]]
def rotate(m,q):
    out=[[0.]*3 for _ in range(3)]
    for i in range(3):
        for j in range(i,3):out[i][j]=out[j][i]=math.fsum(q[i][k]*m[k][l]*q[j][l]for k in range(3)for l in range(3))
    return out

def default_parameters():return dict(zip(PARAMETER_ORDER,[1000.,1e5,math.radians(30),.12,.025,1.1,.1,2.,2.**1.25,2.,0.,0.,1.,.3]+[64*math.ulp(1.)]*3))
def evaluate(case):
    p=case['parameters'];z=case['state'];inc=case['increment']
    if set(p)!=set(PARAMETER_ORDER)or not all(_finite(v)for v in p.values())or p['p_ref']!=1000 or not 1<=p['p_scale']<=1e12:raise ValueError('explicit selected17 parameters')
    if any(p[k]!=64*math.ulp(1.)for k in('lode_roundoff_allowance','orientation_allowance','stress_interior_margin')):raise ValueError('fixed numerical policies')
    if not isinstance(z,list)or len(z)!=7 or not all(_finite(v)for v in z)or not isinstance(inc,list)or len(inc)!=6 or not all(_finite(v)for v in inc):raise ValueError('state7/loading6')
    out=rate(from_mandel(z[:6]),from_mandel(inc),z[6],[p[k]for k in('n1','n2','n3')],**{k:p[k]for k in('phi_c','lambda_star','kappa_star','N','nu_pp','alpha_G','alpha_E','alpha_nu','source_a')})
    expected=to_mandel(out['stress_rate'])+[out['e_rate']]
    return {'expected':expected,'diagnostics':out['diagnostics'],'stress_scale':max(1.,math.hypot(*z[:6]))*math.hypot(*inc),'void_scale':max(1.,(1+z[6])*math.hypot(*inc))}
def cases():
    base=default_parameters();sigma=[120000.,90000.,80000.,3000.,-2000.,1000.];load=[.001,-.0003,.0002,.0004,-.0002,.0001];out=[]
    def add(name,p,z,de):out.append(dict(id=name,parameters=p.copy(),state=z.copy(),increment=de.copy()))
    for name,n in [('vertical',[0.,0.,1.]),('oblique',[1/3,2/3,2/3]),('negative-oblique',[-1/3,-2/3,-2/3])]:
        p=base|dict(zip(('n1','n2','n3'),n))
        for scale in(.01,1.,10.):
            for label,de in [('mixed',load),('reverse',[-x for x in load]),('zero',[0.]*6)]:add(f'{name}-p{scale}-{label}',p,[x*scale for x in sigma]+[.65],de)
    for label,de in [('xy',[0.,0.,0.,.001,0.,0.]),('yz',[0.,0.,0.,0.,.001,0.]),('xz',[0.,0.,0.,0.,0.,.001]),('hydro-compression',[.001]*3+[0.]*3),('hydro-expansion',[-.001]*3+[0.]*3)]:add('canonical-'+label,base,[1e5]*3+[0.]*3+[.65],de)
    for label,de in [('mixed',load),('hydro',[.001]*3+[0.]*3),('reverse',[-.001]*3+[0.]*3),('zero',[0.]*6)]:add('isotropic-ratios-'+label,base|dict(alpha_G=1.,alpha_E=1.,alpha_nu=1.),[1e5]*3+[0.]*3+[.65],de)
    q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]];n=[1/3,2/3,2/3];p=base|dict(zip(('n1','n2','n3'),[math.fsum(q[i][j]*n[j]for j in range(3))for i in range(3)]))
    add('rotated-oblique-mixed',p,to_mandel(rotate(from_mandel(sigma),q))+[.65],to_mandel(rotate(from_mandel(load),q)))
    return out

def invalid_cases():
    import copy
    base=cases()[0];out=[]
    for name,field,value in [('axis-zero','axis',[0.,0.,0.]),('axis-not-unit','axis',[0.,0.,2.]),('axis-near-invalid','axis',[0.,0.,1.+1e-10]),('negative-void','state',base['state'][:6]+[-.1]),('zero-stress','state',[0.]*6+[.65]),('indefinite','state',[1e5,1e5,-1e5,0.,0.,0.,.65])]:
        c=copy.deepcopy(base);c['id']='invalid-'+name
        if field=='axis':c['parameters'].update(dict(zip(('n1','n2','n3'),value)))
        else:c[field]=value
        out.append(c)
    for name,value in [('alpha_G',0.),('alpha_E',0.),('alpha_nu',0.),('kappa_star',0.),('nu_pp',.5),('phi_c',0.),('source_a',.4),('p_ref',999.),('p_scale',0.)]:
        c=copy.deepcopy(base);c['id']='invalid-'+name;c['parameters'][name]=value;out.append(c)
    c=copy.deepcopy(base);c['id']='invalid-lambda-equals-kappa';c['parameters']['kappa_star']=c['parameters']['lambda_star'];out.append(c)
    return out

def build_reference():
    import hashlib,pathlib
    return {'version':'clay2014-printed-Am-Eq49-cartesian-v1','source_sha256':SOURCE_SHA256,'source_url':SOURCE_URL,'source_locators':['PDFp2Eqs2-6','PDFp3Eqs7-15','PDFp9Eqs34-47','PDFp10Eqs48-50'],'generator_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'parameter_order':PARAMETER_ORDER,'basis':'symmetric_mandel','compression_positive':True,'zero_spin':True,'variant':'printed Eq14 Am and proposed Eq49 exponent; source Am identity discrepancy retained; no IGS','policy':POLICY,'cases':[c|evaluate(c)for c in cases()],'invalid_cases':invalid_cases(),'claims':{'scientific_admission':False,'integration':False,'AD':False,'source_repair':False},'limitations':['Binary64 scalar arithmetic and direct determinant invariants, not certified highprecision reference.','Nonisotropic near-isotropic cancellation and exact Lode boundaries may reject; corpus avoids those cancellation regions.','Axis64epsilon unit margin is a numerical project policy, no hidden normalization.']}
