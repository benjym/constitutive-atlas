"""Source-only audit of reused uint32 limb formulas; not compiled-core execution.

No normalized-determinant fixture/reference oracle is constructed here.
"""
import json,random
B=1<<32; MASK=B-1

def limbs(n):
 a=[]
 while n:a.append(n&MASK);n>>=32
 return a

def integer(a):return sum(x<<(32*i) for i,x in enumerate(a))
def trim(a):
 while a and not a[-1]:a.pop()
 return a

def add(a,b):
 c=[0]*(max(len(a),len(b))+1);carry=0
 for i in range(len(c)-1):
  t=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)+carry
  assert 0<=t<1<<64
  c[i]=t&MASK;carry=t>>32
 c[-1]=carry
 return trim(c)

def subtract(a,b):
 assert integer(a)>=integer(b)
 c=[0]*len(a);borrow=0
 for i in range(len(a)):
  t=(b[i] if i<len(b) else 0)+borrow
  assert t<=B
  borrow=int(a[i]<t);c[i]=(a[i]-t)&MASK
 assert borrow==0
 return trim(c)

def shift(a,n):
 if not a:return []
 whole,rest=divmod(n,32);c=[0]*(len(a)+whole+bool(rest))
 for i,x in enumerate(a):
  c[i+whole]|=(x<<rest)&MASK
  if rest:c[i+whole+1]|=x>>(32-rest)
 return trim(c)

def multiply(a,b):
 if not a or not b:return []
 c=[0]*(len(a)+len(b))
 for i,x in enumerate(a):
  carry=0
  for j,y in enumerate(b):
   t=x*y+c[i+j]+carry
   assert 0<=t<1<<64
   c[i+j]=t&MASK;carry=t>>32
  assert c[i+len(b)]==0 # terminal slot untouched before assignment
  c[i+len(b)]=carry
 return trim(c)

def check():
 rng=random.Random(948529)
 samples=[0,1,MASK,B,B+1,B*B-1,B*B,B**4-1]
 samples += [rng.getrandbits(rng.randrange(1,257)) for _ in range(80)]
 counts=dict(add=0,subtract=0,multiply=0,shift=0)
 for x in samples:
  for y in samples:
   a,b=limbs(x),limbs(y)
   assert integer(add(a,b))==x+y;counts['add']+=1
   large,small=(a,b) if x>=y else (b,a)
   assert integer(subtract(large,small))==abs(x-y);counts['subtract']+=1
   assert integer(multiply(a,b))==x*y;counts['multiply']+=1
  for n in [0,1,31,32,33,1074,10499,20998]:
   assert integer(shift(limbs(x),n))==x<<n;counts['shift']+=1
 # Dense carry propagation near the conservative full comparison-square size.
 x=B**657-1;y=B**657-1
 assert integer(multiply(limbs(x),limbs(y)))==x*y;counts['multiply']+=1
 assert (B-1)**2+(B-1)+(B-1)==(1<<64)-1
 # Proof constants in README, expressed as integer inequalities.
 assert 3<4 and 45<64 and 81<128
 assert 5128-(-5371)==10499 and 2*10499==20998
 assert 20998<2**31 and 10742<2**31
 return {'kind':'source-only-limb-formula-and-bound-probes','seed':948529,'counts':counts,'failed':0,'scope':'Python translations of specific reused unsigned-limb formulas checked against Python integers; no compiled C++ or normalized-determinant oracle/results tested','bounds':{'input_quantum_exponent':-1074,'derivative_numerator_min_quantum_exponent':-4297,'boundary_times_denominator_min_quantum_exponent':-5371,'comparison_difference_bits_max':10499,'comparison_square_bits_max':20998,'dense_carry_probe_limbs':657}}

if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
