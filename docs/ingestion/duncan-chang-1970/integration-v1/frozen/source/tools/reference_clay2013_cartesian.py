"""Independent Cartesian Mašín-2013 diagnostic rate; zero spin, no integration.

No Atlas imports, Mandel conversion, reduced implementation or 2014/IGS law.
Inputs: symmetric3x3 compression-positive stress/stretching, stressPa, angle radians.
Source: author PDF pp.13-14 Eqs43-58; p.3 Eqs1,3,7.
"""
import math

SOURCE_SHA256 = '21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281'
SOURCE_URL = 'https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf'
DOI = 'https://doi.org/10.1007/s11440-012-0199-y'


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
        raise ValueError('outside conservative clay2013 diagnostic parameter/state scope')


def rate(stress,stretching,e,*,phi_c,lambda_star,kappa_star,N,nu):
    """Return compression-positive Cartesian stress rate, e rate and diagnostics.

    Stretching is per caller coordinate; no physical viscosity, spin or time step
    is inferred. Domain choices are diagnostic restrictions, not source theorems.
    """
    _parameters(e,phi_c,lambda_star,kappa_star,N,nu)
    sigma=_matrix(stress,'stress'); E=_matrix(stretching,'stretching')
    try:
        return _rate(sigma,E,e,phi_c,lambda_star,kappa_star,N,nu)
    except (OverflowError,ZeroDivisionError) as exc:
        raise ValueError('clay2013 arithmetic range/singular-state failure') from exc


def _rate(sigma,E,e,phi_c,lambda_star,kappa_star,N,nu):
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
    omega=-log_cos2/math.log(2)+.3*(Fm-sine2)
    xi=1.7+3.9*sine2
    pe=1000*math.exp((N-math.log1p(e))/lambda_star)
    fs=3*p/2*(1/lambda_star+1/kappa_star)*(1-2*nu)/(1+nu)
    if not (omega>0 and pe>0 and fs>0):
        raise ValueError('nonpositive omega/equivalent pressure/stiffness')
    fd=(2*p/pe)**2
    fdA=4*(1-Fm)**(2/omega)
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
    c=nu/(1-2*nu)
    # Literal fourth-order symmetric identity and dyadic terms (81 entries).
    L=[[[[.5*(float(i==k and j==l)+float(i==l and j==k))
             +c*float(i==j and k==l) for l in range(3)] for k in range(3)]
         for j in range(3)] for i in range(3)]
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
                           'source_sha256':SOURCE_SHA256,'zero_spin':True}}


def isotropic_pressure_rate(p,e,volumetric_compression_rate,*,lambda_star,kappa_star,N):
    """Separate analytic isotropic scalar result; no tensor-rate implementation calls."""
    if not all(_finite(x) for x in (p,e,volumetric_compression_rate,lambda_star,kappa_star,N)):
        raise ValueError('finite isotropic inputs required')
    if not (p>0 and e>=0 and lambda_star>kappa_star>0):
        raise ValueError('outside conservative isotropic scope')
    try:
        pe=1000*math.exp((N-math.log1p(e))/lambda_star)
        v=volumetric_compression_rate
        ratio=(p/pe)**2
        answer=p/2*((1/lambda_star+1/kappa_star)*v+
                    ratio*(1/lambda_star-1/kappa_star)*abs(v))
        _require_finite((pe,ratio,answer),'analytic isotropic result')
        if pe<=0 or ratio<=0:
            raise ValueError('isotropic factor outside arithmetic range')
        return answer
    except (OverflowError,ZeroDivisionError) as exc:
        raise ValueError('isotropic arithmetic range failure') from exc
