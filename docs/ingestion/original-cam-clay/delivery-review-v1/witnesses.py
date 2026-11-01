"""Algebraic witnesses only; no constitutive candidate or compiled calls."""
import json
import math
from pathlib import Path

M, p, pc = 1.2, 100000.0, 200000.0
radius = -M*p*math.log(p/pc)
interior = [{'q':q, 'f':abs(q)+M*p*math.log(p/pc)} for q in (0.,10000.)]
assert all(row['f'] < 0 for row in interior)
# Both admit zero total strain, unchanged p/v/packing and no plastic flow.
# A zero-plastic predictor's shear residual is de_s - (a-b).
# With a single active sign and a replaced multiplier equation a=0,
# the local (q,a) Jacobian is [[0,-1],[0,1]], rank one.
predictor_jacobian = [[0.,-1.],[0.,1.]]
assert predictor_jacobian[0][0]*predictor_jacobian[1][1]-predictor_jacobian[0][1]*predictor_jacobian[1][0] == 0
cone=[]
for a,b in ((1.,0.),(0.,1.),(.5,.5)):
    ds, dv = a-b, M*(a+b)
    assert abs(ds) <= dv/M
    cone.append({'a':a,'b':b,'plastic_distortion':ds,'plastic_volume':dv,
                 'stress_work_over_p':dv,'smooth_abs_shear_loss_over_p':M*abs(ds)})
# With prescribed nonzero distortion, a>0 forces f+=0. Thus from a strict
# interior initial state the positive-strain response reaches yield as ds -> 0+.
report={'scope':'analytical counterexamples; no update implementation',
        'interior_zero_increment_nonuniqueness':{'p':p,'pc':pc,'M':M,'admissible_q_radius':radius,'states':interior},
        'automatic_zero_plastic_predictor':{'jacobian_q_a':predictor_jacobian,'rank':1,'unknowns':2},
        'vertex_normal_cone':cone,'compiled_calls':0}
Path(__file__).with_name('witnesses.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: two admissible interior hold stresses, singular predictor block, and three cone witnesses')
