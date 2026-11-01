"""Independent Decimal closed-form isotropic clay2013 trajectory.
No Atlas imports, rate evaluator, source-code translation, or numerical ODE solver.
Compression-positive volumetric strain increments; zero spin.
"""
from decimal import Decimal, localcontext

D=Decimal

def number(x):
    if isinstance(x,bool): raise ValueError('Boolean is not a real input')
    z=D.from_float(x) if type(x) is float else D(x)
    if not z.is_finite(): raise ValueError('finite Decimal input required')
    return z

def expm1(x):
    """Avoid cancellation in unloading/loading near zero strain."""
    if abs(x)>D('.1'): return x.exp()-1
    term=x; result=x; n=1
    while term:
        n+=1;term=term*x/n;new=result+term
        if new==result: return new
        result=new
    return result

def state(p,e,*,lambda_star,kappa_star,N):
    p,e,L,K,N=map(number,(p,e,lambda_star,kappa_star,N))
    if not (p>0 and e>=0 and L>K>0):raise ValueError('p>0,e>=0,lambda>kappa>0 required')
    pe=D(1000)*((N-(1+e).ln())/L).exp()
    return dict(p=p,e=e,pe=pe,r=(p/pe)**2)

def advance(p,e,dx,*,lambda_star,kappa_star,N,precision=90):
    """Exact segment of one sign; dx=integrated volumetric compression strain.

    Parameters/initial data may be strings or Decimal. Floats are converted by
    exact binary64 identity; strings retain their exact decimal identity.
    Only e>=0 states are retained. Returned x is this segment's increment.
    """
    if type(precision) is not int or not 32 <= precision <= 1000:
        raise ValueError("precision must be an integer between32 and1000")
    with localcontext() as ctx:
        ctx.prec=precision
        L,K,N,dx=map(number,(lambda_star,kappa_star,N,dx))
        initial=state(p,e,lambda_star=L,kappa_star=K,N=N)
        if dx > (1+initial['e']).ln():
            raise ValueError('segment leaves nonnegative void-ratio domain')
        e1=(1+initial['e'])*(-dx).exp()-1
        if e1<0:raise ValueError('segment leaves nonnegative void-ratio domain')
        z=(1/K-1/L)*abs(dx)
        y0=1/initial['r']
        if dx>=0:
            q=expm1(-z);y=y0*(-z).exp()-q
        else:
            q=expm1(z);y=y0*z.exp()+q
        pe=initial['pe']*(dx/L).exp()
        p=pe/y.sqrt()
        return dict(p=+p,e=+e1,pe=+pe,r=+(1/y),x=+dx)

def path(p,e,increments,**parameters):
    result=[]
    for dx in increments:
        value=advance(p,e,dx,**parameters)
        result.append(value);p,e=value['p'],value['e']
    return result
