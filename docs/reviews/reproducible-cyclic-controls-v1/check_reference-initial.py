from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
import json,sys,random,struct
import reference as r
P=Path(__file__).parent;a,b=[json.loads((P/n).read_bytes())for n in('reference-p140.json','reference-p180.json')];checks=0;maximum=D(0)
with localcontext()as ctx:
 ctx.prec=140
 def walk(x,y):
  global checks,maximum
  if isinstance(y,dict):
   assert set(x)==set(y)
   for k in y:
    if k=='precision':continue
    walk(x[k],y[k])
  elif isinstance(y,list):
   assert len(x)==len(y)
   for u,v in zip(x,y):walk(u,v)
  elif isinstance(y,str):
   try:u,v=D(x),D(y)
   except Exception:assert x==y
   else:
    err=abs(u-v)/max(D(1),abs(u),abs(v));maximum=max(maximum,err);assert err<=D('1e-110');checks+=1
  else:assert x==y
 walk(a,b);assert not a['violations']and not b['violations'];checks+=1
 # Exact integer rounding ties incl signed underflow, plus independent host conversion sanity.
 for x,bits in[(F(1)+F(1,1<<53),0x3ff0000000000000),(F(1)+F(3,1<<53),0x3ff0000000000002),(F(1,1<<1075),0),(-F(1,1<<1075),1<<63),(F(3,1<<1075),2)]:assert r.bits(x)==bits;checks+=1
 random.seed(1205000)
 for i in range(2000):
  x=F(random.randrange(-10**8,10**8),1<<random.randrange(0,1100));host=struct.unpack('>Q',struct.pack('>d',float(x)))[0];assert r.bits(x)==host;checks+=1
 for n in range(1,5001):
  for cycles in(0,1,100):
   for i in(0,1,n//2,n):
    k,q,j=r.phase(n,cycles,i);assert 0<=k<n and 0<=q<=3 and 0<=j<=n;checks+=1
    assert (cycles*i)%n==k;checks+=1
  assert r.waveform(n,1,n)[0]==0;checks+=1
  if n%4==0:
   assert r.waveform(n,1,n//4)[0]==1 and r.waveform(n,1,n//2)[0]==0 and r.waveform(n,1,3*n//4)[0]==-1;checks+=1
 for args in((0,1,0),(5001,1,1),(5,-1,1),(5,101,1),(5,1,-1),(5,1,6)):
  try:r.phase(*args)
  except AssertionError:checks+=1
  else:raise AssertionError('invalid accepted')
print(json.dumps({'identity':'cyclic-controls-reference-selfcheck-v1','passed':True,'checks':checks,'maximum_precision_normalized_difference':str(maximum),'phase_cases':b['phase_cases'],'controls':b['controls'],'candidate_calls':0,'compiled_calls':0},indent=2))
