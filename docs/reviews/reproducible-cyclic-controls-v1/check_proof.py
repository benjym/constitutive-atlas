"""Exact rational certificate for the proposed analytic error bound."""
from fractions import Fraction as F
import math,json
u=F(1,1<<53)
def atan_bounds(n,count):
 x=F(1,n);s=F(0)
 for k in range(count):s+=(-1)**k*x**(2*k+1)/F(2*k+1)
 nextterm=(-1)**count*x**(2*count+1)/F(2*count+1)
 return min(s,s+nextterm),max(s,s+nextterm)
a,b=atan_bounds(5,150);c,d=atan_bounds(239,50);pi_low,pi_high=16*a-4*d,16*b-4*c;pi2=F.from_float(float.fromhex('0x1.921fb54442d18p+0'));checks=0
assert pi_low<pi_high and max(abs(pi2-pi_low/2),abs(pi2-pi_high/2))<u;checks+=1
X=F(8,5);assert pi2*(1+u)**2<X;checks+=1
argbound=u+pi2*(2*u+u*u);assert argbound<5*u;checks+=1
S=sum(X**(2*n+1)/F(math.factorial(2*n+1))for n in range(12));assert S<F(12,5);checks+=1
remainder=X**25/F(math.factorial(25));assert remainder<F(1,10**20);checks+=1
gamma44=44*u/(1-44*u);total=argbound+gamma44*S+remainder;assert total<128*u;checks+=1
range_margin=F(1,2*5000**2);assert 128*u<range_margin;checks+=1
# Smallest nonzero argument and the degree23 term remain normal by many orders.
xmin=F(1,5000)*F(3,2)*(1-u)**2;minterm=xmin**23/F(math.factorial(23))*(1-44*u);assert minterm>F(1,1<<1022);checks+=1
assert 100*5000<2**31 and 4*4999<2**31;checks+=1
assert 128*u+u*(1+128*u)<130*u;checks+=1
D=lambda x:float(x)
print(json.dumps({'identity':'cyclic-rne12-rational-bound-certificate-v1','passed':True,'checks':checks,'pi_constant_error_less_than_u':True,'argument_error_bound':str(argbound),'truncation_bound':str(remainder),'total_wave_error_bound':str(total),'total_wave_error_bound_decimal_approx':D(total),'declared_wave_bound':D(128*u),'range_margin':D(range_margin),'candidate_calls':0,'compiled_calls':0},indent=2))
