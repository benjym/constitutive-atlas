from fractions import Fraction as F
import json
# Independent directional derivative check with unequal component scales.
s=[F(2),F(3),F(5)]
J=[F(7),F(-11),F(13)]
jet=[J[k]*s[k] for k in range(3)]
for j in range(3):
 direction=[s[j]*(F(k==j)-F(1,3)) for k in range(3)]
 assert sum(direction)==0
 expected=sum(J[k]*direction[k] for k in range(3))
 actual=jet[j]-sum(s[j]*jet[k]/(3*s[k]) for k in range(3))
 assert expected==actual
# Rotate a symmetric tensor with R=[[0,1,0],[-1,0,0],[0,0,1]].
R=[[0,1,0],[-1,0,0],[0,0,1]]
A=[[F(28,100),F(1,100),F(2,100)],[F(1,100),F(-14,100),F(3,100)],[F(2,100),F(3,100),F(-14,100)]]
B=[[sum(R[i][k]*A[k][l]*R[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
a=[A[0][0],A[1][1],A[2][2],A[0][1],A[0][2],A[1][2]]
b=[B[0][0],B[1][1],B[2][2],B[0][1],B[0][2],B[1][2]]
assert b==[a[1],a[0],a[2],-a[3],a[5],-a[4]]
print(json.dumps({'status':'passed','scaled_projection_directions':3,'tensor_rotation':'R A R^T verified exactly','compiled_calls':0}))
