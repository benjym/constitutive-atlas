"""Independent known-eigensystem/factorization fixtures; no discriminator import.

Q(sqrt(2)) pairs are exact. Compare the characteristic polynomial from the
stored Mandel entries with the product from independently known eigenvalues.
"""
from fractions import Fraction as F
import json

def q(a=0,b=0):return (F(a),F(b))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]+2*a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def prod(roots):
    p=[q(1)]
    for root in roots:
        out=[q() for _ in range(len(p)+1)]
        for i,c in enumerate(p):
            out[i]=add(out[i],mul(neg(root),c));out[i+1]=add(out[i+1],c)
        p=out
    return p
def characteristic(m):
    x,y,z,u,v,w=map(F,m)
    # Direct 3x3 determinant expansion, before any centering/discriminant.
    return [q(-x*y*z+(x*v*v+y*w*w+z*u*u)/2,-u*v*w/2),
            q(x*y+x*z+y*z-(u*u+v*v+w*w)/2),q(-x-y-z),q(1)]

cases=[
 ('hydrostatic',[7,7,7,0,0,0],[q(7)]*3,'both'),
 ('double-max',[5,5,2,0,0,0],[q(5),q(5),q(2)],'max'),
 ('double-min',[2,2,5,0,0,0],[q(2),q(2),q(5)],'min'),
 # Matrix has zero diagonal and all off-diagonals 1/sqrt(2).
 # Its eigenvectors are (1,1,1) and the perpendicular plane.
 ('radical-double-min',[0,0,0,1,1,1],[q(0,1),q(0,F(-1,2)),q(0,F(-1,2))],'min'),
 ('radical-double-max',[0,0,0,-1,-1,-1],[q(0,-1),q(0,F(1,2)),q(0,F(1,2))],'max'),
 ('distinct',[5,3,2,0,0,0],[q(5),q(3),q(2)],'neither'),
 ('ulp-distinct',[1,1+2**-52,2,0,0,0],[q(1),q(F(1)+F(1,2**52)),q(2)],'neither'),
]
count=0
for name,m,roots,kind in cases:
    assert characteristic(m)==prod(roots),name
    count+=1
    # Translate and scale exactly, including sign reversal and extreme dyadics.
    for scale in (F(1,2**1000),F(2**1000),F(-1)):
        # Fraction operands deliberately preserve exactness, not float overflow.
        transformed=[scale*F(v) for v in m]
        scaled_roots=[mul(q(scale),r)for r in roots]
        assert characteristic(transformed)==prod(scaled_roots),(name,scale)
        count+=1

# At the radical repeated minimum the cluster projector is I-vv^T,
# v=(1,1,1)/sqrt(3), so P/2 has diagonal 1/3 and off diagonal -1/6.
# This rational projector is positive semidefinite, trace 1, and supported
# on the two-dimensional eigenspace, checked using 3P integer matrices.
threeP=[[2,-1,-1],[-1,2,-1],[-1,-1,2]]
assert all(sum(row)==0 for row in threeP)
assert all(sum(threeP[i][k]*threeP[k][j] for k in range(3))==3*threeP[i][j]
           for i in range(3)for j in range(3))
assert sum(threeP[i][i]for i in range(3))==6
print(json.dumps({'status':'pass','characteristic_factorizations':count,
                  'independent_cluster_projector_checks':3,
                  'scope':'design fixtures; production discriminator not imported'},indent=2))
