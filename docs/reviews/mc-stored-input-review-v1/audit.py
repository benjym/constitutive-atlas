"""Independent source-only input audit; no Atlas/candidate/capture imports."""
from pathlib import Path
from fractions import Fraction as F
import collections
import hashlib
import json
import math
from decimal import Decimal as D, localcontext

import sys
P=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)

def run():
 d=json.loads((P/'inputs.json').read_text());cert=json.loads((P/'frozen/docs/ingestion/mohr-coulomb/results.json').read_text());cap=json.loads((P/'retained-v1-holds.json').read_text())
 checks={};details={}
 def test(name,val):checks[name]=bool(val)
 def frow(row,key,alt):return list(map(F,row.get(key,row.get(alt))))
 q=[[F(-2,3),F(2,15),F(11,15)],[F(2,3),F(-1,3),F(2,3)],[F(1,3),F(14,15),F(2,15)]]
 test('dense_rotation_orthonormal',all(sum(q[i][k]*q[j][k] for k in range(3))==int(i==j) for i in range(3) for j in range(3)))
 det=q[0][0]*(q[1][1]*q[2][2]-q[1][2]*q[2][1])-q[0][1]*(q[1][0]*q[2][2]-q[1][2]*q[2][0])+q[0][2]*(q[1][0]*q[2][1]-q[1][1]*q[2][0])
 test('dense_rotation_determinant_positive_one',det==1)
 def elastic(v,K,G):return [2*G*x+(K-F(2,3)*G)*sum(v) for x in v]
 def inverse(t,K,G):return [(x-sum(t)/3)/(2*G)+sum(t)/(9*K) for x in t]
 def rotated(v):return [[sum(q[i][k]*v[k]*q[j][k] for k in range(3)) for j in range(3)]for i in range(3)]
 def mandel(a):return [float(a[0][0]),float(a[1][1]),float(a[2][2]),math.sqrt(2)*float(a[0][1]),math.sqrt(2)*float(a[1][2]),math.sqrt(2)*float(a[0][2])]
 byid={c['id']:c for c in d['cases']}
 for row in cert['certificates']:
  name=row['case'];t=frow(row,'source_tension_principal_trial','trial');r=frow(row,'source_tension_return','return');gamma=F(row.get('gamma','0'))
  test(name+':ordered_trial_and_return',t[0]>=t[1]>=t[2] and r[0]>=r[1]>=r[2])
  test(name+':compression_sign_and_compliance',mandel(rotated([-x for x in inverse(t,F(1),F(1))]))==[float.fromhex(x)for x in byid['certificate/'+name+'/dense']['loading']])
  test(name+':exact_inverse_elastic',elastic(inverse(t,F(1),F(1)),F(1),F(1))==t)
  test(name+':yield',F(8,5)*r[0]-F(2,5)*r[2]-8<=0)
  if 'source_subgradient'in row:
   v=list(map(F,row['source_subgradient']));cor=elastic(v,F(1),F(1))
   test(name+':KKT_update',all(ti-ri==gamma*ci for ti,ri,ci in zip(t,r,cor)))
   test(name+':subgradient_bounds',F(4,3)>=v[0]>=v[1]>=v[2]>=F(-2,3) and sum(v)==F(2,3))
   test(name+':subgradient_complementarity',(v[0]-F(4,3))*(r[0]-r[1])==0 and (v[2]+F(2,3))*(r[1]-r[2])==0)
   test(name+':yield_complementarity',gamma>=0 and gamma*(F(8,5)*r[0]-F(2,5)*r[2]-8)==0)
 for c in d['cases']:
  p={k:float.fromhex(x)for k,x in c['parameters'].items()};K=p['E']/(3*(1-2*p['nu']));G=p['E']/(2*(1+p['nu']));s=math.sin(p['phi']);z=math.sin(p['psi'])
  test(c['id']+':parameter_domain',p['E']>0 and p['c']>0 and -1<p['nu']<.5 and 0<p['phi']<math.pi/2 and 0<p['psi']<math.pi/2 and K>0 and G>0)
  den=[4*K*z*s+4*G*(1+z*s/3),4*K*z*s+G*(3-s-z+z*s/3),4*K*z*s+G*(3+s+z+z*s/3),4*K*z*s]
  test(c['id']+':positive_denominators',all(math.isfinite(x)and x>0 for x in den))
  test(c['id']+':resolved_coefficient_interface',c['resolved_coefficients']=={k:float(v).hex()for k,v in {'K':K,'G':G,'sf':s,'sd':z,'cf':math.cos(p['phi'])}.items()})
  test(c['id']+':finite_shapes',all(len(c[g])==6 and all(math.isfinite(float.fromhex(x))for x in c[g])for g in ('current','parent','loading')))
  test(c['id']+':current_equals_parent_at_stored_point',c['current']==c['parent'])
 for label,nu,z in [('negative-lame',F(-3,5),F(1,3)),('high-poisson',F(49,100),F(1,3)),('dilation-above-friction',F(1,8),F(4,5))]:
  E=F(9,4);K=E/(3*(1-2*nu));G=E/(2*(1+nu))
  for branch in ('face','left','right','apex'):
   ret={'face':[F(5),F(2),F(0)],'left':[F(5),F(5),F(0)],'right':[F(5),F(0),F(0)],'apex':[F(20,3)]*3}[branch]
   v={'face':[1+z,F(0),-1+z],'left':[(1+z)/2,(1+z)/2,-1+z],'right':[1+z,(-1+z)/2,(-1+z)/2],'apex':[2*z/3]*3}[branch]
   t=[r+x/4 for r,x in zip(ret,elastic(v,K,G))]
   test(label+'/'+branch+':KKT',F(8,5)*ret[0]-F(2,5)*ret[2]==8 and t[0]>=t[1]>=t[2] and sum(v)==2*z and 1+z>=v[0]>=v[1]>=v[2]>=-1+z)
   expected=mandel(rotated([-x for x in inverse(t,K,G)]))
   test(label+'/'+branch+':stored_loading',expected==[float.fromhex(x)for x in byid['parameter/'+label+'/'+branch]['loading']])
 # Source scaling changes E,c, not the dimensionless strain or execution p_ref.
 for c in d['cases']:
  if 'power-of-two-stress-scale'not in c['tags']:continue
  _,name,power=c['id'].split('/');n=int(power);base=byid['certificate/'+name+'/dense']
  test(c['id']+':scale',c['loading']==base['loading'] and float.fromhex(c['parameters']['E'])==math.ldexp(2.25,n) and float.fromhex(c['parameters']['c'])==math.ldexp(5.,n) and float.fromhex(c['parameters']['p_ref'])==1.)
 seedvec=[[F(float.fromhex(x))for g in ('current','parent','loading')for x in seed[g]]for seed in d['seeds']]
 test('38_columns_present',d['columns']==len(seedvec)==38)
 test('first18_complete_independent_basis',all(v==[F(int(i==j))for j in range(18)]for i,v in enumerate(seedvec[:18])))
 test('20_dense_directions_unique_and_mixed',len({tuple(v)for v in seedvec[18:]})==20 and all(all(any(v[j:j+6])for j in (0,6,12))for v in seedvec[18:]))
 test('seeds_finite',all(math.isfinite(float(x))for v in seedvec for x in v))
 test('literal_capture_preserved',all(byid['retained-v1-hold/'+r['id']]['parent']==r['parent'] and byid['retained-v1-hold/'+r['id']]['parameters']==r['parameters'] for r in cap['cases']))
 test('capture_provenance_explicit',d['candidate_interpreter_capture_calls']==cap['candidate_interpreter_capture_calls']==8 and d['compiled_observations']==cap['compiled_observations']==0)
 test('source_hash',d['source_certificate_sha256']==hashlib.sha256((P/'frozen/docs/ingestion/mohr-coulomb/results.json').read_bytes()).hexdigest())
 test('capture_hash',d['capture_sha256']==hashlib.sha256((P/'retained-v1-holds.json').read_bytes()).hexdigest())
 test('isolated_generator_replay_byte_exact',(P/'inputs.json').read_bytes()==(OUT/'replay/inputs.json').read_bytes())
 dup=collections.defaultdict(list)
 for c in d['cases']:dup[tuple(c[g][j]for g in ('current','parent','loading')for j in range(6))+tuple(c['parameters'].values())].append(c['id'])
 details['named_rows']=len(d['cases']);details['unique_bitwise_input_parameter_tuples']=len(dup);details['duplicate_groups']=[v for v in dup.values()if len(v)>1]
 details['tags']=dict(collections.Counter(t for c in d['cases']for t in c['tags']))
 details['coverage_limits']=['18-dimensional current/parent/loading seed space; no parameter directional derivatives.','All stored current values equal parent values; separate seeds test independent local partials only.','Boundary/repeated-spectrum tags are exact-source construction provenance, not actual-rounded spectral labels.','Scale sweep fixes p_ref1Pa; physical E,c scale, numerical normalization does not.','No explicit rejected parameter/nonfinite input matrix or rollback stateful calls in these137 value/reference cases.','Dense trial rotations included; source hold cases have diagonal/planar parents, no new fully dense hold family.']
 # Exact-stored diagonal yield witness: mathematical trig from binary64 phi.
 with localcontext()as ctx:
  ctx.prec=90
  c=byid['hold/elastic_yield_hold/diagonal'];x=D.from_float(float.fromhex(c['parameters']['phi']));s=x;term=x;k=1
  while True:
   term=-term*x*x/D((2*k)*(2*k+1));old=s;s+=term;k+=1
   if s==old:break
  cf=D(1);term=D(1);k=1
  while True:
   term=-term*x*x/D((2*k-1)*(2*k));old=cf;cf+=term;k+=1
   if cf==old:break
  principal=sorted([-D.from_float(float.fromhex(v))for v in c['parent'][:3]],reverse=True)
  yieldvalue=(1+s)*principal[0]-(1-s)*principal[-1]-2*D(5)*cf
  details['nominal_yield_hold_exact_stored_mathematical_yield']=str(yieldvalue)
  test('nominal_yield_boundary_not_exact_stored_boundary',yieldvalue!=0)
 result={'identity':'mc-stored-input-independent-audit-v1','checks':checks,'failed':[k for k,v in checks.items()if not v],'status':'pass'if all(checks.values())else'fail','details':details}
 (OUT/'checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'status':result['status'],'assertions':len(checks),'failed':result['failed'],'unique_inputs':len(dup),'rounded_yield_witness':details['nominal_yield_hold_exact_stored_mathematical_yield']}))
 if result['failed']:raise SystemExit(1)
if __name__=='__main__':run()
