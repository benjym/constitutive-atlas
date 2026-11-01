"""Exact scalar analogue of selected-tie max-history departure; no Atlas import."""
from fractions import Fraction as F
import json
def residual(x,h):return (x-1,h-abs(x))
def norm(r):return max(map(abs,r))
initial=(F(0),F(0));initial_error=norm(residual(*initial))
# At x=0 the selected derivative of abs(x) is zero, so delta=(1,0).
for k in range(12):
    alpha=F(1,2**k);trial=(alpha,F(0))
    assert trial[1]<abs(trial[0])
# Full step is not strict descent; half-step is, despite infeasible history.
trial=(F(1,2),F(0))
assert norm(residual(*trial))==initial_error/2
# At x>0 the Newton system is [[1,0],[-1,1]].
# Residual at trial is (-1/2,-1/2), yielding delta=(1/2,1).
endpoint=(trial[0]+F(1,2),trial[1]+1)
assert residual(*endpoint)==(0,0)
assert endpoint[1]>=abs(endpoint[0])
# Removing trial feasibility alone cannot authorize an infeasible root:
# the separate final constraint still rejects h=0 at the root x=1.
assert not F(0)>=abs(F(1))
print(json.dumps({'pass':True,'blocked_positive_trial_fractions_checked':12,
                  'strict_descent_outside_solution_set':True,
                  'endpoint':list(map(str,endpoint)),
                  'scope':'exact scalar analogue; no compiled/model execution'},indent=2))
