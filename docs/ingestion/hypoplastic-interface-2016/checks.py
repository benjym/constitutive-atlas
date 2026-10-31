"""Exact rational checks of thesis reduced algebra; no constitutive rate implementation."""
from fractions import Fraction as F
import json
from pathlib import Path

def embed(x):
 a,b,c,d=x;return [[a,c,d],[c,b,0],[d,0,b]]
def mul(a,b):return [[sum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def determinant(a):return sum(a[0][j]*(a[1][(j+1)%3]*a[2][(j+2)%3]-a[1][(j+2)%3]*a[2][(j+1)%3])for j in range(3))
def reduced_dot(x,y):
 a,b,c,d=x;e,f,g,h=y;return [a*e+c*g+d*h,b*f+c*g,a*g+c*f,d*e+b*h]
def run():
 checked=0
 for k in range(1,25):
  x=[F(k+1,3),F(k+2,5),F(k-7,11),F(9-k,13)];y=[F(k-2,7),F(k,9),F(3-k,5),F(k+3,17)]
  a,b=embed(x),embed(y)
  assert sum(a[i][i]for i in range(3))==x[0]+2*x[1]
  assert determinant(a)==x[0]*x[1]**2-x[1]*(x[2]**2+x[3]**2)
  assert sum(a[i][j]*b[i][j]for i in range(3)for j in range(3))==x[0]*y[0]+2*sum(x[i]*y[i]for i in range(1,4))
  # Printed4th-order identity under weighted contraction must return x.
  assert [x[0],2*F(1,2)*x[1],2*F(1,2)*x[2],2*F(1,2)*x[3]]==x
  checked+=4
 x=[2,3,5,7];cart=mul(embed(x),embed(x));red=reduced_dot(x,x)
 assert red==[78,34,25,35]
 assert cart[1][1]==34 and cart[2][2]==58 and cart[1][2]==35
 assert embed(red)!=cart
 # Exact power conjugacy for zero in-plane stretching; engineering shears not Mandel shears.
 s=[F(11),F(7),F(3),F(5)];d=[F(2),0,F(13,2),F(17,2)]
 assert s[0]*d[0]+2*sum(s[i]*d[i]for i in range(1,4))==s[0]*2+s[2]*13+s[3]*17
 return {'version':'interface2016-algebra-checks-0.1','exact_scalar_checks':checked+4,'source':'thesis5.1–5.4,5.23–5.34','reduced_product_witness':{'x':x,'reduced_dot':red,'cartesian_square':cart,'equal':False},'constitutive_rate_checked':False,'compiled_execution':False,'admission':False}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--check',type=Path);a=p.parse_args();r=run()
 if a.check and json.loads(a.check.read_text())!=r:raise SystemExit('retained check mismatch')
 if a.output:
  if a.output.exists():raise SystemExit('fresh output required')
  a.output.write_text(json.dumps(r,indent=2)+'\n')
 print('PASS',r['exact_scalar_checks'],'exact algebra checks; reduced product nonclosure retained')
