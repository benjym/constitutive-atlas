"""Independent original-equation references; no Atlas or candidate module import."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import json,hashlib,time
HERE=Path(__file__).resolve().parent
policy=json.loads((HERE/'reference_policy-v2.json').read_text())


def run(Nstr,psistr,mode,digits,steps):
 with localcontext() as ctx:
  ctx.prec=digits
  M=D('1.2');N=D(Nstr);h=D(280);lam=D('.0135');Gamma=D('.82');pref=D(1000);p0=D(130000)
  final=D(policy['endpoint_progress']);ds=final/steps
  initial_r=((1-N)*((1-N).ln()/N)).exp() if N else D(-1).exp()
  # Written without production eta-rate or inverse Eq10 for finite stages.
  ec=Gamma-lam*(p0/pref).ln(); e0=ec+D(psistr)
  C0=p0;K0=D(0) if mode=='constant_mean' else D(1)/3
  C1=C0*D('1.02') if mode=='changing_C_and_K' else C0
  K1=D('.30') if mode=='changing_C_and_K' else K0
  def controls(s):return C0+(C1-C0)*s/final,K0+(K1-K0)*s/final
  def reconstruct(pi,s):
   C,K=controls(s);p=p0
   for _ in range(60):
    Y=((p/pi).ln()*N/(1-N)).exp() if N else D(1)
    eta=M/N*(1+(N-1)*Y) if N else M*(1+(pi/p).ln())
    residual=p*(1-K*eta)-C
    if abs(residual)/p0<D(policy['root_residual_relative']):
     if eta<0 or 1-K*eta<=0 or 1-K*eta+K*M*Y<=0:raise ArithmeticError('reference active branch/domain failure')
     return p,p*eta,eta
    derivative=1-K*eta+K*M*Y
    nxt=p-residual/derivative
    if nxt<=0:raise ArithmeticError('root left positive-pressure branch')
    p=nxt
   raise ArithmeticError('original-yield root did not converge')
  def rhs(s,y):
   pi,e,ev,eq=y;p,q,eta=reconstruct(pi,s)
   if pi<=0 or e<=0:raise ArithmeticError('reference state domain')
   psi_i=e-Gamma+lam*(pi/pref).ln()
   base=1+D('3.5')*psi_i*N/M
   if base<=0:raise ArithmeticError('limiting image domain')
   rL=(base.ln()*(N-1)/N).exp() if N else (-D('3.5')*psi_i/M).exp()
   dilation=(M-eta)/(1-N)
   return (h*(p*rL-pi),-(1+e)*dilation,dilation,D(1))
  y=(p0*initial_r,e0,D(0),D(0));samples=[]
  for step in range(steps):
   s=step*ds
   a=rhs(s,y);b=rhs(s+ds/2,tuple(x+ds*v/2 for x,v in zip(y,a)));c=rhs(s+ds/2,tuple(x+ds*v/2 for x,v in zip(y,b)));d=rhs(s+ds,tuple(x+ds*v for x,v in zip(y,c)))
   y=tuple(x+ds*(aa+2*bb+2*cc+dd)/6 for x,aa,bb,cc,dd in zip(y,a,b,c,d))
  pi,e,ev,eq=y;p,q,eta=reconstruct(pi,final)
  result=dict(eta=eta,e=e,ev=ev,eq=eq,mean_pressure=p,deviatoric_stress=q,image_pressure=pi,image_state_parameter=e-Gamma+lam*(pi/pref).ln(),dilatancy=(M-eta)/(1-N),axial_strain=eq+ev/3,radial_strain=ev/3-eq/2)
  result['stress']=[p+2*q/3,p-q/3,p-q/3,D(0),D(0),D(0)]
  return dict(outputs={k:[str(v) for v in x] if isinstance(x,list) else str(x) for k,x in result.items()},initial_state=dict(eta='0',e=str(e0),ev='0',eq='0'),controls_start=dict(pressure_control=str(C0),stress_ratio_control=str(K0)),controls_end=dict(pressure_control=str(C1),stress_ratio_control=str(K1)))


def difference(a,b):
 errors=[]
 for k,x in a['outputs'].items():
  av=x if isinstance(x,list) else [x];bx=b['outputs'][k];bv=bx if isinstance(bx,list) else [bx]
  scale=D(130000) if k in ('mean_pressure','deviatoric_stress','image_pressure','stress') else D(1)
  errors.extend(abs(D(x)-D(y))/scale for x,y in zip(av,bv))
 return max(errors)


def main():
 cases=[];modes=policy['controls'];t=time.monotonic()
 for ni,N in enumerate(policy['N']):
  for psi_i,psi in enumerate(policy['initial_state_parameter']):
   mode=modes[(ni+psi_i)%3]
   coarse=run(N,psi,mode,50,4096);fine=run(N,psi,mode,50,8192);high=run(N,psi,mode,75,8192)
   refinement=difference(coarse,fine);precision=difference(fine,high)
   if refinement>D(policy['reference_refinement_max_normalized']) or precision>D(policy['reference_precision_max_normalized']):raise AssertionError((N,psi,mode,refinement,precision))
   cases.append(dict(id=f'N{N}-psi{psi}-{mode}',N=N,psi0=psi,mode=mode,reference=high,refinement_error=str(refinement),precision_error=str(precision)))
   print(cases[-1]['id'],'reference passes',flush=True)
 result=dict(policy_sha256=hashlib.sha256((HERE/'reference_policy-v2.json').read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,elapsed_seconds=time.monotonic()-t)
 (HERE/'references-v2.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
