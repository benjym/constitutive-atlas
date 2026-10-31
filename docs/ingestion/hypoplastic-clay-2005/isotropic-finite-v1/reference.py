"""Independent finite isotropic source-law closed form; no Atlas/oracle imports."""
import argparse,hashlib,json
from decimal import Decimal as D,localcontext,getcontext
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(v):return D(v['numerator'])/D(v['denominator'])
def sin(x):
 term=x;total=x;k=0;cutoff=D(10)**(-getcontext().prec-5)
 while abs(term)>=cutoff:k+=1;term=-term*x*x/D((2*k)*(2*k+1));total+=term
 return total

def powd(x,y):return (y*x.ln()).exp()
def exprel_integral(b,x):return x if b==0 else((b*x).exp()-1)/b

def calculate(f,prec):
 with localcontext()as ctx:
  ctx.prec=prec;par={k:exact(v)for k,v in f['parameters'].items()};p0=exact(f['initial']['p']);e0=exact(f['initial']['e']);phi,lam,kap,N,r,pref=[par[k]for k in ['phi_c','lambda_star','kappa_star','N','r','p_ref']]
  a=D(3).sqrt()*(3-sin(phi))/(2*D(2).sqrt()*sin(phi));Q=3+a*a;alpha=(((lam-kap)/(lam+kap))*Q/(a*D(3).sqrt())).ln()/D(2).ln();Delta=Q-powd(D(2),alpha)*a*D(3).sqrt();c1=2*Delta/(9*r);c2=1+(1-c1)*3/(a*a);Yi=D(3).sqrt()*a/Q;C=3*c1+c2*a*a;K=3*C/(lam*Delta);h=alpha*(3/lam-K);g=alpha*K*Yi
  pe0=pref*((N-(1+e0).ln())/lam).exp();q0=powd(2*p0/pe0,-alpha);qstar=-g/h
  assert p0>0 and e0>=0 and 0<kap<lam and r>0 and alpha>0 and Delta>0 and h<0 and g>0
  relative=lambda x,y:abs(x-y)/max(D(1),abs(x),abs(y))
  identities={'C_equals_Q':relative(C,Q),'K_reduction':relative(K,3*(lam+kap)/(2*lam*kap)),'Delta_reduction':relative(Delta,2*kap*Q/(lam+kap)),'Yi_fd_NCL':relative(Yi*powd(D(2),alpha),(lam-kap)/(lam+kap)),'NCL_loading_logp_slope':relative(K*(1-Yi*powd(D(2),alpha)),3/lam),'NCL_unloading_logp_slope':relative(K*(1+Yi*powd(D(2),alpha)),3/kap),'loading_fixedq':relative(qstar,powd(D(2),-alpha))}
  coefficients=dict(a=a,Q=Q,alpha=alpha,Delta=Delta,c1=c1,c2=c2,Yi=Yi,C=C,K=K,h=h,g=g,pe0=pe0,q0=q0,qstar=qstar,maximum_e_nonnegative_compression=(1+e0).ln()/3)
  rows=[]
  for c in f['cases']:
   eps=exact(c['axial_target']);eta=D(1 if eps>0 else-1 if eps<0 else 0);x=abs(eps);b=eta*h;expb=(b*x).exp();q=q0*expb+g*exprel_integral(b,x)if eta else q0;pe=pe0*(3*eps/lam).exp();p=pe/2*powd(q,-1/alpha);e=(1+e0)*(-3*eps).exp()-1
   if eta==0:p=p0;e=e0
   qx=eta*h*q+g if eta else D(0);qx_direct=b*q0*expb+g*expb if eta else D(0);px=p*(3*eta/lam-qx/(alpha*q))if eta else D(0);px_source=p*K*(eta-Yi/q)if eta else D(0);ex=-3*eta*(1+e);q_alt=(-g/b)+(q0+g/b)*expb if eta else q0
   checks={'q_linear_ODE':relative(qx,qx_direct),'pressure_ODE':relative(px,px_source),'q_equilibrium_solution':relative(q,q_alt),'positive_q':q>0,'positive_p':p>0,'nonnegative_e':e>=0}
   assert checks['positive_q']and checks['positive_p']and checks['nonnegative_e']
   rows.append({'id':c['id'],'axial_target':eps,'p':p,'e':e,'pe':pe,'q':q,'fd':1/q,'state':[p,p,p,D(0),D(0),D(0),e],'dp_d_abs_axial':px,'de_d_abs_axial':ex,'checks':checks,'budget_stress_absolute_Pa':D('1e-5')*max(D(1),p),'budget_void_absolute':D('1e-6')})
  return coefficients,identities,rows

def encode(x):
 if isinstance(x,D):return str(x)
 if isinstance(x,list):return [encode(v)for v in x]
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 return x

def run(root,packet):
 f=json.loads((packet/'prospective-freeze.json').read_text())
 for n,s in f['files'].items():assert sha(root/n)==s,n
 evaluated={n:calculate(f,n)for n in f['policy']['decimal_precisions']};convergence=[]
 with localcontext()as ctx:
  ctx.prec=180
  for low,high in zip(evaluated[80][2],evaluated[160][2]):
   pe=abs(low['p']-high['p'])/max(D(1),abs(low['p']),abs(high['p']));ee=abs(low['e']-high['e'])/max(D(1),abs(low['e']),abs(high['e']));convergence.append({'id':high['id'],'scaled_pressure_difference':pe,'scaled_void_difference':ee,'passed':max(pe,ee)<=D('1e-60')})
 checks={}
 for precision,(coefficient,identities,rows)in evaluated.items():
  with localcontext()as ctx:
   ctx.prec=precision;initial_p=exact(f['initial']['p']);initial_e=exact(f['initial']['e'])
  checks[precision]={'coefficient_identities_passed':all(e<=D('1e-60')for e in identities.values()),'ODE_checks_passed':all(v<=D('1e-60')for row in rows for k,v in row['checks'].items()if type(v)is D),'zero_limit_identity':next(r for r in rows if r['id']=='zero')['p']==initial_p and next(r for r in rows if r['id']=='zero')['e']==initial_e}
 result={'version':'clay2005-isotropic-finite-v1-reference','input_freeze_sha256':sha(packet/'prospective-freeze.json'),'script_sha256':sha(Path(__file__)),'precision_results':{n:{'coefficients':c,'coefficient_identity_residuals':i,'cases':r}for n,(c,i,r)in evaluated.items()},'convergence':convergence,'checks':checks,'all_checks_passed':all(c['passed']for c in convergence)and all(all(v.values())for v in checks.values()),'compiled_calls':0,'Atlas_imports':False,'source_oracle_evaluations':0,'scientific_admission':False}
 return encode(result)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.root,a.packet);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print('allchecks',r['all_checks_passed'])
