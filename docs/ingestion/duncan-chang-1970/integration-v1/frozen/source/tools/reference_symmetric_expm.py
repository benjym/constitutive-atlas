"""Independent stdlib Decimal Cartesian expm/Fréchet corpus, no Atlas imports."""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path

VERSION='symmetric-expm-decimal-reference-v1'
PRECISIONS=(100,160)

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def zero():return [[Decimal(0)for _ in range(3)]for _ in range(3)]
def identity():return [[Decimal(i==j)for j in range(3)]for i in range(3)]
def add(a,b):return [[a[i][j]+b[i][j]for j in range(3)]for i in range(3)]
def scale(a,b):return [[x*b for x in row]for row in a]
def mul(a,b):return [[sum((a[i][k]*b[k][j]for k in range(3)),Decimal(0))for j in range(3)]for i in range(3)]
def maximum(a):return max(abs(x)for row in a for x in row)
def mandel(a,sqrt2):return [a[0][0],a[1][1],a[2][2],sqrt2*(a[0][1]+a[1][0])/2,sqrt2*(a[1][2]+a[2][1])/2,sqrt2*(a[0][2]+a[2][0])/2]
def cart(v,sqrt2):
    x,y,z,u,v,w=v
    return [[x,u/sqrt2,w/sqrt2],[u/sqrt2,y,v/sqrt2],[w/sqrt2,v/sqrt2,z]]

def oracle(values,precision=160):
    if type(values)is not list or len(values)!=6 or any(type(v)is not float or not math.isfinite(v)for v in values):raise ValueError('six finite actual binary64 floats required')
    if type(precision)is not int or precision<60:raise ValueError('precision>=60 required')
    with localcontext()as context:
        context.prec=precision
        sqrt2=Decimal(2).sqrt()
        A=cart([Decimal.from_float(v)for v in values],sqrt2)
        # Operator corpus support is exact Mandel Frobenius <=64. Decimal avoids
        # false exact-spectrum assumptions and intermediate binary64 overflow.
        norm2=sum((Decimal.from_float(v)**2 for v in values),Decimal(0))
        if norm2>Decimal(64)**2:raise ValueError('outside exact binary64 Mandel Frobenius64 support')
        B=A;s=0
        while max(sum(abs(x)for x in row)for row in B)>Decimal(1)/8:
            B=scale(B,Decimal(1)/2);s+=1
        factor=Decimal(2)**(-s)
        H=[]
        for k in range(6):
            seed=[Decimal(int(j==k))for j in range(6)]
            H.append(scale(cart(seed,sqrt2),factor))
        term=identity();total=identity();directions=[zero()for _ in range(6)];jac=[zero()for _ in range(6)]
        threshold=Decimal(10)**(-(precision-25));consecutive=0
        for k in range(1,4097):
            previous=term
            directions=[scale(add(mul(u,B),mul(previous,h)),Decimal(1)/k)for u,h in zip(directions,H)]
            term=scale(mul(previous,B),Decimal(1)/k)
            total=add(total,term);jac=[add(j,u)for j,u in zip(jac,directions)]
            if max(maximum(term),*(maximum(u)for u in directions))<threshold:consecutive+=1
            else:consecutive=0
            if consecutive==3:break
        else:raise ArithmeticError('oracle convergence budget exhausted')
        for _ in range(s):
            jac=[add(mul(total,j),mul(j,total))for j in jac]
            total=mul(total,total)
        output=mandel(total,sqrt2);columns=[mandel(j,sqrt2)for j in jac]
        return dict(value=[+x for x in output],jacobian=[[+columns[j][i]for j in range(6)]for i in range(6)],scalings=s,terms=k,precision=precision,stop_absolute_term=str(threshold))

def rotate(v,Q):
    r=math.sqrt(2);x,y,z,u,v,w=v;A=[[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]
    B=[[sum(Q[i][k]*A[k][l]*Q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)]
    return [float(B[0][0]),float(B[1][1]),float(B[2][2]),float(r*(B[0][1]+B[1][0])/2),float(r*(B[1][2]+B[2][1])/2),float(r*(B[0][2]+B[2][0])/2)]

def cases():
    out=[]
    def put(name,v,**metadata):out.append(dict(id=name,input=[float(x)for x in v],**metadata))
    put('zero',[0]*6)
    for c in (-32.,-1.,1.,32.):put('isotropic-'+str(c),[c,c,c,0,0,0])
    put('mixed-distinct',[-4.,.5,3.,0,0,0]);put('double-eigenvalue',[1.,1.,-2.,0,0,0])
    for gap in (1e-4,1e-8,1e-12,math.ulp(1.)):
        put('near-double-'+str(gap),[1.,1.+gap,-2.,0,0,0])
    put('pure-xy',[0,0,0,2,0,0]);put('pure-oblique-shear',[0,0,0,2,-1,.7])
    Q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
    reflection=[[0.,1.,0.],[1.,0.,0.],[0.,0.,1.]]
    for name,v in [('mixed',[-4.,.5,3.,0,0,0]),('double',[1.,1.,-2.,0,0,0]),('noncoaxial',[2.,-1.,.5,.7,-.2,.4])]:
        put(name+'-oblique-actual-rounded',rotate(v,Q),construction='binary64 Q A Q^T; actual rounded Mandel matrix is oracle input',rotation=Q)
        put(name+'-reflection',rotate(v,reflection),construction='binary64 reflected Cartesian matrix',rotation=reflection)
    for power in range(-1,7):
        t=2.**power
        for label,x in [('below',math.nextafter(t,-math.inf)),('at',t),('above',math.nextafter(t,math.inf))]:
            if x<=64:put(f'scaling-{power}-{label}',[x,0,0,0,0,0],construction='single-axis nextafter threshold; exact binary64 input')
    put('negative-support-boundary',[-64,0,0,0,0,0])
    put('large-mixed',[35,-28,12,9,-7,5])
    return out

def corpus():
    rows=[]
    for case in cases():
        low,high=[oracle(case['input'],p)for p in PRECISIONS]
        with localcontext()as context:
            context.prec=180
            dv=[abs(a-b)for a,b in zip(low['value'],high['value'])]
            dj=[[abs(a-b)for a,b in zip(x,y)]for x,y in zip(low['jacobian'],high['jacobian'])]
            value_scale=max(Decimal(1),*(abs(x)for x in high['value']))
            jac_scale=max(Decimal(1),*(abs(x)for row in high['jacobian']for x in row))
            refinement=dict(value_absolute=[str(x)for x in dv],jacobian_absolute=[[str(x)for x in row]for row in dj],maximum_scaled_value=str(max(dv)/value_scale),maximum_scaled_jacobian=str(max(x for row in dj for x in row)/jac_scale))
        rows.append(case|dict(input_sha256=digest(case['input']),oracle=dict(value=[float(x)for x in high['value']],jacobian=[[float(x)for x in row]for row in high['jacobian']],decimal_value=[str(x)for x in high['value']],decimal_jacobian=[[str(x)for x in row]for row in high['jacobian']]),refinement=refinement,precision_runs=[{k:v for k,v in run.items()if k not in ('value','jacobian')}for run in (low,high)]))
    return dict(version=VERSION,scope='Standalone mathematical operator oracle only; no Atlas/kernel import, model admission or native execution',basis='Mandel xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz',jacobian='row output Mandel component, column unit input Mandel direction; all6directions',input_semantics='Actual finite binary64 Mandel components converted by Decimal.from_float; offdiagonal Cartesian conversion uses Decimal sqrt2 at each precision. Constructed rounded rotations are not assumed exact supplied spectra.',algorithm='Independent forward matrix power-series and differentiated term recurrence; scale until Cartesian infinity norm<=1/8; adaptive absolute tail-term termination3successive terms; square with product-rule Fréchet recurrence.',precisions=list(PRECISIONS),implementation_support='exact Mandel Frobenius<=64; production computed-boundary roundoff remains a separate policy',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=rows,invalid_cases=[dict(id='above-support',input=[math.nextafter(64.,math.inf),0.,0.,0.,0.,0.],expected='range rejection'),dict(id='nonfinite',input_token='NaN/Infinity/-Infinity in each component (not JSON numbers)',expected='finite-input rejection'),dict(id='wrong-shape-or-bool',input_token='length5/7; Boolean component',expected='type/shape rejection')],uncertainty='100/160digit empirical precision refinement is reported componentwise; not a rigorous binary64 rounding-error certificate')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(corpus(),indent=2,allow_nan=False)+'\n')
