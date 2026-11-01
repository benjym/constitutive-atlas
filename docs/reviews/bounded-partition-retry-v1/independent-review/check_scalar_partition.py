"""Independent rational branch roots for the prospective synthetic fixture."""
from fractions import Fraction as F
import json
Eur,Ep=F(10),F(2)
h=F(50,64);loading=F(7,64)
def roots(stress,de):
    possible=[]
    for label,E in [('unload',Eur),('primary',Ep)]:
        out=stress+E*de
        if (out<h)==(label=='unload'):possible.append((label,out))
    return possible
assert not roots(F(0),loading)
# Ordinary binary recursion commits its first half, then encounters the gap.
first=roots(F(0),loading/2)
assert first==[('unload',F(35,64))]
assert not roots(first[0][1],loading/2)
# Alternative third, then halves of the remaining two-thirds, admits roots.
stress=F(0);labels=[]
for de in [loading/3]*3:
    candidates=roots(stress,de);assert len(candidates)==1
    label,stress=candidates[0];labels.append(label)
assert labels==['unload','unload','primary']
assert stress==F(77,96)>h
assert (Eur+Eur+Ep)/3==F(22,3)
print(json.dumps({'pass':True,'unsplit_no_root':True,
                  'alternative_branches':labels,'ideal_endpoint':str(stress),
                  'fixed_ideal_fraction_tangent':str(F(22,3)),
                  'scope':'exact rational fixture; binary split requires separate error audit'},indent=2))
