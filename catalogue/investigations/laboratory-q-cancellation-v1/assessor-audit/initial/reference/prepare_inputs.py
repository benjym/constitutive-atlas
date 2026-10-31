from pathlib import Path
import math,struct,json
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
P=Path(__file__).parent;cases=[]
def bits(x):return struct.pack('>d',x).hex()
def add(name,v,category,provenance='analytic stored-input corpus'):
 assert len(v)==6 and all(math.isfinite(x)and abs(x)<=1e300 for x in v)
 cases.append({'id':name,'category':category,'input_bits':[bits(x)for x in v],'input_hex':[x.hex()for x in v],'provenance':provenance})
sub=float.fromhex('0x0.0000000000001p-1022');normal=float.fromhex('0x1p-1022')
for label,x in [('zero',0.),('negative-zero',-0.),('one',1.),('minus-one',-1.),('100k',100000.),('large',1e300),('negative-large',-1e300),('tiny',1e-300),('normal-min',normal),('subnormal-min',sub),('observed-native',float.fromhex('0x1.66b187563dbbap+18')),('observed-wasm',float.fromhex('0x1.66b187563dbb7p+18'))]:
 add('isotropic-'+label,[x,x,x,0.,0.,0.],'exact-isotropic','stored-value analytic corpus; two observed diagonals copied from parent task, not rerun')
for label,x in [('100k',100000.),('large',1e300),('tiny',1e-300),('normal-min',normal),('subnormal-min',sub)]:
 up=math.nextafter(x,math.inf);down=math.nextafter(x,-math.inf)
 if up<=1e300:add('near-isotropic-one-ulp-'+label,[up,x,x,0.,0.,0.],'near-isotropic')
 add('near-isotropic-down-'+label,[x,down,x,0.,0.,0.],'near-isotropic')
for name,v in [('diagonal',[300000.,200000.,100000.,0.,0.,0.]),('mixed-scale',[1e300,1.,-1e300,0.,0.,0.]),('tiny-diagonal',[sub,0.,-sub,0.,0.,0.]),('all-shears',[0.,0.,0.,1e5,-2e5,3e5]),('large-shears',[1e300,0.,-1e300,1e300,-1e300,1e300]),('tiny-shears',[0.,0.,0.,sub,-sub,sub]),('hydro-plus-tiny-shear',[1e300,1e300,1e300,sub,0.,0.]),('hydro-plus-unit-shear',[1e300,1e300,1e300,1.,0.,0.])]:add(name,v,'diagonal/shear/mixed')
for label,x in [('one',1.),('large',1e300),('tiny',1e-300),('subnormal-min',sub)]:add('pure-mandel-shear-'+label,[0.,0.,0.,x,0.,0.],'pure-shear')
# Rational orthogonal rotations in Cartesian basis; store all resulting rounded Mandel components.
for name,R in [('planar',[[F(3,5),F(-4,5),F(0)],[F(4,5),F(3,5),F(0)],[F(0),F(0),F(1)]]),('spatial',[[F(1,9),F(8,9),F(4,9)],[F(8,9),F(1,9),F(-4,9)],[F(-4,9),F(4,9),F(-7,9)]])]:
 assert all(sum(R[i][k]*R[j][k]for k in range(3))==int(i==j)for i in range(3)for j in range(3))
 diag=[F(300000),F(200000),F(100000)];A=[[sum(R[i][k]*diag[k]*R[j][k]for k in range(3))for j in range(3)]for i in range(3)]
 with localcontext()as ctx:
  ctx.prec=150;sqrt2=D(2).sqrt();v=[float(A[i][i])for i in range(3)]+[float(D(A[i][j].numerator)/D(A[i][j].denominator)*sqrt2)for i,j in [(0,1),(1,2),(0,2)]]
 add('rounded-rotation-'+name,v,'rounded-rotation','Rational orthogonal rotation of diag300000,200000,100000; exact Cartesian rational entries then each Mandel component rounded independently. Reference targets stored tensor, not unrounded ideal.')
(P/'inputs.json').write_text(json.dumps({'identity':'laboratory-q-stored-binary64-inputs-v1','cases':cases},indent=2)+'\n');print(len(cases),'source-only inputs prepared; no q reference computed')
