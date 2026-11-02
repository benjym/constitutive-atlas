"""Independent stress-space references; never imports the DSL or material engine."""
import math
P=[20e6,10e6,100e3,20e6]
E=[.01,-.004,-.006,.002,-.001,.003]
Z=E+[0.]*7
D=[.001,-.0002,.0003,.0007,-.0006,.0005]
ZERO=[0.]*6
def rotate(v,R):
    r=math.sqrt(2);m=[[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]
    a=[[math.fsum(R[i][k]*m[k][l]*R[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return [a[0][0],a[1][1],a[2][2],r*a[0][1],r*a[1][2],r*a[0][2]]
def rotate_state(z,R):return rotate(z[:6],R)+rotate(z[6:12],R)+[z[12]]
def dev(v):
    mean=math.fsum(v[:3])/3
    return [x-(mean if i<3 else 0) for i,x in enumerate(v)]
def stress(z,p=P):
    elastic=[a-b for a,b in zip(z[:6],z[6:12])];s=dev(elastic);v=math.fsum(elastic[:3])*p[0]
    return [(v if i<3 else 0)+2*p[1]*s[i] for i in range(6)]
def relaxation(z,t,p=P):
    K,G,Y,eta=p;s=dev(stress(z,p));q=math.sqrt(1.5*math.fsum(x*x for x in s))
    if q<=Y:return list(z)
    # Integrate the scalar overstress exactly; recover plastic strain by compliance.
    fraction=(q-Y)*(-math.expm1(-3*G*t/eta))/q
    dv=[x*fraction/(2*G) for x in s]
    return list(z[:6])+[a+b for a,b in zip(z[6:12],dv)]+[z[12]+q*fraction/(3*G)]
def creep(z,t,p=P):
    K,G,Y,eta=p;s=dev(stress(z,p));q=math.sqrt(1.5*math.fsum(x*x for x in s));lam=max(q-Y,0)/eta
    dv=[t*1.5*lam*x/q if q else 0 for x in s]
    return [a+b for a,b in zip(z[:6],dv)]+[a+b for a,b in zip(z[6:12],dv)]+[z[12]+t*lam]
def stress_space_history(z,segments,p=P,steps=8192):
    """RK4 on six stress components plus accumulated strain, not production state.

    Piecewise constant six-component rates; final output at each segment. A distinct
    doubled-grid calculation must converge before these are used as references.
    """
    K,G,Y,eta=p;sig=stress(z,p);a=z[12];eps=list(z[:6]);result=[]
    def derivative(x,d):
        sd=dev(x[:6]);q=math.sqrt(1.5*math.fsum(v*v for v in sd));over=max(q-Y,0)
        # Stress balance independently eliminates plastic strain: sigma'=C:D-C:Dvp.
        loss=3*G*over/(eta*q) if q else 0
        ed=dev(d);volume=K*math.fsum(d[:3])
        return [(volume if i<3 else 0)+2*G*ed[i]-loss*sd[i] for i in range(6)]+[over/eta]
    for duration,d in segments:
        h=duration/steps;x=sig+[a]
        for j in range(steps):
            k1=derivative(x,d);k2=derivative([v+h*k/2 for v,k in zip(x,k1)],d)
            k3=derivative([v+h*k/2 for v,k in zip(x,k2)],d);k4=derivative([v+h*k for v,k in zip(x,k3)],d)
            x=[v+h*(a+2*b+2*c+e)/6 for v,a,b,c,e in zip(x,k1,k2,k3,k4)]
        sig,a=x[:6],x[6];eps=[v+duration*r for v,r in zip(eps,d)]
        sd=dev(sig);meanstrain=math.fsum(sig[:3])/(9*K)
        elastic=[sd[i]/(2*G)+(meanstrain if i<3 else 0) for i in range(6)]
        state=eps+[v-e for v,e in zip(eps,elastic)]+[a];result.append(dict(state=state,stress=sig[:]))
    return result
