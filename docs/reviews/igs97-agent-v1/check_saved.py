"""Independent saved-evidence arithmetic; no Atlas imports, integration or binaries."""
from pathlib import Path
import json,math,hashlib,sys
from decimal import Decimal,localcontext
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for required in ['inputs.json','review.json','manifest.json']:
 assert (O/required).is_file(),'required frozen binding missing: '+required
for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
assert sha(R/'models/hypoplastic-sand-igs97.json')=='83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def matrix(a):
 q=math.sqrt(2);return [[a[0],a[3]/q,a[5]/q],[a[3]/q,a[1],a[4]/q],[a[5]/q,a[4]/q,a[2]]]
def mandel(A):return [A[0][0],A[1][1],A[2][2],math.sqrt(2)*A[0][1],math.sqrt(2)*A[1][2],math.sqrt(2)*A[0][2]]
def rotate(a,Q):
 A=matrix(a);return mandel([[sum(Q[i][k]*A[k][l]*Q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)])
def args(a,key):return [float(x)for x in a[a.index(key)+1].split(',')]
def rate(s,d,p):
 # Direct source Eq40 + NH97 Eq14/15 contraction in orthonormal coordinates.
 _,phi,hs,n,ed0,ec0,ei0,alpha,beta,rad,mr,mt,br,chi=p
 tr=sum(s[:3]);hat=[x/tr for x in s[:6]];dev=[hat[i]-(1/3 if i<3 else 0)for i in range(6)]
 j2=dot(dev,dev);u=math.sqrt(3*j2);A=matrix(dev);cub=sum(A[i][j]*A[j][k]*A[k][i]for i in range(3)for j in range(3)for k in range(3));co=-math.sqrt(6)*cub/j2**1.5 if j2>1e-24 else 0
 F=math.sqrt(u*u/8+(2-u*u)/(2+math.sqrt(2)*u*co))-u/(2*math.sqrt(2));a=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi));c=math.exp(-(tr/hs)**n);ed,ec,ei=ed0*c,ec0*c,ei0*c;e=s[6]
 fd=((e-ed)/(ec-ed))**alpha;fe=(ec/e)**beta;fb=hs/n*(ei0/ec0)**beta*(1+ei)/ei*(tr/hs)**(1-n)/(3+a*a-a*math.sqrt(3)*((ei0-ed0)/(ec0-ed0))**alpha);fac=fb*fe/dot(hat,hat)
 def L(x):return [fac*(F*F*x[i]+a*a*dot(hat,x)*hat[i])for i in range(6)]
 N=[-fac*fd*a*F*(hat[i]+dev[i])for i in range(6)];hn=math.sqrt(dot(s[7:],s[7:]));eta=[x/hn if hn else 0 for x in s[7:]];rho=min(hn/rad,1);v=dot(eta,d);w=rho**chi;ld,le=L(d),L(eta)
 return [(w*mt+(1-w)*mr)*ld[i]+w*v*((1-mt)*le[i]+N[i]if v>0 else(mr-mt)*le[i])for i in range(6)]+[-(1+e)*sum(d[:3])]+[d[i]-(rho**br*eta[i]*v if v>0 else 0)for i in range(6)]
def ratio(a,b,t):
 return max(abs(x-y)/((t['stress_absolute_Pa']if i<6 else t['void_ratio_absolute']if i==6 else t['history_absolute'])+t['relative']*abs(y))for i,(x,y)in enumerate(zip(a,b)))
def memory(h,d,rad):
 with localcontext()as c:
  c.prec=90;h,d,rad=map(lambda x:Decimal(str(x)),(h,d,rad));sign=Decimal(1)if d>=0 else Decimal(-1);q=h*sign;length=abs(d)
  if q<0:
   if length<=-q:return float(h+d)
   length+=q;q=Decimal(0)
  if q>=rad:return float(sign*rad)
  u0=(q/rad).sqrt();target=length/(2*rad)-u0-(1-u0).ln();lo=u0;hi=Decimal(1)-Decimal('1e-89')
  for _ in range(300):
   u=(lo+hi)/2
   if -u-(1-u).ln()<target:lo=u
   else:hi=u
  return float(sign*rad*((lo+hi)/2)**2)
reports={};allpathmax=0;refmax=0;analyticalmax=0;v1failed=[]
for name in ['igs-investigation-v1','igs-analytical-history-v2']:
 a=read(R/'catalogue/evidence/reports'/f'{name}.json');assert len(a['cases'])==303;counts={};ratemax=0;segs=0
 for row in a['cases']:
  kind=row['kind'];counts[kind]=counts.get(kind,0)+1
  if 'arguments'in row:
   p=args(row['arguments'],'--parameters');s=args(row['arguments'],'--initial');d=args(row['arguments'],'--strain')
  if kind in ['cartesian-igs-rate','fixed-frame-covariance','atlas-numerical-convention']:
   ref=rate(s,d,p);assert ratio(row['expected'],ref,a['tolerances']['rate'])<1;rr=ratio(row['actual'],ref,a['tolerances']['rate']);assert rr<1;ratemax=max(ratemax,rr)
   if kind=='fixed-frame-covariance':
    b=row['base_arguments'];base=rate(args(b,'--initial'),args(b,'--strain'),p);Q=row['rotation'];rot=rotate(base[:6],Q)+[base[6]]+rotate(base[7:],Q);assert ratio(ref,rot,a['tolerances']['rate'])<1
  elif kind=='invalid-state-or-parameters':assert row['result']['ok']is False and row['result']['state']==row['initial'] and row['result']['diagnostics']['substeps']==0
  elif kind=='independent-rk4-reference':
   actual=row['initial'];expected=row['initial'];active={i for v in [actual[7:]]+row['strain_segments']for i,x in enumerate(v)if x!=0};axis=next(iter(active))if len(active)==1 else None;hm=actual[7+axis]if axis is not None else None
   for seg,d in zip(row['segments'],row['strain_segments']):
    segs+=1;aa=seg['arguments'];assert args(aa,'--initial')==actual and args(aa,'--strain')==d;p=args(aa,'--parameters');levels=seg['reference_levels'];assert levels[-1]['state']==seg['expected']
    for old,new in zip(levels,levels[1:]):assert math.isclose(ratio(old['state'],new['state'],a['tolerances']['reference']),new['comparison_to_previous'],rel_tol=1e-10,abs_tol=1e-10)
    rr=ratio(seg['actual'],seg['expected'],a['tolerances']['path']);assert math.isclose(rr,seg['max_tolerance_ratio'],rel_tol=1e-10,abs_tol=1e-10)
    if name.endswith('v2'):
     assert rr<=1 and seg['reference_converged']and levels[-1]['comparison_to_previous']<=1;allpathmax=max(allpathmax,rr);refmax=max(refmax,levels[-1]['comparison_to_previous']);assert abs(sum(seg['diagnostics']['increment_fractions'])-1)<1e-14
     exact_e=(1+actual[6])*math.exp(-sum(d[:3]))-1;assert abs(seg['actual'][6]-exact_e)<1e-8
    if axis is not None:
     hm=memory(hm,d[axis],p[9]);stored=seg['analytical_history'];assert abs(stored['expected']-hm)<1e-18
     ar=abs(seg['actual'][7+axis]-hm)/(a['tolerances']['path']['history_absolute']+a['tolerances']['path']['relative']*abs(hm))
     if name.endswith('v2'):assert ar<=1;analyticalmax=max(analyticalmax,ar)
    actual=seg['actual'];expected=seg['expected']
   if not row['passed']:v1failed.append(row['id'])
 reports[name]={'passed':a['passed'],'counts':counts,'saved_segments':segs,'direct_source_rate_max_ratio':ratemax}
assert reports['igs-investigation-v1']['passed']is False and reports['igs-analytical-history-v2']['passed']is True
assert v1failed==['path-mobilisation','path-saturated-reversal-through-zero','path-small-cycles','path-large-reversal']
assert read(R/'catalogue/evidence/reports/igs-investigation-v1.json')['tolerances']==read(R/'catalogue/evidence/reports/igs-analytical-history-v2.json')['tolerances']
# Source scalar-history missed-crossing counterexample, no stress trajectory generation.
h=-7.862141684009169e-6;d=1e-5;rad=1e-4
f=lambda x,inc:inc*(1-math.sqrt(abs(x)/rad))if x*inc>0 else inc
mid=lambda x,inc:x+f(x+f(x,inc)/2,inc)
full=mid(h,d);first=mid(h,d/2);half=mid(first,d/2);exact=memory(h,d,rad)
assert full==half and abs(exact-1.93701012831811e-6)<1e-19 and abs(half-exact)>2e-7
k1=f(first,d/2);k2=f(first+k1/2,d/2);k3=f(first+k2,d/2);defect=abs((k1-2*k2+k3)/6)/rad;assert defect>1e-6
out={'passed':True,'reports':reports,'original_failed_paths':v1failed,'tolerances_unchanged':True,'v2_max_native_path_ratio':allpathmax,'v2_max_saved_reference_refinement_ratio':refmax,'v2_max_analytical_history_ratio':analyticalmax,'hidden_crossing':{'midpoint_and_two_half':half,'analytical':exact,'missed_error':abs(half-exact),'scaled_endpoint_defect':defect},'rollback_scope':'three invalid-parent rejections only; no late-failure/host transaction claim','compiled_calls':0,'builds':0,'reference_trajectory_generation':False}
print(json.dumps(out,indent=2))

# Verify original source algebra and explicit-state crosswalk without compiled calls.
import subprocess
for script,extra,saved in [('docs/ingestion/hypoplastic-sand-igs97/original-equation-review-v3/check.py',[],'algebra-checks.json'),('docs/ingestion/hypoplastic-sand-igs97/check_crosswalk.py',['--repo',str(R)],'contract-checks.json')]:
 z=subprocess.run([sys.executable,'-B',str(R/script),*extra],cwd=R,capture_output=True,text=True);assert z.returncode==0,z.stderr;assert json.loads(z.stdout)==read(O/saved)
# Exact finite common-runtime evidence, not all303 historical cases on this runtime.
B=R/'docs/reviews/common-scalar-functions-v1/actual-root-v1';freeze=read(B/'source-freeze.json')['files']
for p in ['models/hypoplastic-sand-igs97.json','tests/test_solver.cpp','tools/test_wasm.mjs','cpp/include/atlas/solver.hpp']:assert sha(R/p)==freeze[p],p
assert any(r['name']=='native_numerical'and r['exit_code']==0 for r in read(B/'native-gate-processes.json'))
assert any(r['name']=='legacy'and r['exit_code']==0 for r in read(B/'wasm-gate-processes.json'))
assert 'IGS analytical crossing and cyclic history passed for 6 increments.'in(B/'legacy.log').read_text()
assert 'integration-settings checks passed'in(B/'native_numerical.log').read_text()
source=(R/'tests/test_solver.cpp').read_text()
for witness in ['odd budget lost late rollback','endpoint defect missed hidden branch','crossing history inaccurate','midpoint pair exceeded one-step budget']:assert witness in source
original=read(R/'catalogue/investigations/igs-original-rates-v1.json');assert original['count']==original['passed']==576 and original['model_sha256']==sha(R/'models/hypoplastic-sand-igs97.json')and original['parameters']['beta']==1
for receipt in ['hypoplastic-sand-igs97-investigation-v1','hypoplastic-sand-igs97-analytical-history-v2']:
 a=read(R/'catalogue/evidence'/f'{receipt}.json');assert a['model']['definition_sha256']==sha(R/'models/hypoplastic-sand-igs97.json')
 for row in a['artifacts']:assert sha(R/row['path'])==row['sha256']
if '--private-source'in sys.argv:
 for s in read(O/'source-reading.json')['sources']:assert sha(s['local_private_path'])==s['sha256']
if '--private-artifacts'in sys.argv:
 for s in read(B/'durable-artifacts.json')['artifacts']:assert sha(R/s['durable_path'])==s['sha256']
sys.path.insert(0,str(R));from atlas.agent_review import validate_review;assert validate_review(O/'review.json',root=R,for_approval=True)['status']=='accepted'
for n,h in read(O/'manifest.json').items():assert sha(O/n)==h,n
