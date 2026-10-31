"""Prospective source-reference-only interval eligibility. Never imports Atlas.
Bounds constitute a falsifiable backend contract, not a universal error theorem.
"""
from decimal import Decimal as D,localcontext
from pathlib import Path
import json,gzip,sys,hashlib,collections
EPS=D(2)**-52;SUB=D(2)**-1074;MAX=D.from_float(sys.float_info.max)
class I:
 def __init__(self,a,b=None):self.a=D(a);self.b=D(a if b is None else b)
 def __add__(self,o):
  o=asI(o);return rounded(self.a+o.a,self.b+o.b)
 __radd__=__add__
 def __neg__(self):return I(-self.b,-self.a)
 def __sub__(self,o):return self+-asI(o)
 def __rsub__(self,o):return asI(o)+-self
 def __mul__(self,o):
  o=asI(o);v=[a*b for a in(self.a,self.b)for b in(o.a,o.b)];return rounded(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,o):
  o=asI(o)
  if o.a<=0<=o.b:raise ArithmeticError('denominator enclosure contains zero')
  v=[a/b for a in(self.a,self.b)for b in(o.a,o.b)];return rounded(min(v),max(v))
 def pair(self):return [str(self.a),str(self.b)]
def asI(x):return x if isinstance(x,I)else I(x)
def rounded(a,b):
 # Full eps, not unit roundoff, and full minsub, intentionally conservative.
 r=max(abs(a),abs(b))*EPS+SUB;return I(a-r,b+r)
def exacthex(s):return D.from_float(float.fromhex(s))
def norm(v):return sum(x*x for x in v).sqrt()
def maxI(a,b):return I(max(a.a,b.a),max(a.b,b.b))
def minI(a,b):return I(min(a.a,b.a),min(a.b,b.b))
def lt(a,b):return ([True]if a.b<b.a else[False]if a.a>=b.b else[False,True])
def le(a,b):return ([True]if a.b<=b.a else[False]if a.a>b.b else[False,True])
def ge(a,b):return le(b,a)
def possible(v):
 F,ga,gs,a,b,L,R=[v[k]for k in('ftrial','class_ga','class_gs','gsl','gsr','gla','gra')];out=set()
 for elastic in le(F,I(0)):
  if elastic:out.add('elastic');continue
  for apex in ge(ga,maxI(L,R)):
   if apex:out.add('apex');continue
   for face in lt(gs,minI(a,b)):
    if face:out.add('face');continue
    for left in lt(a,b):out.add('left'if left else'right')
 return sorted(out)
def item(c,r):
 co=r['coefficients'];p={}
 for k in('K','G'):
  x=D(co[k]);rad=abs(x)*(8*EPS/(1-8*EPS))+SUB;p[k]=I(x-rad,x+rad)
 for k in('sf','sd','cf'):
  x=D(co[k]);p[k]=I(x-4*EPS,x+4*EPS)
 p['c']=I(exacthex(c['parameters']['c']));K,G,s,d,cf,cv=[p[k]for k in('K','G','sf','sd','cf','c')]
 loading=[I(exacthex(x))for x in c['loading']];parent=[I(exacthex(x))for x in c['parent']]
 trace=loading[0]+loading[1]+loading[2]
 trial=[-(parent[k]+K*trace+2*G*(loading[k]-trace/3))if k<3 else-(parent[k]+2*G*loading[k])for k in range(6)]
 t=list(map(D,r['trial_source_mandel']));n=norm(t)
 error=norm([max(abs(q.a-v),abs(q.b-v))for q,v in zip(trial,t)])
 eig=list(map(D,r['eigenvalues']));radius=error+512*EPS*(n+error)+2*SUB
 # Exact diagonal fastpath cannot mix coordinate eigenvalues; order intervals conservatively.
 if all(q.a<=0<=q.b for q in trial[3:])and all(x==0 for x in t[3:]):
  a=sorted([q.a for q in trial[:3]],reverse=True);b=sorted([q.b for q in trial[:3]],reverse=True);v=[I(x,y)for x,y in zip(a,b)]
 else:v=[I(x-radius,x+radius)for x in eig]
 v1,v2,v3=v;x,y=v1-v2,v2-v3
 h=2*cv*cf;aa=2*(K-2*G/3)*d
 ds=4*K*d*s+4*G*(1+d*s/3);dl=4*K*d*s+G*(3-s-d+d*s/3);dr=4*K*d*s+G*(3+s+d+d*s/3);da=4*K*d*s
 F=(1+s)*v1-(1-s)*v3-h
 q=dict(K=K,G=G,sf=s,sd=d,cf=cf,h=h,aa=aa,ds=ds,dl=dl,dr=dr,da=da,v1=v1,v2=v2,v3=v3,ftrial=F,gsl=x/(2*G*(1+d)),gsr=y/(2*G*(1-d)),gla=(x+2*y)/(2*G*(3-d)),gra=(2*x+y)/(2*G*(3+d)),class_ga=(F-(1+s/3)*x-(1-s/3)*y)/da,class_gs=F/ds)
 allowed=possible(q);S=D(r['stress_scale']);Dsc=list(map(D,r['direction_scales']));branches={};reasons=[]
 for branch in allowed:
  b=r['branches'][branch];gaps=list(map(D,r['eigen_gaps']));needed={'elastic':[],'face':[0,1],'left':[1],'right':[0],'apex':[]}[branch]
  gap=min([gaps[i]for i in needed],default=n or D(1));glow=gap-2*radius;threshold=1024*EPS*(n+error)
  problems=[]
  if b['status']!='defined':problems.append('mathematically-undefined-selected-repeated-spectrum')
  if needed and glow<=threshold:problems.append('selected-gap-not-certified-above-numerical-threshold')
  if b['status']=='defined':
   values=[D(x)for x in b['residual']]+[D(x)for a in b['directions']for x in a['residual']]
   if any(abs(x)>MAX for x in values):problems.append('reference-value-or-direction-outside-binary64')
   if branch!='elastic'and D(b['gamma'])<0:problems.append('adjacent-canonical-branch-negative-multiplier')
  condition=D(1)if not needed else 1+n/max(gap,D('1e-10000'))
  # Frozen proposed accuracy contracts, expressly not proved worst-case guarantees.
  branches[branch]={'mathematically_defined':b['status']=='defined','gap':str(gap),'gap_lower_enclosure':str(glow),'resolution_threshold_upper':str(threshold),'failure_eligibility_reasons':problems,'value_norm_budget':str(32768*EPS*S*condition+2*SUB),'direction_norm_budgets':[str(262144*EPS*z*condition*condition+2*SUB)for z in Dsc],'condition_factor':str(condition)}
  reasons.extend(problems)
 # Severe material rounding: physically valid sine can round1; no generic failure pass without witness.
 if s.a<=0 or s.b>=1 or d.a<=0 or d.b>=1:reasons.append('coefficient-domain-near-rounding-endpoint')
 core=not reasons
 mixed='mixed-scale-middle'in c['id']
 return {'id':c['id'],'canonical_branch':r['selected_branch'],'eligible_branches':allowed,'must_succeed':core,'coverage_class':'required-success'if core else'conditional-numerical-coverage-gap','reasons':sorted(set(reasons)),'trace_envelopes':{k:x.pair()for k,x in q.items()},'trial_error_norm':str(error),'eigenvalue_radius_global':str(radius),'branches':branches,'current_basis_columns_exact_identity':[0,1,2,3,4,5],'mixed_component_gate':{'middle_index':1,'budget':'128*eps*abs(reference residual middle)+2*minsub','require_zero_offdiagonal_exact':True}if mixed else None}
def run(inputs,reference):
 raw=Path(inputs).read_bytes();data=json.loads(raw);ref=json.loads(gzip.decompress(Path(reference).read_bytes()));assert ref['input_sha256']==hashlib.sha256(raw).hexdigest();out=[]
 with localcontext()as ctx:
  ctx.prec=160
  for c,r in zip(data['cases'],ref['cases']):
   assert c['id']==r['id']
   try:out.append(item(c,r['canonical']))
   except ArithmeticError as e:out.append({'id':c['id'],'must_succeed':False,'coverage_class':'interval-unresolved','reason':str(e)})
 counts=collections.Counter(x['coverage_class']for x in out);coverage=collections.Counter(x['canonical_branch']for x in out if x['must_succeed']);assert set(coverage)=={'elastic','face','left','right','apex'}if len(out)>2 else True
 return {'identity':'mc-prospective-source-interval-policy-table-v1','candidate_calls':0,'compiled_observations':0,'input_sha256':hashlib.sha256(raw).hexdigest(),'reference_sha256':hashlib.sha256(Path(reference).read_bytes()).hexdigest(),'counts':dict(counts),'required_success_canonical_branch_counts':dict(coverage),'cases':out}
if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
