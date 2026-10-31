"""Independent normalized determinant Cartesian/cofactor quotient references.
No Atlas or compiled material imports. Radical field is used for exact tie/certification,
not the Decimal Cartesian calculation.
"""
import argparse,hashlib,json,math
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(s):
 x=float(s)
 if not math.isfinite(x):raise ValueError('nonfinite input or seed')
 return x

def dec(x):n,d=x.as_integer_ratio();return D(n)/D(d)
def dmatrix(v):
 q=D(2).sqrt();x,y,z,u,v,w=v;return [[x,u/q,w/q],[u/q,y,v/q],[w/q,v/q,z]]
def cofactor(a):
 out=[]
 for i in range(3):
  row=[]
  for j in range(3):
   r=[k for k in range(3)if k!=i];c=[k for k in range(3)if k!=j];row.append((a[r[0]][c[0]]*a[r[1]][c[1]]-a[r[0]][c[1]]*a[r[1]][c[0]])*((-1)**(i+j)))
  out.append(row)
 return out

def determinant(a,c):return sum((a[0][j]*c[0][j]for j in range(3)),D(0))
def decimal_cartesian(values,seeds,prec):
 with localcontext()as ctx:
  ctx.prec=prec;a=dmatrix([dec(x)for x in values]);c=cofactor(a);out=[determinant(a,c)]
  for col in range(38):
   e=dmatrix([dec(seeds[r][col])for r in range(6)]);out.append(sum((c[i][j]*e[i][j]for i in range(3)for j in range(3)),D(0)))
  return out

class Q:
 """Exact a+b sqrt2, assembled via Cartesian entries and tensor cofactors."""
 def __init__(self,a=0,b=0):self.a=F(a);self.b=F(b)
 def __add__(self,o):
  if not isinstance(o,Q):o=Q(o)
  return Q(self.a+o.a,self.b+o.b)
 __radd__=__add__
 def __neg__(self):return Q(-self.a,-self.b)
 def __sub__(self,o):return self+-o
 def __mul__(self,o):
  if not isinstance(o,Q):o=Q(o)
  return Q(self.a*o.a+2*self.b*o.b,self.a*o.b+self.b*o.a)
 __rmul__=__mul__
 def json(self):return {'rational':[str(self.a.numerator),str(self.a.denominator)],'sqrt2_coefficient':[str(self.b.numerator),str(self.b.denominator)]}

def qmatrix(v):
 x,y,z,u,v,w=[F(x)for x in v];return [[Q(x),Q(0,u/2),Q(0,w/2)],[Q(0,u/2),Q(y),Q(0,v/2)],[Q(0,w/2),Q(0,v/2),Q(z)]]
def exact_cartesian(values,seeds):
 a=qmatrix(values);c=cofactor(a);out=[sum((a[0][j]*c[0][j]for j in range(3)),Q())]
 for col in range(38):
  e=qmatrix([seeds[r][col]for r in range(6)]);out.append(sum((c[i][j]*e[i][j]for i in range(3)for j in range(3)),Q()))
 return out

def rounded(v):
 try:x=float(v)
 except OverflowError:return {'overflow':True,'sign':1 if v>0 else-1}
 if not math.isfinite(x):return {'overflow':True,'sign':1 if x>0 else-1}
 if x==0:x=0.
 return {'overflow':False,'hex':x.hex(),'value':x}

def certified(q):
 if q.b==0:
  answer=rounded(q.a);return answer|{'certified':True,'method':'exact-rational-nearest-even'}
 # sqrt2 bounded by consecutive integer multiples of10^-512, via exact isqrt.
 base=10**512;lo=F(math.isqrt(2*base*base),base);hi=lo+F(1,base)
 a,b=(q.a+q.b*lo,q.a+q.b*hi)if q.b>0 else(q.a+q.b*hi,q.a+q.b*lo)
 lower,upper=rounded(a),rounded(b)
 if lower!=upper:return {'certified':False,'method':'unresolved-512digit-enclosure','lower_round':lower,'upper_round':upper}
 return lower|{'certified':True,'method':'512digit-rational-sqrt2-enclosure'}


def normalized_exact(values,seeds):
 t=sum((F(x)for x in values[:3]),F());assert t
 components=exact_cartesian(values,seeds);p=components[0]
 def divided(q,d):return Q(q.a/d,q.b/d)
 result=[divided(p,t**3)]
 for col,q in enumerate(components[1:]):
  te=sum((F(seeds[r][col])for r in range(3)),F());result.append(divided(q*t-p*(3*te),t**4))
 return result

def normalized_decimal(values,seeds,prec):
 with localcontext()as ctx:
  ctx.prec=prec;a=dmatrix([dec(x)for x in values]);cof=cofactor(a);p=determinant(a,cof);t=dec(sum((F(x)for x in values[:3]),F()));out=[p/(t**3)]
  for col in range(38):
   e=dmatrix([dec(seeds[r][col])for r in range(6)]);dp=sum((cof[i][j]*e[i][j]for i in range(3)for j in range(3)),D(0));te=dec(sum((F(seeds[r][col])for r in range(3)),F()));out.append((dp*t-3*p*te)/(t**4))
  return out

def rejection(reason):return {'ok':False,'reason':reason,'value':None,'derivatives':[None]*38,'unchanged_output':True}
def scaled(a,b):return max(abs(x-y)/max(D(1),abs(x),abs(y))for x,y in zip(a,b))
def run(packet,root):
 freeze=json.loads((packet/'prospective-freeze.json').read_text())
 for n,s in freeze['files'].items():assert sha(root/n)==s,n
 rows=[];summary={'unique_cases':len(freeze['cases']),'primal_accepted':0,'Jet_accepted':0,'nonfinite_primals':0,'nonfinite_seeds':0,'zero_trace':0,'primal_overflow':0,'derivative_overflow':0,'unresolved':0,'convergence_failures':0,'certified_components':0,'exact_zero_precision_branches':0}
 for raw in freeze['cases']:
  row={k:raw[k]for k in ('id','values','seeds','tags')}
  try:values=list(map(parse,raw['values']))
  except ValueError:row.update(primal_expectation={'ok':False,'reason':'nonfinite-primal'},expectation=rejection('nonfinite-primal'));summary['nonfinite_primals']+=1;rows.append(row);continue
  trace=sum((F(x)for x in values[:3]),F());row['exact_trace']=[str(trace.numerator),str(trace.denominator)]
  if trace==0:row.update(primal_expectation={'ok':False,'reason':'zero-trace'},expectation=rejection('zero-trace'));summary['zero_trace']+=1;rows.append(row);continue
  zero_seeds=[[0.]*38 for _ in range(6)];primal_q=normalized_exact(values,zero_seeds)[0];primal_cert=certified(primal_q);row['primal_rounding_certificate']=primal_cert;row['exact_primal_component']=primal_q.json()
  if not primal_cert['certified']:summary['unresolved']+=1;row.update(primal_expectation={'ok':None,'reason':'unresolved-reference'},expectation={'ok':None,'reason':'unresolved-reference'});rows.append(row);continue
  summary['certified_components']+=1
  if primal_cert['overflow']:row['primal_expectation']={'ok':False,'reason':'final-primal-overflow'};summary['primal_overflow']+=1
  else:row['primal_expectation']={'ok':True,'hex':primal_cert['hex'],'value':primal_cert['value']};summary['primal_accepted']+=1
  try:seeds=[list(map(parse,r))for r in raw['seeds']]
  except ValueError:row['expectation']=rejection('nonfinite-seed');summary['nonfinite_seeds']+=1;rows.append(row);continue
  assert len(values)==6 and len(seeds)==6 and all(len(r)==38 for r in seeds)
  exact_components=normalized_exact(values,seeds);certs=[certified(q)for q in exact_components];row['rounding_certificates']=certs;row['exact_cartesian_algebraic_components']=[q.json()for q in exact_components];summary['certified_components']+=38
  precision={n:normalized_decimal(values,seeds,n)for n in freeze['policy']['precision_digits']};zero_components=[i for i,q in enumerate(exact_components)if q.a==0 and q.b==0];summary['exact_zero_precision_branches']+=len(zero_components)
  corrected={n:[D(0)if i in zero_components else v for i,v in enumerate(vals)]for n,vals in precision.items()}
  with localcontext()as ctx:ctx.prec=1000;difference=scaled(corrected[640],corrected[960]);passed=difference<=D('1e-200')
  row['precision_check']={'digits':[640,960],'max_scaled_component_difference_with_predeclared_exact_zero_branches':str(difference),'passed':passed,'exact_zero_components':zero_components,'raw_decimal_values':{str(n):list(map(str,v))for n,v in precision.items()}}
  if not passed:summary['convergence_failures']+=1
  if not all(c['certified']for c in certs):row['expectation']={'ok':None,'reason':'unresolved-reference'};summary['unresolved']+=1
  elif primal_cert['overflow']:row['expectation']=rejection('final-primal-overflow')
  elif any(c['overflow']for c in certs[1:]):row['expectation']=rejection('final-derivative-overflow');row['expectation']['overflow_derivative_columns']=[i for i,c in enumerate(certs[1:])if c['overflow']];summary['derivative_overflow']+=1
  else:row['expectation']={'ok':True,'value':certs[0]['value'],'value_hex':certs[0]['hex'],'derivatives':[c['value']for c in certs[1:]],'derivatives_hex':[c['hex']for c in certs[1:]],'canonical_positive_zero':True};summary['Jet_accepted']+=1
  rows.append(row)
 summary['Jet_rejected']=summary['unique_cases']-summary['Jet_accepted'];summary['primal_rejected']=summary['unique_cases']-summary['primal_accepted']
 baseline=next(c for c in rows if c['id']=='prior/regular/sphere');assert baseline['expectation']['ok']and baseline['primal_expectation']['ok']
 return {'version':'normalized-determinant-reference-v1','input_freeze_sha256':sha(packet/'prospective-freeze.json'),'reference_script_sha256':sha(Path(__file__)),'summary':summary,'all_reference_components_resolved':summary['unresolved']==0,'all_precision_gates_passed':summary['convergence_failures']==0,'recovery_baseline_id':'prior/regular/sphere','unique_fixture_count':len(rows),'coordinator_prospective_total_Jet_calls_with_one_recovery_after_each_rejection':len(rows)+summary['Jet_rejected'],'compiled_calls':0,'Atlas_imports':False,'new_core_execution':False,'cases':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.packet,a.root);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps(r['summary']));print('resolved',r['all_reference_components_resolved'],'converged',r['all_precision_gates_passed'])
