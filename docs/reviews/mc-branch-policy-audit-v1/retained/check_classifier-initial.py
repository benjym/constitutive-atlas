"""Independent exact Fraction audit; no Atlas or author-code imports/execution."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,itertools,collections,hashlib
Z=Q(0);ONE=Q(1)
def enc(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,(tuple,list)):return [enc(v)for v in x]
 if isinstance(x,dict):return {k:enc(v)for k,v in x.items()}
 return x
class Law:
 def __init__(self,K,G,s,d,c,cp):
  self.K,self.G,self.s,self.d,self.c,self.cp=map(Q,(K,G,s,d,c,cp))
  assert min(self.K,self.G,self.c)>0 and 0<self.s<1 and 0<self.d<1 and self.s*self.s+self.cp*self.cp==1 and self.cp>0
  K,G,s,d,c,cp=self.K,self.G,self.s,self.d,self.c,self.cp
  self.h=2*c*cp;self.A=2*(K-Q(2,3)*G)*d
  self.den={'face':4*K*d*s+4*G*(1+d*s/3),'left':4*K*d*s+G*(3-s-d+d*s/3),'right':4*K*d*s+G*(3+s+d+d*s/3),'apex':4*K*d*s}
  assert all(v>0 for v in self.den.values())
  assert self.den['face']==2*self.A*s+4*G*(1+d*s)
  assert self.den['left']==2*self.A*s+G*(1+d)*(1+s)+2*G*(1-d)*(1-s)
  assert self.den['right']==2*self.A*s+2*G*(1+d)*(1+s)+G*(1-d)*(1-s)
 def data(self,t):
  t1,t2,t3=map(Q,t);G,s,d,h=self.G,self.s,self.d,self.h
  assert t1>=t2>=t3
  a=(t1-t2)/(2*G*(1+d));b=(t2-t3)/(2*G*(1-d))
  l=(t1+t2-2*t3)/(2*G*(3-d));r=(2*t1-t2-t3)/(2*G*(3+d))
  assert l==((1+d)*a+2*(1-d)*b)/(3-d)
  assert r==(2*(1+d)*a+(1-d)*b)/(3+d)
  assert (a<r<l<b)if a<b else(b<l<r<a)if b<a else a==b==l==r
  n={'face':(1+s)*t1-(1-s)*t3-h,'left':(1+s)*(t1+t2)/2-(1-s)*t3-h,'right':(1+s)*t1-(1-s)*(t2+t3)/2-h,'apex':Q(2,3)*s*(t1+t2+t3)-h}
  roots={k:n[k]/self.den[k]for k in n}
  q=lambda branch,x:n[branch]-self.den[branch]*x
  assert q('face',a)==q('left',a)and q('face',b)==q('right',b)
  assert q('left',l)==q('apex',l)and q('right',r)==q('apex',r)
  return n,roots,(a,b,l,r)
 def classify(self,t):
  n,g,(a,b,l,r)=self.data(t)
  # Exact proposed classifier, distinct from independent interval oracle below.
  if n['face']<=0:return 'elastic',Z
  if g['apex']>=max(l,r):return 'apex',g['apex']
  if g['face']<min(a,b):return 'face',g['face']
  return ('left',g['left'])if a<b else('right',g['right'])
 def intervals(self,t):
  n,g,(a,b,l,r)=self.data(t)
  if n['face']<=0:return [('elastic',Z)]
  admissible={'face':0<g['face']<min(a,b),'left':g['left']>0 and a<=g['left']<l,'right':g['right']>0 and b<=g['right']<r,'apex':g['apex']>0 and g['apex']>=max(l,r)}
  return [(k,g[k])for k in admissible if admissible[k]]
 def returned(self,t,branch,g):
  t1,t2,t3=map(Q,t);A,G,d=self.A,self.G,self.d
  if branch=='elastic':return(t1,t2,t3)
  if branch=='face':return(t1-g*(A+2*G*(1+d)),t2-g*A,t3-g*(A-2*G*(1-d)))
  if branch=='left':return((t1+t2)/2-g*(A+G*(1+d)),)*2+(t3-g*(A-2*G*(1-d)),)
  if branch=='right':return(t1-g*(A+2*G*(1+d)),)+((t2+t3)/2-g*(A-G*(1-d)),)*2
  return(self.c*self.cp/self.s,)*3
 def check(self,t):
  branch,g=self.classify(t);accepted=self.intervals(t)
  assert accepted==[(branch,g)],(t,accepted,(branch,g))
  r=self.returned(t,branch,g)
  assert r[0]>=r[1]>=r[2]
  f=(1+self.s)*r[0]-(1-self.s)*r[2]-self.h
  if branch=='elastic':assert g==0 and f<=0
  else:
   assert g>0 and f==0
   v=tuple((t[i]-r[i]-g*self.A)/(2*self.G*g)for i in range(3))
   assert 1+self.d>=v[0]>=v[1]>=v[2]>=-1+self.d and sum(v)==2*self.d
   assert (v[0]-1-self.d)*(r[0]-r[1])==0 and (v[2]+1-self.d)*(r[1]-r[2])==0
   # Every selected projector is isolated, or no projector is needed.
   if branch=='face':assert t[0]>t[1]>t[2]
   if branch=='left':assert t[1]>t[2]
   if branch=='right':assert t[0]>t[1]
  return branch,g,r
 def translated(self,x,y,branch,g):
  # Set the branch's affine q(g)=0 by a hydrostatic translation; does not classify.
  t=(x+y,y,Z);n,_,_=self.data(t)
  m=(self.den[branch]*g-n[branch])/(2*self.s)
  return tuple(v+m for v in t)

def rotate(vals,U):return [[sum(vals[k]*U[i][k]*U[j][k]for k in range(3))for j in range(3)]for i in range(3)]
def grouped_check(t,r,branch):
 U=[[Q(1,9),Q(8,9),Q(4,9)],[Q(8,9),Q(1,9),-Q(4,9)],[-Q(4,9),Q(4,9),-Q(7,9)]]
 I=[[Q(i==j)for j in range(3)]for i in range(3)]
 assert rotate((ONE,ONE,ONE),U)==I
 pmax=rotate((ONE,Z,Z),U);pmin=rotate((Z,Z,ONE),U);direct=rotate(r,U)
 if branch=='face':grouped=[[r[1]*I[i][j]+(r[0]-r[1])*pmax[i][j]+(r[2]-r[1])*pmin[i][j]for j in range(3)]for i in range(3)]
 elif branch=='left':grouped=[[r[0]*I[i][j]+(r[2]-r[0])*pmin[i][j]for j in range(3)]for i in range(3)]
 elif branch=='right':grouped=[[r[2]*I[i][j]+(r[0]-r[2])*pmax[i][j]for j in range(3)]for i in range(3)]
 elif branch=='apex':grouped=[[r[0]*I[i][j]for j in range(3)]for i in range(3)]
 else:grouped=rotate(t,U)
 assert grouped==direct
 # At the proposed accepted Atlas stress S=-return(-trialAtlas), residual is zero.
 source_return=grouped;atlas_accepted=[[-v for v in row]for row in source_return]
 assert all(atlas_accepted[i][j]+source_return[i][j]==0 for i in range(3)for j in range(3))
 return direct

def main(source,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);source=Path(source)
 counts=collections.Counter();constructs=[];params=0
 for K,d,(s,cp),c in itertools.product([Q(1,1000),Q(1,3),ONE,Q(1000)],[Q(1,100),Q(1,3),Q(1,2),Q(99,100)],[(Q(3,5),Q(4,5)),(Q(5,13),Q(12,13)),(Q(9999,10001),Q(200,10001))],[ONE,Q(5)]):
  law=Law(K,ONE,s,d,c,cp);params+=1
  for m,x,y in itertools.product([Q(-100),Q(-5),Z,ONE,Q(5),Q(10),Q(100)],[Z,Q(1,100),ONE,Q(3),Q(10)],[Z,Q(1,100),ONE,Q(3),Q(10)]):
   t=(m+x+y,m+y,m);branch,_,_=law.check(t);counts['grid_'+branch]+=1;counts['grid_cases']+=1
  for a,b,label in [(ONE,Q(2),'left-path'),(Q(2),ONE,'right-path'),(ONE,ONE,'coincident-path'),(Z,ONE,'repeat-upper'),(ONE,Z,'repeat-lower'),(Z,Z,'hydro')]:
   x=2*law.G*(1+d)*a;y=2*law.G*(1-d)*b
   _,_,(_,_,l,r)=law.data((x+y,y,Z));M=max(l,r);first=min(a,b)
   cases=[('elastic-yield','face',Z,'elastic'),('apex-upper','apex',M,'apex'),('apex-interior','apex',M+ONE,'apex')]
   # Hydro at g=0 is elastic, not apex, by F<=0 ownership.
   if M==0:cases[1]=('hydro-yield','apex',Z,'elastic')
   if first>0:cases.append(('face-interior','face',first/2,'face'))
   if a<b:
    cases.extend([('face-left-equality','face',a,'left'),('left-interior','left',(a+l)/2,'left')])
   elif b<a:cases.extend([('face-right-equality','face',b,'right'),('right-interior','right',(b+r)/2,'right')])
   elif first>0:cases.append(('face-apex-equality','face',first,'apex'))
   for name,equation,g,want in cases:
    t=law.translated(x,y,equation,g);branch,actual,returned=law.check(t)
    assert branch==want,(label,name,branch,want)
    grouped_check(t,returned,branch);counts['constructed_cases']+=1;counts['constructed_'+branch]+=1
    if params==1:constructs.append(enc({'path':label,'name':name,'branch':branch,'trial':t,'gamma':actual,'returned':returned}))
 original=json.loads((source/'results.json').read_text());p=original['parameters'];law=Law(*[Q(p[k])for k in('K','G','sin_phi','sin_psi','c','cos_phi')])
 for cert in original['certificates']:
  t=tuple(map(Q,cert.get('source_tension_principal_trial',cert.get('trial'))));branch,g,r=law.check(t)
  assert (branch,g,r)==(cert['branch'],Q(cert['gamma']),tuple(map(Q,cert.get('source_tension_return',cert.get('return')))))
  grouped_check(t,r,branch);counts['original_certificates']+=1
 result={'identity':'mc-branch-exact-independent-audit-v1','parameter_sets':params,'counts':dict(counts),'constructed_examples_first_parameters':constructs,'failed':0,'compiled_observations':0,'scientific_admission':False,'limits':['Finite exact sampling corroborates but does not replace algebraic proof','No floating classifier/decomposition/AD execution','Dense rational Cartesian reconstruction, not stored-Mandel floating fixtures','Strict positive source domain preserved']}
 (out/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='constructed_examples_first_parameters'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('out');a=p.parse_args();main(a.source,a.out)
