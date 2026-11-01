"""Reproducible local ASBS witness, not a material integrator or initialization API."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from tools import reference_clay2013_cartesian as oracle

SOURCE_SHA256='21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281'
ORACLE_SHA256='d37b6b87206cafc0a74af53f4effd51c37495f318dcf4889eeec19d55943e50b'
PARAMETERS=dict(phi_c=.5,lambda_star=.1,kappa_star=.01,N=.9,nu=.2)
STRESS=[[160000.,0.,0.],[0.,90000.,0.],[0.,0.,50000.]]
STRETCHING=[[.008,0.,0.],[0.,0.,0.],[0.,0.,-.01]]


def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def describe(stress,e,parameters):
    p=math.fsum(stress[i][i]/3 for i in range(3))
    t=[[-x/p for x in row] for row in stress]
    I1=sum(t[i][i] for i in range(3));I2=(sum(x*x for row in t for x in row)-I1*I1)/2;I3=determinant(t)
    fm=(9*I3+I1*I2)/(I3+I1*I2)
    phi=parameters['phi_c'];lam=parameters['lambda_star']
    omega=-2*math.log(math.cos(phi))/math.log(2)+.3*(fm-math.sin(phi)**2)
    logpe=math.log(1000)+(parameters['N']-math.log1p(e))/lam
    loggap=omega*(math.log(p)-logpe)-math.log1p(-fm)
    residual=(1-fm)*math.expm1(loggap)
    return {'p':p,'Fm':fm,'omega':omega,'log_pe':logpe,'pe_over_p':math.exp(logpe-math.log(p)),
            'asbs_loggap':loggap,'asbs_residual':residual}


def e_from_ratio(p,pe_over_p,*,N,lambda_star):
    """Exact algebraic conversion only; does not assert physical preparation/OCR."""
    if not all(type(x) in (int,float) and math.isfinite(x) for x in (p,pe_over_p,N,lambda_star)):
        raise ValueError('finite ratio conversion inputs required')
    if not p>0 or not pe_over_p>0 or not lambda_star>0:
        raise ValueError('positive pressure/ratio/compression slope required')
    e=math.expm1(N-lambda_star*math.fsum((math.log(p/1000),math.log(pe_over_p))))
    if not math.isfinite(e) or e<0:
        raise ValueError('requested density outside nonnegative-e diagnostic scope')
    return e


def directional_f_diagonal(stress,stress_rate,e,e_rate,parameters):
    """Differentiate Eqs17,18-21,25 and density Eq7 analytically for diagonal stress."""
    T=[-stress[i][i] for i in range(3)];td=[-stress_rate[i][i] for i in range(3)]
    I1=sum(T);I2=-sum(T[i]*T[j] for i,j in [(0,1),(1,2),(0,2)]);I3=math.prod(T)
    dI1=sum(td)
    dI2=-sum(td[i]*T[j]+T[i]*td[j] for i,j in [(0,1),(1,2),(0,2)])
    dI3=sum(td[i]*T[(i+1)%3]*T[(i+2)%3] for i in range(3))
    U=9*I3+I1*I2;V=I3+I1*I2
    dU=9*dI3+dI1*I2+I1*dI2;dV=dI3+dI1*I2+I1*dI2
    dFm=(dU*V-U*dV)/(V*V)
    desc=describe(stress,e,parameters)
    logx=math.log(desc['p'])-desc['log_pe']
    pd=sum(stress_rate[i][i] for i in range(3))/3
    logpe_dot=-e_rate/((1+e)*parameters['lambda_star'])
    result=dFm+math.exp(desc['omega']*logx)*(.3*dFm*logx+desc['omega']*(pd/desc['p']-logpe_dot))
    return {'f_dot':result,'Fm_dot':dFm,'p_dot':pd,'log_pe_dot':logpe_dot}


def verified_oracle():
    if oracle.SOURCE_SHA256!=SOURCE_SHA256:
        raise ValueError('oracle source receipt mismatch')
    if hashlib.sha256(Path(oracle.__file__).read_bytes()).hexdigest()!=ORACLE_SHA256:
        raise ValueError('oracle implementation hash mismatch; review and regenerate evidence')
    return oracle


def witness():
    oracle=verified_oracle()
    first=describe(STRESS,.7,PARAMETERS)
    ratio=math.exp(-math.log1p(-first['Fm'])/first['omega'])
    e=e_from_ratio(first['p'],ratio,N=PARAMETERS['N'],lambda_star=PARAMETERS['lambda_star'])
    initial=describe(STRESS,e,PARAMETERS)
    r=oracle.rate(STRESS,STRETCHING,e,**PARAMETERS)
    derivative=directional_f_diagonal(STRESS,r['stress_rate'],e,r['e_rate'],PARAMETERS)
    probes=[]
    for h in (1e-3,1e-4,1e-5,1e-6):
        plus=[[STRESS[i][j]+h*r['stress_rate'][i][j] for j in range(3)] for i in range(3)]
        minus=[[STRESS[i][j]-h*r['stress_rate'][i][j] for j in range(3)] for i in range(3)]
        fplus=describe(plus,e+h*r['e_rate'],PARAMETERS)['asbs_residual']
        fminus=describe(minus,e-h*r['e_rate'],PARAMETERS)['asbs_residual']
        probes.append({'h':h,'f_plus':fplus,'central_directional_difference':(fplus-fminus)/(2*h)})
    return {'source_sha256':SOURCE_SHA256,'parameters':PARAMETERS,'stress_Pa':STRESS,
            'compression_positive_stretching':STRETCHING,'e':e,'initial':initial,
            'rate':r,'analytic_directional_derivative':derivative,'directional_probes':probes,
            'scope':'local vector-field diagnostic; probes are tangent-state perturbations, not integrated paths'}



if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,help='optional private original PDF for hash verification')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.source is not None and hashlib.sha256(args.source.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise ValueError('source hash mismatch')
    evidence=witness()
    evidence['source_file_hash_verified']=args.source is not None
    evidence['input_hashes']={'tools/reference_clay2013_cartesian.py':ORACLE_SHA256,
                              'tools/clay2013_asbs_diagnostic.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(evidence,indent=2,sort_keys=True,allow_nan=False)+'\n')
