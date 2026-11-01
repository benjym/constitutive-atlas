"""Saved-only analytic backward-Euler transverse map and independent AD comparison."""
from decimal import Decimal as D,localcontext
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];P=HERE.parent
spec=importlib.util.spec_from_file_location('saved_covariance',P/'covariance.py');cov=importlib.util.module_from_spec(spec);spec.loader.exec_module(cov)
load=cov.load

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symmetric(z):return all(z[o+1]==z[o+2] and all(x==0 for x in z[o+3:o+6]) for o in [0,7,13,19])
def matrix(z,raw,scale):
 """Residual Jacobian in (delta sigma/scale, delta alpha, delta fabric) yy-minus-zz coordinates."""
 z=[D.from_float(float(x)) for x in z];k={n:D.from_float(float(x)) for n,x in raw.items()};s=z[:6];alpha=z[7:13];fabric=z[13:19]
 p=sum(s[:3])/3;e=z[6];r=[s[i]/p-(1 if i<3 else 0) for i in range(6)];w=[x-y for x,y in zip(r,alpha)];N=sum(x*x for x in w).sqrt();n=[x/N for x in w]
 assert symmetric([float(x) for x in z]),'matrix requires actual symmetric state'
 c3=D(6).sqrt()*sum(x**3 for x in n[:3]);g=2*k['c']/((1+k['c'])-(1-k['c'])*c3)
 B=1+D('1.5')*(1-k['c'])/k['c']*g*c3;C=3*(D(3)/2).sqrt()*(1-k['c'])/k['c']*g;f=B-2*C*n[1]
 G=k['G0']*k['p_at']*(D('2.97')-e)**2/(1+e)*(p/k['p_at']).sqrt();b0=k['G0']*k['h0']*(1-k['ch']*e)/(p/k['p_at']).sqrt()
 distance=sum((a-b)*c for a,b,c in zip(alpha,z[19:25],n));L=z[25]*distance/b0
 psi=e-k['e0']+k['lambda_c']*(p/k['p_at'])**k['xi'];ab=(D(2)/3).sqrt()*(g*k['M']*(-k['nb']*psi).exp()-k['m']);ad=(D(2)/3).sqrt()*(g*k['M']*(k['nd']*psi).exp()-k['m'])
 dil=k['A0']*(1+max(D(0),sum(a*b for a,b in zip(fabric,n))))*(ad-sum(a*b for a,b in zip(alpha,n)))
 A=2*G*L*f/N;H=D(2)/3*z[25];J=H*ab/N;F=k['cz']*max(D(0),-L*dil)
 return [[1+A/p,-A/scale,D(0)],[-J*scale/p,1+H+J,D(0)],[F*k['zmax']*scale/(p*N),-F*k['zmax']/N,1+F]]


def inverse2(m):
 det=m[0][0]*m[1][1]-m[0][1]*m[1][0]
 if det==0:return det,None
 return det,[[m[1][1]/det,-m[0][1]/det],[-m[1][0]/det,m[0][0]/det]]


def audit():
 freeze=load(HERE/'freeze.json')
 for name,h in freeze['files'].items():assert sha(ROOT/name)==h,name
 native=ROOT/'docs/reviews/sanisand-v03-monotonic-v1/native-results';index=load(native/'index.json');model=load(ROOT/'docs/reviews/sanisand-v03-research-freeze-v1/model.json')
 rows=[];checked=0;worst=D(0);ad_rows=[]
 with localcontext() as ctx:
  ctx.prec=90
  for item in index['records']:
   if not item['id'].startswith('extension-') or '-p20000/' not in item['id']:continue
   receipt=load(native/item['file']);assert sha(native/item['file'])==item['sha256'];args=receipt['request']['args'];pars=dict(zip(model['parameters'],[float(x) for x in args[1].split(',')]));points=receipt['response']['points'];gain=[D(1),D(0)];steps=[]
   first=next((i for i,x in enumerate(points) if not symmetric(x['state'])),None)
   for i,point in enumerate(points[1:],1):
    if not symmetric(point['state']) or not symmetric(points[i-1]['state']):break
    assert point['diagnostics']['increment_fractions']==[1],'caller step contains substeps; simple BE map unavailable'
    m=matrix(point['state'],pars,D(20000));det,inverse=inverse2(m)
    assert inverse is not None,'singular transverse current Jacobian'
    gain=[sum(inverse[j][k]*gain[k] for k in range(2)) for j in range(2)]
    amplification_norm=max(sum(abs(x) for x in row) for row in inverse)
    steps.append({'point':i,'determinant':str(det),'inverse_infinity_norm':str(amplification_norm),'unit_initial_stress_mode_gain':list(map(str,gain))})
   rows.append({'id':item['id'],'first_binary64_symmetry_loss_point':first,'exact_symmetric_prefix_steps':len(steps),'total_caller_steps':len(points)-1,'prefix_endpoint_gain':list(map(str,gain)),
                'maximum_step_inverse_norm':str(max(D(x['inverse_infinity_norm']) for x in steps)) if steps else None,'steps':steps})
  requests=load(P/'covariance-requests.json.gz');raw=gzip.decompress((P/'native-output.jsonl.gz').read_bytes()).decode();responses=[json.loads(x) for x in raw.splitlines()]
  for parent_index,parent in enumerate(requests['parents']):
   if not symmetric(parent['current']) or not symmetric(parent['incoming']):continue
   base=parent_index*116;parameters=dict(zip(model['parameters'],requests['requests'][base]['wire'][:16]));m=matrix(parent['current'],parameters,D(100000));err=D(0)
   for col,(yy,zz) in enumerate([(1,2),(8,9),(14,15)]):
    a=responses[base+2*yy]['directional'];b=responses[base+2*zz]['directional']
    for row,(ry,rz) in enumerate([(1,2),(8,9),(14,15)]):
     value=(D.from_float(a[ry])-D.from_float(a[rz])-D.from_float(b[ry])+D.from_float(b[rz]))/2/(D(100000) if row==0 else 1)
     err=max(err,abs(value-m[row][col])/max(D(1),abs(m[row][col])));checked+=1
   assert err<=D(freeze['independent_analytic_to_AD_gate']),str(err)
   worst=max(worst,err);ad_rows.append({'id':parent['id'],'maximum_scaled_derivative_difference':str(err)})
  assert len(rows)==9 and checked>=9,'coverage missing'
 return {'kind':'independent-discrete-transverse-diagnosis','candidate_integrations':0,'compiled_calls':0,'independent_analytic_to_AD_pass':True,'independent_derivative_components':checked,'maximum_scaled_derivative_difference':str(worst),
         'derivative_rows':ad_rows,'paths':rows,'qualification_pass':False,
         'limits':'Actual exactly symmetric prefixes only; stops at first binary64 symmetry loss. Unit perturbation gain is a local linearization diagnostic, not a manufactured replacement history, Newton-iterate trace, multiple-root proof or correction of the original failed accuracy gate.'}


if __name__=='__main__':print(json.dumps(audit(),indent=2))
