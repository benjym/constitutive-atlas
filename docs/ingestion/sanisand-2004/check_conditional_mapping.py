"""Exact conditional algebra, not a transcription of unavailable 1986 rules."""
from fractions import Fraction as F
import json


def dot(a, b):
    return sum((x*y for x,y in zip(a,b)), F(0))


def subtract(a,b):
    return tuple(x-y for x,y in zip(a,b))


def check():
    # Cartesian diagonal traceless tensors; all contractions exact, no Mandel sqrt2.
    n=(F(2,3),F(-1,3),F(-1,3))
    initial=(F(0),F(0),F(0))
    current=n
    image_initial=tuple(3*x for x in n)
    images=[image_initial,tuple(4*x for x in n),tuple(5*x for x in n)]
    rows=[]
    for name,image in zip(('fixed-image','moving-image-cancellation','moving-image-opposite-sign'),images):
        delta_initial=subtract(image_initial,initial)
        delta=subtract(image,current)
        lhs=dot(subtract(delta_initial,delta),n)
        state_term=dot(subtract(current,initial),n)
        image_term=dot(subtract(image_initial,image),n)
        assert lhs==state_term+image_term
        rows.append(dict(case=name,distance_denominator=str(lhs),state_denominator=str(state_term),image_motion_term=str(image_term)))
    assert rows[0]['distance_denominator']==rows[0]['state_denominator']=='2/3'
    assert rows[1]['distance_denominator']=='0' and rows[1]['state_denominator']=='2/3'
    assert rows[2]['distance_denominator']=='-2/3' and rows[2]['state_denominator']=='2/3'
    return {'kind':'conditional-exact-algebra-only','assumption':'delta = image - state in the same fixed coordinates; normal n held fixed','not_established':['1986 uses this mapping/sign/coordinate','2004 alpha and alpha_b identify these tensors','canonical reversal rules','physical reachability or material trajectories'],'cases':rows,'passed':3,'failed':0}


if __name__=='__main__':
    print(json.dumps(check(),indent=2,sort_keys=True))
