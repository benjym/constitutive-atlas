"""Independent Cartesian Decimal/cofactor references with rational sqrt2 enclosures.
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

def scaled(a,b):return max(abs(x-y)/max(D(1),abs(x),abs(y))for x,y in zip(a,b))
def run(packet,root):
 freeze=json.loads((packet/'prospective-freeze.json').read_text())
 for n,s in freeze['files'].items():assert sha(root/n)==s
 rows=[];summary={'cases':0,'accepted':0,'nonfinite_rejected':0,'rounded_overflow_rejected':0,'unresolved':0,'decimal_convergence_failures':0,'certified_components':0,'exact_rational_components':0}
 for case in freeze['cases']:
  row={k:case[k]for k in ('id','values','seeds','tags')};summary['cases']+=1
  try:v=list(map(parse,case['values']));s=[list(map(parse,r))for r in case['seeds']];assert len(v)==6 and len(s)==6 and all(len(r)==38 for r in s)
  except ValueError:
   row['expectation']={'ok':False,'reason':'nonfinite-input-or-seed','value':None,'derivatives':[None]*38,'unchanged_output':True};summary['nonfinite_rejected']+=1;rows.append(row);continue
  precision={p:decimal_cartesian(v,s,p)for p in freeze['policy']['precision_digits']};algebraic=exact_cartesian(v,s);certs=[certified(q)for q in algebraic]
  with localcontext()as ctx:ctx.prec=340;error=scaled(precision[160],precision[320]);converged=error<=D('1e-120')
  row['precision_check']={'digits':[160,320],'max_scaled_component_difference':str(error),'passed':converged,'decimal_values':{str(p):list(map(str,values))for p,values in precision.items()}}
  if not converged:summary['decimal_convergence_failures']+=1
  row['rounding_certificates']=certs
  if not all(c['certified']for c in certs):row['expectation']={'ok':None,'reason':'unresolved-reference'};summary['unresolved']+=1
  elif any(c['overflow']for c in certs):
   row['expectation']={'ok':False,'reason':'rounded-output-overflow','overflow_components':[i-1 for i,c in enumerate(certs)if c['overflow']],'value':None,'derivatives':[None]*38,'unchanged_output':True};summary['rounded_overflow_rejected']+=1
  else:
   row['expectation']={'ok':True,'value':certs[0]['value'],'value_hex':certs[0]['hex'],'derivatives':[c['value']for c in certs[1:]],'derivatives_hex':[c['hex']for c in certs[1:]],'canonical_positive_zero':True};summary['accepted']+=1
  summary['certified_components']+=sum(c['certified']for c in certs);summary['exact_rational_components']+=sum(c.get('method')=='exact-rational-nearest-even'for c in certs)
  # Retain exact Cartesian field values so independent bounds can be reconstructed.
  row['exact_cartesian_algebraic_components']=[q.json()for q in algebraic]
  rows.append(row)
 accepted={r['id']:r for r in rows if r['expectation'].get('ok')is True}
 assert accepted['regular/mixed']['expectation']['value_hex']==accepted['exact-covariance/signed-reflection']['expectation']['value_hex']
 return {'version':'symmetric-determinant-reference-v1','input_freeze_sha256':sha(packet/'prospective-freeze.json'),'reference_script_sha256':sha(Path(__file__)),'summary':summary,'all_reference_components_resolved':summary['unresolved']==0,'all_decimal_convergence_passed':summary['decimal_convergence_failures']==0,'compiled_calls':0,'atlas_imports':False,'cases':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.packet,a.root);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps(r['summary']));print('all resolved',r['all_reference_components_resolved'],'converged',r['all_decimal_convergence_passed'])
