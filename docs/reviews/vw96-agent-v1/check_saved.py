"""Read existing evidence; recompute source rates/saved comparisons, never integrate."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3] if 'docs' in Path(__file__).parts else Path('/Users/bmar5496/code/constitutive-atlas')
def load(p):return json.loads((ROOT/p).read_text())
def matrix(v):
 r=math.sqrt(2);return [[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]
def tr(a):return sum(a[i][i]for i in range(3))
def inner(a,b):return sum(a[i][j]*b[i][j]for i in range(3)for j in range(3))
def mm(a,b):return [[sum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def mandel(a):return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
def rate(z,d,par):
 # Direct compression-positive Eq40 conversion; independent of saved oracle/DSL.
 _,phi,hs,n,ed0,ec0,ei0,alpha,beta=par
 s=matrix(z);D=matrix(d);pressure=tr(s)/3;A=[[x/(3*pressure)for x in row]for row in s]
 B=[[A[i][j]-(1/3 if i==j else 0)for j in range(3)]for i in range(3)]
 j=inner(B,B);u=math.sqrt(3*j);cos=-math.sqrt(6)*tr(mm(mm(B,B),B))/j**1.5 if j else 0
 F=math.sqrt(u*u/8+(2-u*u)/(2+math.sqrt(2)*u*cos))-u/(2*math.sqrt(2))
 a=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi));r=math.exp(-(3*pressure/hs)**n)
 ed,ec,ei=ed0*r,ec0*r,ei0*r;e=z[6]
 fd=((e-ed)/(ec-ed))**alpha;fe=(ec/e)**beta
 fb=hs/n*(ei0/ec0)**beta*(1+ei)/ei*(3*pressure/hs)**(1-n)/(3+a*a-a*math.sqrt(3)*((ei0-ed0)/(ec0-ed0))**alpha)
 k=fb*fe/inner(A,A);ad=inner(A,D);dn=math.sqrt(inner(D,D))
 result=[[k*(F*F*D[i][j]+a*a*ad*A[i][j]-fd*a*F*(A[i][j]+B[i][j])*dn)for j in range(3)]for i in range(3)]
 return mandel(result)+[-(1+e)*tr(D)]
def ratio(a,b,t):
 assert len(a)==len(b) and all(math.isfinite(x)for x in a+b)
 return max(abs(x-y)/((t['stress_absolute_Pa']if i<6 else t['state_absolute'])+t['relative']*abs(y))for i,(x,y)in enumerate(zip(a,b)))
def arg(args,key):return list(map(float,args[args.index(key)+1].split(',')))
def check_report(name):
 d=load(name);counts={};worst_rate=worst_path=worst_ref=0;source_checks=0
 for c in d['cases']:
  counts[c['kind']]=counts.get(c['kind'],0)+1
  if c['kind'] in ['cartesian-source-rate','fixed-frame-covariance']:
   args=c['arguments'];expected=rate(arg(args,'--current'),arg(args,'--strain'),arg(args,'--parameters'))
   re=ratio(c['expected'],expected,d['tolerances']['rate']);assert re<=1
   ra=ratio(c['actual'],expected,d['tolerances']['rate']);assert ra<=1
   worst_rate=max(worst_rate,ra);source_checks+=1
   if c['kind']=='fixed-frame-covariance':
    Q=c['rotation'];qt=list(map(list,zip(*Q)));base=c['base_result']['values'];rotated=mandel(mm(mm(Q,matrix(base)),qt))+base[6:]
    assert ratio(c['actual'],rotated,d['tolerances']['rate'])<=1
  elif c['kind']=='independent-rk4-reference':
   for s in c['segments']:
    # No regeneration: compare the last two saved grid states and actual endpoint.
    re=ratio(s['coarse'],s['expected'],d['tolerances']['rk4_convergence']);ra=ratio(s['actual'],s['expected'],d['tolerances']['path'])
    assert math.isclose(re,s['reference_tolerance_ratio'],rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(ra,s['max_tolerance_ratio'],rel_tol=1e-12,abs_tol=1e-12)
    assert s['reference_converged']==(re<=1)
    assert ra<=1
    worst_ref=max(worst_ref,re);worst_path=max(worst_path,ra)
    levels=s.get('reference_levels',[])
    if levels:assert levels[-1]['state']==s['expected'] and all(a['steps']<b['steps']for a,b in zip(levels,levels[1:]))
   # Exact source Eq2 continuity independently bounds stored final density.
   totaltrace=sum(sum(e[:3])for e in c['strain_segments']);exact=(1+c['initial'][6])*math.exp(-totaltrace)-1
   assert abs(c['segments'][-1]['expected'][6]-exact)<1e-11
  elif c['kind']=='invalid-initial-state':
   assert c['result']['ok'] is False and c['result']['state']==c['initial']
  else:raise AssertionError(c['kind'])
 assert d['passed']==all(c['passed']for c in d['cases'])
 return {'path':name,'cases':len(d['cases']),'passed':d['passed'],'counts':counts,'source_rate_recomputations':source_checks,'maximum_native_rate_ratio':worst_rate,'maximum_native_path_ratio':worst_path,'maximum_saved_reference_ratio':worst_ref}
def main():
 v1=check_report('catalogue/evidence/reports/hypoplasticity-investigation-v1.json')
 v2=check_report('catalogue/evidence/reports/hypoplasticity-cartesian-rk4-v2.json')
 resume=check_report('catalogue/investigations/native-resume-2026-10-31/vw96.json')
 assert not v1['passed'] and v1['cases']==226 and v1['maximum_saved_reference_ratio']>1
 assert v2['passed'] and v2['cases']==229 and v2['maximum_saved_reference_ratio']<=1
 assert resume['passed'] and resume['cases']==229
 a=load('catalogue/evidence/reports/hypoplasticity-investigation-v1.json');b=load('catalogue/evidence/reports/hypoplasticity-cartesian-rk4-v2.json')
 assert a['tolerances']==b['tolerances']
 model=load('models/hypoplastic-sand-vw96.json');assert b['parameters']==[x['default']for x in model['parameters'].values()]
 assert b['parameters']==load('catalogue/investigations/native-resume-2026-10-31/vw96.json')['parameters']
 return {'saved_only_review_pass':True,'reports':[v1,v2,resume],'tolerances_unchanged':True,'new_integrations':0,'compiled_calls':0,'scope':'Saved endpoints/rates only; no all-stage domain, current-release, Wasm or browser certification.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
