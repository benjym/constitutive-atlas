"""Independent14-state instantaneous HP/extracted-ASBS+GIS Cartesian reference.

Only stdlib and the independent Cartesian/dense HP reference; no Atlas/DSL or
material integrator. Input strain direction is compression-positive Mandel.
"""
import math
from tools import reference_gis2024_hp_host as hp

HP_PARAMETERS={'phi','hs','ei0','ec0','ed0','n','alpha','beta'}
GIS_PARAMETERS={'R','m_R','m_T','beta_R','chi_R','gamma_chi','chi_0','chi_max','C_Omega','gamma_Omega'}

class ReferenceDomainError(ValueError):
    pass

def real(x):
    try:valid=type(x) in (int,float) and math.isfinite(x) and float(x)==x
    except (ValueError,OverflowError):valid=False
    if not valid:raise ReferenceDomainError('finite lossless real required; bool excluded')
    return float(x)

def six(x):
    if type(x) not in (list,tuple) or len(x)!=6:raise ReferenceDomainError('six Mandel components required')
    return [real(v) for v in x]

def finite_tree(x):
    if isinstance(x,dict):
        for v in x.values():finite_tree(v)
    elif isinstance(x,(tuple,list)):
        for v in x:finite_tree(v)
    elif x is not None:real(x)
    return x

def coupled_rates(state,de,parameters):
    """Return instantaneous sigma6,e,h6,Omega derivatives plus diagnostics.

    No state is advanced and no inputs are mutated. Exact zero direction has
    zero derivatives and undefined directional k; no clipping/floors are used.
    """
    if not isinstance(state,dict) or set(state)!={'sigma','e','h','Omega'}:raise ReferenceDomainError('exact14-state fields required')
    if not isinstance(parameters,dict) or set(parameters)!=HP_PARAMETERS|GIS_PARAMETERS:raise ReferenceDomainError('exact18 material parameters required')
    p={k:real(v) for k,v in parameters.items()}
    sigma=six(state['sigma']);h=six(state['h']);e=real(state['e']);Omega=real(state['Omega']);d=six(de)
    if not (p['hs']>0 and 0<p['n']<1 and 0<p['phi']<math.pi/2 and p['alpha']>0 and p['beta']>=0 and 0<p['ed0']<p['ec0']<p['ei0'] and e>0):raise ReferenceDomainError('outside HP audit parameter domain')
    if any(p[k]<=0 for k in ['R','beta_R','chi_R','gamma_chi','chi_0','gamma_Omega']) or p['chi_max']<p['chi_0'] or p['C_Omega']<0 or not 1<=p['m_T']<=p['m_R'] or not 0<=Omega<=1:raise ReferenceDomainError('outside GIS audit parameter/state domain')
    sn=hp.mat(sigma);hm=hp.mat(h);dm=hp.mat(d);pressure=hp.trace(sn)/3
    if not pressure>0:raise ReferenceDomainError('positive effective mean pressure required')
    if math.sqrt(sum(x*x for x in h))>p['R']:raise ReferenceDomainError('h outside radius; no projection')
    try:
        comp=math.exp(-(3*pressure/p['hs'])**p['n'])
        if not p['ed0']*comp<e<p['ei0']*comp:raise ReferenceDomainError('void ratio outside bounded audit domain')
        Hpre=hp.mul(sn,1/hp.trace(sn));Hd=hp.add(Hpre,[[-1/3 if i==j else 0. for j in range(3)] for i in range(3)])
        j2=hp.dot(Hd,Hd);psi=math.sqrt(3*j2)
        cube=sum(Hd[i][j]*Hd[j][k]*Hd[k][i] for i in range(3) for j in range(3) for k in range(3))
        lode=-math.sqrt(6)*cube/j2**1.5 if j2 else 0.
        Fden=2+math.sqrt(2)*psi*lode
        if Fden<=0 or psi*psi/8+(2-psi*psi)/Fden<=0:raise ReferenceDomainError('outside positive F denominator/radicand scope')
        host=hp.oracle({k:p[k] for k in HP_PARAMETERS}|{'sigma':sigma,'e':e})
        finite_tree(host)
        if min(host[k] for k in ['F','fs','fd','fdAstar','C','S'])<=0:raise ReferenceDomainError('nonpositive host factor')
        H=hp.mul(sn,1/hp.trace(sn));Q=hp.dot(H,H)
        a=math.sqrt(3/8)*(3-math.sin(p['phi']))/math.sin(p['phi'])
        m=hp.mat(host['m']);hn=math.sqrt(sum(x*x for x in h));dn=hp.norm(dm)
        if hn==0 and any(v!=0 for v in h):raise ReferenceDomainError('nonzero h norm underflow')
        if dn==0 and any(v!=0 for v in d):raise ReferenceDomainError('nonzero strain direction norm underflow')
        hd=hp.mul(hm,1/hn) if hn else [[0.]*3 for _ in range(3)]
        rho=hn/p['R'];loading=hp.dot(hd,dm)
        chi=p['chi_0']+Omega*(p['chi_max']-p['chi_0']);gamma=p['gamma_chi']*chi
        finite_tree([rho,loading,chi,gamma])
        if all(v==0 for v in d):
            return {'sigma_rhs':[0.]*6,'e_rhs':0.,'h_rhs':[0.]*6,'Omega_rhs':0.,'derivative':[0.]*14,'diagnostics':{'rho':rho,'chi':chi,'gamma':gamma,'k':None,'q':None,'suppression':None,'fdAstar':host['fdAstar'],'S':host['S']}}
        q=loading/dn
        if not -1-64*math.ulp(1.)<=q<=1+64*math.ulp(1.):raise ReferenceDomainError('unresolved directional cosine')
        power=rho**p['chi_R']
        k=power*p['m_T']+(1-power)*p['m_R']
        k+=power*(1-p['m_T'])*q if loading>0 else -power*(p['m_R']-p['m_T'])*q
        if k<=0:raise ReferenceDomainError('nonpositive stiffness multiplier')
        suppression=host['S']**(k**gamma)
        if suppression<=0:raise ReferenceDomainError('positive suppression underflow')
        inner=hp.add(dm,hp.mul(m,-host['C']*suppression*dn))
        # Direct Cartesian B.2 action, not the GIS DSL or a production6x6 action.
        stress=hp.mul(hp.add(hp.mul(inner,host['F']**2),hp.mul(H,a*a*hp.dot(H,inner))),k*host['fs']/Q)
        hr=hp.add(dm,hp.mul(hd,-rho**p['beta_R']*loading)) if loading>0 else dm
        er=-(1+e)*hp.trace(dm)
        Or=p['C_Omega']*(1-rho**p['gamma_Omega']-Omega)*dn
        sr=hp.mandel(stress);hrr=hp.mandel(hr)
        return finite_tree({'sigma_rhs':sr,'e_rhs':er,'h_rhs':hrr,'Omega_rhs':Or,'derivative':sr+[er]+hrr+[Or],'diagnostics':{'rho':rho,'chi':chi,'gamma':gamma,'k':k,'q':q,'suppression':suppression,'fdAstar':host['fdAstar'],'S':host['S']}})
    except (ArithmeticError,ValueError,TypeError) as exc:
        if isinstance(exc,ReferenceDomainError):raise
        raise ReferenceDomainError('reference arithmetic/domain failure: '+str(exc)) from exc
