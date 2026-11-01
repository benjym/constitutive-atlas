"""Source-only rational algebra checks, independent of Atlas evaluation/compiler."""
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
policy=HERE/'check_policy.json'
checks=[]
def check(name,condition,detail=None):
    checks.append({'name':name,'passed':bool(condition),'detail':detail})
def determinant(v):
    x,y,z,u,vv,w=v
    return x*y*z+2*u*vv*w-x*vv*vv-y*w*w-z*u*u
def potential(v,k):
    return sum(v[:3])**3-k*determinant(v)
def components(v,k):
    x,y,z,u,vv,w=v;t=x+y+z
    return [3*t*t-k*(y*z-vv*vv),3*t*t-k*(x*z-w*w),3*t*t-k*(x*y-u*u),2*k*(z*u-vv*w),2*k*(x*vv-u*w),2*k*(y*w-u*vv)]
for label,v,k in [('triaxial',list(map(Q,[6,2,2])),Q(44)),('offdiagonal',[Q(10),Q(7),Q(5),Q(1),Q(1,2),Q(-1,4)],Q(51))]:
    v=v+[Q(0)]*(6-len(v));n=components(v,k);directions=[]
    for i in range(6):
        # Cubic g has central derivative D(h)=g'(0)+c*h²; cancel c exactly.
        def central(h):
            plus=v.copy();minus=v.copy();plus[i]+=h;minus[i]-=h
            return (potential(plus,k)-potential(minus,k))/(2*h)
        derivative=(4*central(Q(1,2))-central(Q(1)))/3
        directions.append(derivative)
    check(label+'_all6_gradient',directions==n)
    work=sum(s*a for s,a in zip(v,n));check(label+'_euler_3g',work==3*potential(v,k))
    stress_m=[float(a) for a in v[:3]]+[math.sqrt(2)*float(a) for a in v[3:]]
    strain_m=[float(a) for a in n[:3]]+[float(a)/math.sqrt(2) for a in n[3:]]
    mandel_work=sum(a*b for a,b in zip(stress_m,strain_m));err=abs(mandel_work-float(work))/max(1,abs(float(work)))
    check(label+'_mandel_work',err<=json.loads(policy.read_text())['float_checks']['Mandel_vs_engineering_work_relative_tolerance'],err)
v=[Q(3),Q(3),Q(3),Q(0),Q(0),Q(0)]
check('hydrostatic_f27',sum(v[:3])**3/determinant(v)==27)
check('hydrostatic_g_and_gradient_zero',potential(v,Q(27))==0 and all(a==0 for a in components(v,Q(27))))
s1,s3,nu=Q(6),Q(2),Q(3,5);t=s1+2*s3;k=3*t*t*(1+nu)/(s3*(s1+nu*s3))
ratio=(3*t*t-k*s1*s3)/(3*t*t-k*s3*s3)
check('Eq11_recovers_Eq10_ratio',ratio==-nu)
# Rational derivative quotient rule applied to independent Eq16 inversion W=a*x/(1-d*x).
for name,k1,ft,rf,M,l,Kur,n,A in [('dense',Q(103),Q(40),Q(957,1000),Q(255,1000000),Q(132,100),2300,Q(80,100),Q(44,100)),('loose',Q(58),Q(33),Q(970,1000),Q(680,1000000),Q(117,100),1600,Q(86,100),Q(39,100))]:
    check(name+'_table_admissibility',k1>ft>=27 and 0<rf<1 and M>0 and Kur>0 and 0<A<1)
    d=rf/(k1-ft);a=Q(7);x=(k1-ft)/2
    quotient_derivative=(a*(1-d*x)+a*x*d)/(1-d*x)**2
    eq19=a/(1-rf*x/(k1-ft))**2
    check(name+'_Eq16_derivative_Eq19',quotient_derivative==eq19)
    check(name+'_finite_failure_denominator',1-d*(k1-ft)==1-rf and 1-rf>0)
report={'policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),'scope':'Independent source algebra, no constitutive/path/backend qualification','checks':checks,'passed':all(c['passed'] for c in checks)}
(HERE/'algebra-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
