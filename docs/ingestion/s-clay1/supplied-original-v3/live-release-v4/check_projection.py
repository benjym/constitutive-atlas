"""Exact independent tangent-space check; no constitutive/compiled calls."""
from fractions import Fraction as F
import json
P=[[F(i==j)-F(1,3) for j in range(3)] for i in range(3)]
assert all(sum(row)==0 for row in P)
assert [[sum(P[i][k]*P[k][j] for k in range(3)) for j in range(3)] for i in range(3)]==P
assert all(P[i][j]==P[j][i] for i in range(3) for j in range(3))
assert sum(P[i][i] for i in range(3))==2
# A 90-degree xy frame rotation preserves the trace and fabric norm.
fabric=[F(28,100),-F(14,100),-F(14,100),F(1,100),F(2,100),F(3,100)]
rot=[fabric[1],fabric[0],fabric[2],-fabric[3],fabric[5],-fabric[4]]
assert sum(fabric[:3])==sum(rot[:3])==0
assert sum(x*x for x in fabric)==sum(x*x for x in rot)
print(json.dumps({'status':'pass','trace_free_projector_rank':2,'idempotent':True,'fabric_rotation_trace_and_norm_preserved':True,'compiled_calls':0},indent=2))
