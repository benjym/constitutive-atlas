"""Independent stress-space references; no Atlas imports or generated expressions."""
import math
P=[20e6,10e6,100e3,.002,2.]
Z=[.01,-.004,-.006,.002,-.001,.003]+[0.]*7
ZERO=[0.]*6
D=[.001,-.0002,.0003,.0007,-.0006,.0005]
def dev(a):
 mean=math.fsum(a[:3])/3
 return [v-(mean if i<3 else 0) for i,v in enumerate(a)]
def stress(z,p=P):
 e=[a-b for a,b in zip(z[:6],z[6:12])];v=p[0]*math.fsum(e[:3]);s=dev(e)
 return [(v if i<3 else 0)+2*p[1]*s[i] for i in range(6)]
def equivalent(s):return math.sqrt(1.5*math.fsum(v*v for v in dev(s)))
def multiplier(q,p=P):return p[3]*max(q/p[2]-1.,0.)**p[4]
def relaxation(z,t,p=P):
 K,G,Y,A,n=p;s=dev(stress(z,p));q=equivalent(s)
 if q<=Y:return list(z)
 u=q/Y-1.;c=3*G*A/Y
 if n==1.:end=u*math.exp(-c*t)
 else:end=u*math.exp(-math.log1p((n-1)*c*t*u**(n-1))/(n-1))
 loss=Y*(u-end);dv=[loss*v/(2*G*q) for v in s]
 return list(z[:6])+[a+b for a,b in zip(z[6:12],dv)]+[z[12]+loss/(3*G)]
def creep(z,t,p=P):
 K,G,Y,A,n=p;s=dev(stress(z,p));q=equivalent(s);lam=multiplier(q,p)
 dv=[1.5*t*lam*v/q if q else 0. for v in s]
 return [a+b for a,b in zip(z[:6],dv)]+[a+b for a,b in zip(z[6:12],dv)]+[z[12]+t*lam]
def rotate(v,R):
 r=math.sqrt(2);m=[[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]
 a=[[math.fsum(R[i][k]*m[k][l]*R[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
 return [a[0][0],a[1][1],a[2][2],r*a[0][1],r*a[1][2],r*a[0][2]]
def rotate_state(z,R):return rotate(z[:6],R)+rotate(z[6:12],R)+[z[12]]
def stress_space_history(z,segments,p=P,steps=8192):
 """RK4 for sigma6/alpha, reconstructing plastic strain by compliance.

 Finite constant rates per segment; callers must check a doubled-grid reference
 before using results. This is independent of the production 13-state BE solve.
 """
 K,G,Y,A,n=p;sig=stress(z,p);alpha=z[12];eps=list(z[:6]);result=[]
 def rhs(x,d):
  sd=dev(x[:6]);q=equivalent(sd);lam=multiplier(q,p);loss=3*G*lam/q if q else 0.
  ed=dev(d);volume=K*math.fsum(d[:3])
  return [(volume if i<3 else 0)+2*G*ed[i]-loss*sd[i] for i in range(6)]+[lam]
 for duration,d in segments:
  h=duration/steps;x=sig+[alpha]
  for j in range(steps):
   a=rhs(x,d);b=rhs([v+h*k/2 for v,k in zip(x,a)],d);c=rhs([v+h*k/2 for v,k in zip(x,b)],d);e=rhs([v+h*k for v,k in zip(x,c)],d)
   x=[v+h*(a+2*b+2*c+e)/6 for v,a,b,c,e in zip(x,a,b,c,e)]
  sig,alpha=x[:6],x[6];eps=[v+duration*r for v,r in zip(eps,d)]
  sd=dev(sig);mean=math.fsum(sig[:3])/(9*K)
  elastic=[sd[i]/(2*G)+(mean if i<3 else 0.) for i in range(6)]
  state=eps+[v-e for v,e in zip(eps,elastic)]+[alpha]
  result.append({'state':state,'stress':sig[:]})
 return result
