"""Independent scalar/tensor algebra and rational-rank proof, no Atlas imports."""
import hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
D=Path(__file__).resolve().parent;SOURCE=Path('/private/tmp/atlas-control-partition-v1/source')
model=SOURCE/'models/manzari-dafalias-1997-constant-m-be-v1.json';m=json.loads(model.read_text());p={k:v['default']for k,v in m['parameters'].items()}
assert hashlib.sha256(model.read_bytes()).hexdigest()=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'
S=math.sqrt(2/3)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def evaluate(z):
 sigma=z[:6];pressure=sum(sigma[:3])/3;e=z[6];alpha=z[7:13];gamma=z[13]
 dev=[v-(pressure if i<3 else 0)for i,v in enumerate(sigma)];rel=[v/pressure-a for v,a in zip(dev,alpha)];rn=norm(rel);n=[v/rn for v in rel]if rn else[0.]*6
 M=[[n[0],n[3]/math.sqrt(2),n[5]/math.sqrt(2)],[n[3]/math.sqrt(2),n[1],n[4]/math.sqrt(2)],[n[5]/math.sqrt(2),n[4]/math.sqrt(2),n[2]]]
 cos=math.sqrt(6)*sum(M[i][j]*M[j][k]*M[k][i]for i in range(3)for j in range(3)for k in range(3))
 psi=e-p['ec_ref']+p['lambda_c']*math.log(pressure/p['p_ref'])
 def g(c):return 2*c/((1+c)-(1-c)*cos)
 ab=p['Mc']+p['kbc']*max(-psi,0)-p['m'];abimage=g(p['Me']/p['Mc'])*p['Mc']+g(p['kbe']/p['kbc'])*p['kbc']*max(-psi,0)-p['m']
 adimage=g(p['Me']/p['Mc'])*p['Mc']+g(p['kde']/p['kdc'])*p['kdc']*psi-p['m'];bn=S*abimage-dot(alpha,n);bref=2*S*ab;draw=p['A']*(S*adimage-dot(alpha,n));yield_scaled=(norm([s-pressure*a for s,a in zip(dev,alpha)])-S*p['m']*pressure)/p['p_ref']
 violations=[]
 for name,ok in [('p > 0*p_ref',pressure>0),('e > 0',e>0),('b_ref > abs(bn)',bref>abs(bn)),('alpha_bc > 0',ab>0),('gamma >= -1e-10',gamma>=-1e-10),('abs(trace(alpha)) <= 1e-10',abs(sum(alpha[:3]))<=1e-10),('Mc > m',p['Mc']>p['m']),('Me > m',p['Me']>p['m'])]:
  if not ok:violations.append(name)
 denominators=[(1+c)-(1-c)*cos for c in [p['Me']/p['Mc'],p['kbe']/p['kbc'],p['kde']/p['kdc']]]
 assert all(x>0 for x in denominators)
 return dict(angular_denominators=denominators,complementarity_radius=math.hypot(gamma,yield_scaled),trace_domain_margin=1e-10-abs(sum(alpha[:3])),violations=violations,p=pressure,e=e,relative_norm=rn,psi=psi,bn=bn,b_ref_minus_abs_bn=bref-abs(bn),alpha_bc=ab,D_raw=draw,cos3theta=cos,yield_scaled=yield_scaled,branch=[rn>0,psi>0,bn>0,draw>0],alpha_trace=sum(alpha[:3]),gamma=gamma)
z=[110000,95000,100000,500,0,0,.65]+[0.]*6+[.0001];base=evaluate(z);assert not base['violations']
scales=[160000.]*6+[1.]*8;old=[];new=[]
for j in range(14):
 for sign in [1,-1]:
  v=z.copy();v[j]+=sign*1e-6*scales[j];old.append(dict(index=j,sign=sign,**evaluate(v)))
 for h in [5e-11,2.5e-11]if j in [7,8,9]else[1e-6,5e-7]:
  for sign in [1,-1]:
   v=z.copy();v[j]+=sign*h*scales[j];result=evaluate(v);assert not result['violations']and result['branch']==base['branch'];new.append(dict(index=j,h=h,sign=sign,**result))
invalid=sorted({x['index']for x in old if x['violations']});assert invalid==[7,8,9]
basis=[[1/math.sqrt(2),-1/math.sqrt(2),0,0,0,0],[1/math.sqrt(6),1/math.sqrt(6),-2/math.sqrt(6),0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]
tangent=[]
for i,v in enumerate(basis):
 for h in [1e-6,5e-7]:
  for sign in [1,-1]:
   q=z.copy();q[7:13]=[a+sign*h*b for a,b in zip(q[7:13],v)];r=evaluate(q);assert not r['violations']and r['branch']==base['branch'];assert r['alpha_trace']==0;tangent.append(dict(direction=i,h=h,sign=sign,**r))
# Exact rational rank with unnormalized vectors (normalization does not alter rank).
B=[]
for j in list(range(7))+[13]:
 v=[F(0)]*14;v[j]=F(1);B.append(v)
for a in [[1,-1,0,0,0,0],[1,1,-2,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]:B.append([F(0)]*7+list(map(F,a))+[F(0)])
A=[v.copy()for v in B];rank=0
for col in range(14):
 pivot=next((j for j in range(rank,len(A))if A[j][col]),None)
 if pivot is None:continue
 A[rank],A[pivot]=A[pivot],A[rank];a=A[rank][col];A[rank]=[x/a for x in A[rank]]
 for j in range(len(A)):
  if j!=rank:
   a=A[j][col];A[j]=[x-a*y for x,y in zip(A[j],A[rank])]
 rank+=1
assert rank==13 and all(sum(v[7:10])==0 for v in B)
oldrotation=[105000,95000,160000,1000,0,0,.65]+[0.]*7;oldr=evaluate(oldrotation);assert oldr['yield_scaled']>1e-8
rotation=[640500,639500,640000,100,0,0,.65]+[0.]*7;rot=evaluate(rotation);assert not rot['violations']and rot['yield_scaled']<0
# Exact pressure interval and invariant norm envelope for every proportional prefix.
de=[.0001,-.00002,.00001,.00003,.00001,-.00001];trace=sum(de[:3]);dev=[v-(trace/3 if i<3 else 0)for i,v in enumerate(de)]
modmax=p['G0']*(650000/p['p_at'])**p['a'];elasticbound=math.sqrt(510000)+2*modmax*norm(dev);radius=S*p['m']*640000;assert 640000+modmax*trace<650000 and elasticbound<radius
pressure_map_derivative_bound=trace*p['a']*modmax/640000
void_min=.65-(1+p['e0'])*trace
psi_max=.65-p['ec_ref']+p['lambda_c']*math.log(650000/p['p_ref'])
source_nonzero_inner=dot([500,-500,0,100,0,0],dev)
assert pressure_map_derivative_bound<.01 and void_min>0 and psi_max<0 and source_nonzero_inner>0
rpt=dict(identity='md1997-admissible-native-source-proof-v1',compiled_calls=0,atlas_imports=False,base=base,old_invalid_fd_indices=invalid,original_rotation=oldr,cartesian_h_h2_domain_branch_receipts=new,tracefree_h_h2_receipts=tangent,source_tangent_rank=rank,source_tangent_dimension=13,missing_physical_direction='isotropic alpha trace normal; separate implementation trace-band study has full14 Cartesian columns',rotation=rot,rotation_elastic_prefix_envelope=dict(pressure_interval=[640000,650000],upper_fixed_point=640000+modmax*trace,deviator_norm_upper=elasticbound,minimum_yield_radius=radius,strict_margin_Pa=radius-elasticbound,pressure_map_derivative_bound=pressure_map_derivative_bound,void_ratio_lower=void_min,psi_upper=psi_max,initial_deviator_dot_strain_deviator=source_nonzero_inner),ad_fd_result='not observed; only domain/branch/rank/algebra proved')
encoded=json.dumps(rpt,indent=2,allow_nan=False)+'\n'
report_path=D/'proof-results.json'
if report_path.exists():assert report_path.read_text()==encoded,'preserve existing proof report; new study identity required for a changed result'
else:report_path.write_text(encoded)
print(json.dumps(dict(invalid_original_indices=invalid,new_cartesian_probes=len(new),tracefree_probes=len(tangent),rank=rank,elastic_margin_Pa=radius-elasticbound,compiled_calls=0)))
