"""Independent high-precision Cartesian source calculation. No Atlas/reference imports."""
import argparse,hashlib,json,math
from decimal import Decimal as D,localcontext,getcontext
from pathlib import Path

ZERO=D(0);ONE=D(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(x):
 n,d=float(x).as_integer_ratio();return D(n)/D(d)
def ratio(v):return D(v['numerator'])/D(v['denominator'])
def sincos(x):
 cutoff=D(10)**(-getcontext().prec-5);ss=x;cc=ONE;st=x;ct=ONE;k=0
 while True:
  k+=1;st=-st*x*x/D((2*k)*(2*k+1));ct=-ct*x*x/D((2*k-1)*(2*k));ss+=st;cc+=ct
  if abs(st)<cutoff and abs(ct)<cutoff:return ss,cc
  assert k<10000

def trace(a):return sum((a[i][i]for i in range(3)),ZERO)
def dot(a,b):return sum((a[i][j]*b[i][j]for i in range(3)for j in range(3)),ZERO)
def mul(a,b):return [[sum((a[i][k]*b[k][j]for k in range(3)),ZERO)for j in range(3)]for i in range(3)]
def norm(a):return dot(a,a).sqrt()
def detterms(a):return [a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1]),-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0]),a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])]
def det(a):return sum(detterms(a),ZERO)
def cofactor(a):
 result=[]
 for i in range(3):
  row=[]
  for j in range(3):
   r=[k for k in range(3)if k!=i];c=[k for k in range(3)if k!=j];row.append((a[r[0]][c[0]]*a[r[1]][c[1]]-a[r[0]][c[1]]*a[r[1]][c[0]])*((-1)**(i+j)))
  result.append(row)
 return result

def matrix(v):
 x,y,z,u,v,w=v;q=D(2).sqrt();return [[x,u/q,w/q],[u/q,y,v/q],[w/q,v/q,z]]
def mandel(a):q=D(2).sqrt();return [a[0][0],a[1][1],a[2][2],q*a[0][1],q*a[1][2],q*a[0][2]]
def rate(parameters,state,increment):
 pref,pscale,phi,lam,kap,N,r,allowance,floor=parameters;sigma=matrix(state[:6]);E=matrix(increment);e=state[6]
 determinant=det(sigma);minor2=sigma[0][0]*sigma[1][1]-sigma[0][1]**2
 assert sigma[0][0]>0 and minor2>0 and determinant>0,'actual-input Cartesian stress not strictly SPD'
 p=trace(sigma)/3;H=[[x/(3*p)for x in row]for row in sigma];Hd=[[H[i][j]-(ONE/3 if i==j else ZERO)for j in range(3)]for i in range(3)]
 T=[[-x/p for x in row]for row in sigma];I1=trace(T);I2=(dot(T,T)-I1*I1)/2;I3=det(T)
 j2=dot(Hd,Hd);j3=trace(mul(mul(Hd,Hd),Hd));detH=det(H);invterms=[ONE/27,-j2/6,j3/3];detHinv=sum(invterms,ZERO)
 sn,cs=sincos(phi);s3=D(3).sqrt();s2=D(2).sqrt();a=s3*(3-sn)/(2*s2*sn);Q=3+a*a
 alpha=(((lam-kap)/(lam+kap))*Q/(a*s3)).ln()/D(2).ln();pow2=(alpha*D(2).ln()).exp();Delta=Q-pow2*a*s3;c1=2*Delta/(9*r);c2=1+(1-c1)*3/(a*a)
 Yi=s3*a/Q
 sphere=state[0]==state[1]==state[2] and all(x==0 for x in state[3:6])
 if sphere:Y=Yi;F=ONE;lode=ZERO;m=[[-a/Q if i==j else ZERO for j in range(3)]for i in range(3)]
 else:
  assert j2>0
  lode=-D(6).sqrt()*j3/(j2*j2.sqrt());tan=(3*j2).sqrt()
  F=(tan*tan/8+(2-tan*tan)/(2+s2*tan*lode)).sqrt()-tan/(2*s2)
  Y=(Yi-1)*(I1*I2+9*I3)*cs*cs/(8*I3*sn*sn)+Yi
  hnorm=dot(H,H);m=[[-a/F*(H[i][j]+Hd[i][j]-H[i][j]/3*(6*hnorm-1)/((F/a)**2+hnorm))for j in range(3)]for i in range(3)]
 mn=norm(m);unit=[[x/mn for x in row]for row in m]
 def act(X):
  hx=dot(H,X);return [[3*(c1*X[i][j]+c2*a*a*H[i][j]*hx)for j in range(3)]for i in range(3)]
 # Eq73–74 with T=-sigma,D=-E maps to sigma'=fs(L:E+fd*Y*(L:mhat)||E||).
 pe=pref*((N-(1+e).ln())/lam).exp();fd=(alpha*(2*p/pe).ln()).exp();fs=3*p/(lam*Delta)
 A=act(E);B=act(unit);en=norm(E);out=[[fs*(A[i][j]+fd*Y*B[i][j]*en)for j in range(3)]for i in range(3)];values=mandel(out)+[-(1+e)*trace(E)]
 assert alpha>0 and Delta>0 and c1>0 and F>0 and Y>0
 diag={'p':p,'det_sigma':determinant,'det_H_cartesian':detH,'det_H_invariant':detHinv,'det_H_invariant_discrepancy':detHinv-detH,'cartesian_expansion_cancellation':sum(map(abs,detterms(H)),ZERO)/abs(detH),'invariant_expansion_cancellation':sum(map(abs,invterms),ZERO)/abs(detH),'determinant_relative_frobenius_condition':norm(sigma)*norm(cofactor(sigma))/abs(determinant),'minor2':minor2,'j2':j2,'j3':j3,'I3':I3,'Y':Y,'F':F,'alpha':alpha,'Delta':Delta,'fd':fd,'fs':fs,'raw_lode':lode}
 return values,diag

def scaled(a,b):return max(abs(x-y)/max(ONE,abs(x),abs(y))for x,y in zip(a,b))
def encode(x):
 if isinstance(x,D):return str(x)
 if isinstance(x,list):return [encode(y)for y in x]
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 return x

def run(root,packet):
 freeze=json.loads((packet/'prospective-freeze.json').read_text())
 for name,pin in freeze['files'].items():assert sha(root/name)==pin,name
 assert sha(Path(freeze['source']['private_pdf']))==freeze['source']['sha256']
 comparison=json.loads((root/'catalogue/investigations/clay2005-rates-v3/comparison.json').read_text());backends={b:{r['id']:r['response']['values']for r in comparison[b]['cases']}for b in ('native','wasm')}
 result=[]
 for case in freeze['cases']:
  evaluated={};errors=[]
  for prec in freeze['policy']['decimal_precisions']:
   try:
    with localcontext()as ctx:
     ctx.prec=prec;vals={k:[ratio(v)for v in case['exact_binary64'][k]]for k in ('parameters','state','increment')};v,d=rate(vals['parameters'],vals['state'],vals['increment']);evaluated[prec]={'values':v,'diagnostics':d}
   except Exception as exc:errors.append({'precision':prec,'exception':type(exc).__name__,'message':str(exc)})
  convergence=[]
  with localcontext()as ctx:
   ctx.prec=260
   for gate in freeze['policy']['convergence']:
    lo,hi=gate['pair']
    if lo in evaluated and hi in evaluated:
     e=scaled(evaluated[lo]['values'],evaluated[hi]['values']);de=abs(evaluated[lo]['diagnostics']['det_H_cartesian']-evaluated[hi]['diagnostics']['det_H_cartesian'])/abs(evaluated[hi]['diagnostics']['det_H_cartesian']);convergence.append({'pair':[lo,hi],'scaled_rate_difference':e,'relative_detH_difference':de,'passed':e<=D(gate['scaled_rate_tolerance'])and de<=D(gate['relative_detH_tolerance'])})
  row={'id':case['id'],'selection':case['selection'],'precision_results':evaluated,'errors':errors,'convergence':convergence,'converged':not errors and len(convergence)==2 and all(g['passed']for g in convergence)}
  if 240 in evaluated:
   with localcontext()as ctx:
    ctx.prec=240;reference=evaluated[240]['values'];original={k:[ratio(v)for v in case['exact_binary64'][k]]for k in ('parameters','state','increment')}
    row['backend_source_diagnostic']={}
    for b in ('native','wasm'):
     observed=[exact(x)for x in backends[b][case['id']]];per=[abs(a-b)/max(ONE,abs(a),abs(b))for a,b in zip(observed,reference)]
     row['backend_source_diagnostic'][b]={'retained_values':backends[b][case['id']],'scaled_component_errors':per,'max_scaled_error':max(per),'max_stress_relative_error':max(abs(a-b)/abs(b)if b else abs(a-b) for a,b in zip(observed[:6],reference[:6]))}
    perturb=[]
    for i in range(6):
     x=float(case['exact_binary64']['state'][i]['literal'])
     if x==0:continue
     for direction in (-1,1):
      y=math.nextafter(x,math.inf if direction>0 else-math.inf);z=list(original['state']);z[i]=exact(y)
      item={'component':i,'direction':direction,'hex':y.hex(),'exact_ratio':[str(v)for v in y.as_integer_ratio()]}
      try:
       v,d=rate(original['parameters'],z,original['increment']);item.update(spd=True,relative_det_change=abs(d['det_sigma']-evaluated[240]['diagnostics']['det_sigma'])/abs(evaluated[240]['diagnostics']['det_sigma']),scaled_rate_change=scaled(v,reference))
      except Exception as exc:item.update(spd=False,error=type(exc).__name__+':'+str(exc))
      perturb.append(item)
    row['adjacent_binary64_stress_perturbations']=perturb;row['max_adjacent_scaled_rate_change']=max((t['scaled_rate_change']for t in perturb if t.get('spd')),default=ZERO)
  result.append(encode(row))
 return {'version':'clay2005-boundary-precision-v1-results','freeze_sha256':sha(packet/'prospective-freeze.json'),'study_script_sha256':sha(Path(__file__)),'all_cases_converged':all(r['converged']for r in result),'cases':result,'compiled_calls':0,'atlas_oracle_calls':0,'existing_reference_evaluations':0,'new_acceptance_gate':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--packet',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.root,a.packet);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print('converged',r['all_cases_converged'],'cases',len(r['cases']))
