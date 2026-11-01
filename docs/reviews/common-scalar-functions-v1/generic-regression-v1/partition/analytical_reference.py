"""Exact rational source equations only; no Atlas imports or compiled execution."""
from fractions import Fraction as Q
import json

def attempt(x,h,d,depth,work,budget):
 if work[0]>=budget:return None
 for E in (10,2):
  y=x+E*d
  if (y<h)==(E==10):work[0]+=1;return y,max(h,y),[(d,E)]
 if depth>=14:return None
 a=attempt(x,h,d/2,depth+1,work,budget)
 if a is None:return None
 b=attempt(a[0],a[1],d/2,depth+1,work,budget)
 if b is None:return None
 return b[0],b[1],a[2]+b[2]

def reference():
 h=Q(50,64);de=Q(7,64);work=[0];original=attempt(Q(0),h,de,0,work,20000);first=work[0]
 a=attempt(Q(0),h,de/3,1,work,20000);b=attempt(a[0],a[1],de*2/3,1,work,20000);leaves=a[2]+b[2]
 return dict(original_failed=original is None,original_tentative=first,committed=len(leaves),total_work=work[0],endpoint=str(b[0]),tangent=str(sum(d/de*E for d,E in leaves)),leaves=[dict(increment=str(d),modulus=E) for d,E in leaves])
if __name__=='__main__':print(json.dumps(reference(),indent=2))
