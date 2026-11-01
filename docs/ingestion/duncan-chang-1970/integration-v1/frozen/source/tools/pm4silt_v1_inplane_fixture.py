"""Source Eqs1-4 algebra only; not a PM4Silt constitutive update.

Compression-positive SI input project convention; symmetric Cartesian xy shear.
No 3D embedding, parameter defaults, initialization, yield return or DLL execution.
"""
import math

def invariants(sigma):
    if type(sigma) is not list or len(sigma)!=3 or any(type(x)not in(int,float)or not math.isfinite(x)for x in sigma):
        raise ValueError('three finite Cartesian [xx,yy,xy] entries required')
    p=sigma[0]/2+sigma[1]/2
    if not math.isfinite(p) or p<=0:raise ValueError('positive finite in-plane mean required for this diagnostic')
    s=[sigma[0]-p,sigma[1]-p,sigma[2]]
    r=[x/p for x in s]
    j2=r[0]*r[0]+r[1]*r[1]+2*r[2]*r[2]
    if any(not math.isfinite(x)for x in s+r+[j2]):raise ValueError('nonrepresentable diagnostic')
    return dict(p=p,s=s,r=r,r_double_contraction=j2)
