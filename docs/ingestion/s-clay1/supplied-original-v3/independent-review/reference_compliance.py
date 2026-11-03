"""Independent source stress-controlled compliance RK4; no Atlas imports."""
import json,math,hashlib
from pathlib import Path
BASE=Path(__file__).parent
M,lam,kap,nu,beta,mu,eta=1.1,.44,.04,.2,.67,20.,.6
p0,p1=10000.,12000.
a0,v0=.42,3.46
pm0=p0+(eta*p0-a0*p0)**2/((M*M-a0*a0)*p0)
def derivative(p,y,stats):
 v,a,pm,ev,ed=y;q=eta*p
 assert p>0 and v>1 and pm>0 and M*M>a*a
 fp=2*M*M*p-2*a*q-(M*M-a*a)*pm
 fq=2*(q-a*p)
 fpm=-(M*M-a*a)*p
 fa=2*p*(a*pm-q)
 size_per_multiplier=v*pm/(lam-kap)*fp
 rotation_per_multiplier=mu*((.75*eta-a)*max(fp,0)+beta*(eta/3-a)*abs(fq))
 H=-(fpm*size_per_multiplier+fa*rotation_per_multiplier)
 assert H>0
 mult=(fp+eta*fq)/H
 assert mult>0
 K=v*p/kap;G=3*K*(1-2*nu)/(2*(1+nu))
 evprime=1/K+mult*fp
 edprime=eta/(3*G)+mult*fq
 dy=[-v*evprime,mult*rotation_per_multiplier,mult*size_per_multiplier,evprime,edprime]
 assert all(math.isfinite(x) for x in dy)
 stats['min_H']=min(stats['min_H'],H);stats['min_multiplier_derivative']=min(stats['min_multiplier_derivative'],mult)
 return dy

def run(n):
 y=[v0,a0,pm0,0.,0.];h=(p1-p0)/n
 stats={'min_H':math.inf,'min_multiplier_derivative':math.inf,'max_abs_yield_scaled':0.}
 for i in range(n):
  p=p0+i*h
  k1=derivative(p,y,stats)
  k2=derivative(p+h/2,[x+h*k/2 for x,k in zip(y,k1)],stats)
  k3=derivative(p+h/2,[x+h*k/2 for x,k in zip(y,k2)],stats)
  k4=derivative(p+h,[x+h*k for x,k in zip(y,k3)],stats)
  y=[x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(y,k1,k2,k3,k4)]
  pn=p+h;v,a,pm,ev,ed=y
  f=((eta-a)*pn)**2-(M*M-a*a)*(pm-pn)*pn
  stats['max_abs_yield_scaled']=max(stats['max_abs_yield_scaled'],abs(f)/p1**2)
 assert stats['max_abs_yield_scaled']<1e-8
 return {'N':n,'endpoint':dict(zip(['v','alpha','pm_Pa','eps_v','eps_d'],y)),'stats':stats}

def main():
 runs=[run(n) for n in [128,256,512]];diffs=[]
 scales=[1,1,12000,1,1]
 for a,b in zip(runs,runs[1:]):
  diff=max(abs(x-y)/s for x,y,s in zip(a['endpoint'].values(),b['endpoint'].values(),scales))
  diffs.append(diff);assert diff<1e-8
 result={'ok':True,'source_sha256':'1923aff43b80f14970dec624deb8f78b09635f419adbf71d797fa0a1a4169511','policy_sha256':hashlib.sha256((BASE/'REFERENCE_POLICY.md').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'initial':{'p_Pa':p0,'eta':eta,'v':v0,'alpha':a0,'pm_Pa':pm0},'runs':runs,'successive_normalized_endpoint_differences':diffs,'tolerance':1e-8,'atlas_or_compiled_calls':0,'scope':'source-compliance reference only; no candidate comparison or E5 approval'}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
