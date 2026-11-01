"""Independent saved-data MCC review; standard library only, no solver calls."""
import argparse,hashlib,json,math
from pathlib import Path
from fractions import Fraction as Q

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mean(a):return sum(a[:3])/3
def dev(a):
 p=mean(a);return [v-p if i<3 else v for i,v in enumerate(a[:6])]
def root(f,a,b):
 fa=f(a);fb=f(b);assert fa*fb<=0,(fa,fb)
 for _ in range(120):
  m=(a+b)/2;fm=f(m)
  if fa*fm>0:a=m;fa=fm
  else:b=m
 return (a+b)/2

def reference(z,d,P):
 _,M,lam,k,nu=P;p0=mean(z);pc0=z[7];V=sum(d[:3]);v=(1+z[6])*math.exp(-V)
 assert 1-v*V/k>0
 pe=p0/(1-v*V/k);dd=dev(d);s0=dev(z)
 def G(p):return 1.5*v*p/k*(1-2*nu)/(1+nu)
 def t(p):return [s+2*G(p)*x for s,x in zip(s0,dd)]
 def q2(s):return 1.5*sum(x*x for x in s)
 def pc(p):return pc0*math.exp((v*V-k*(1-p0/p))/(lam-k))
 te=t(pe)
 if q2(te)+M*M*pe*(pe-pc0)<=0:p=pe;c=pc0;g=0;s=te
 elif 2*pe==pc0:
  p=pe;c=pc0;fac=M*p/math.sqrt(q2(te));s=[x*fac for x in te];g=pc0/(6*G(p))*(1/fac-1)
 else:
  cp=root(lambda p:math.log(2*p/pc0)-(v*V-k*(1-p0/p))/(lam-k),min(p0,pe,pc0)*1e-8,max(p0,pe,pc0)*100)
  def f(p):
   c=pc(p);vp=V-k/v*(1-p0/p);a=2*p-c;b=a+6*G(p)*vp/(M*M)
   return q2(t(p))*(a/b)**2+M*M*p*(p-c)
  p=root(f,cp,pe);c=pc(p);vp=V-k/v*(1-p0/p);g=pc0*vp/(M*M*(2*p-c));s=[x/(1+6*G(p)*g/pc0) for x in t(p)]
 return [x+p if i<3 else x for i,x in enumerate(s)]+[v-1,c,g]

def budget(a,b):return max(abs(x-y)/( (1e-4 if i<6 or i==7 else 1e-9)+1e-9*abs(y)) for i,(x,y) in enumerate(zip(a,b)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);ap.add_argument('--private-source',type=Path,default=Path('/private/tmp/atlas-mcc-source-review-v3/ModifiedCamClay_report.pdf'));a=ap.parse_args();r=a.repo.resolve();out={};pins={}
 def read(n):pins[n]=sha(r/n);return json.loads((r/n).read_text())
 m=read('models/modified-cam-clay.json');assert pins['models/modified-cam-clay.json']=='e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14'
 pdf=a.private_source;assert sha(pdf)=='a03df6d05d777bfc4d484e6e12a2aecdebcbbf16bfca3b6601e699178620e9ce'
 out['private_source']={'path':str(pdf),'sha256':sha(pdf),'visual_pages':[2,3,5,6]}
 M=Q(6,5);p=Q(1,2);c=1;q=M*p;assert q*q+M*M*p*(p-c)==0;assert q*q+M*p*(p-c)!=0
 out['source_conflict_witnesses']={'selected_yield_at_critical_point':str(q*q+M*M*p*(p-c)),'printed_single_M':str(q*q+M*p*(p-c)),'printed_Eq7_porosity_rate':str((1+Q(1,3))*Q(1,100)),'Eq9_porosity_rate':str((1-Q(1,3))*Q(1,100))}
 rec=read('catalogue/evidence/modified-cam-clay-scalar-v2.json');report=read(rec['artifacts'][0]['path']);assert pins[rec['artifacts'][0]['path']]==rec['artifacts'][0]['sha256'];P=[v['default'] for v in m['parameters'].values()];rows=[]
 for C in report['cases']:
  if C['id'].startswith('continuum-'):
   V=C['total_volumetric_strain'];z=C['initial'];den=P[3] if 'elastic' in C['id'] else P[2];exact=mean(z)*math.exp((1+z[6])*(1-math.exp(-V))/den);errors=[abs(mean(l['final_state'])-exact)/exact for l in C['levels']];orders=[math.log(x/y,2) for x,y in zip(errors,errors[1:])];assert min(orders)>.8 and errors[-1]<5e-4 and all(not l['failed_steps'] for l in C['levels']);rows.append({'id':C['id'],'errors':errors,'orders':orders,'passed':True});continue
  if C['expected_failure']:
   assert C['actual']==C['initial'] and C['solver_ok'] is False and C['returncode']!=0;rows.append({'id':C['id'],'exact_rollback':True});continue
  params=[float(x) for x in C['arguments'][C['arguments'].index('--parameters')+1].split(',')];z=C['initial'][:];fractions=C['diagnostics']['increment_fractions'];assert math.fsum(fractions)==1 and len(fractions)==C['diagnostics']['substeps'] and all(x>0 for x in fractions)
  for f in fractions:z=reference(z,[f*x for x in C['strain_increment']],params)
  ratio=budget(C['actual'],z);assert ratio<=1,(C['id'],ratio);rows.append({'id':C['id'],'budget_fraction':ratio,'substeps':len(fractions)})
 out['saved_native_cases']=rows;assert len(rows)==57
 old=read('catalogue/evidence/modified-cam-clay-investigation-v1.json');oldr=read(old['artifacts'][0]['path']);assert pins[old['artifacts'][0]['path']]==old['artifacts'][0]['sha256'];out['retained_v1']={'outcome':old['outcome'],'failed_cases':[c['id'] for c in oldr['cases'] if not c['passed']]};assert old['outcome']=='failed'
 b='catalogue/investigations/laboratory-q-cancellation-v1/';assert sha(r/b/'frozen/models/modified-cam-clay.json')==pins['models/modified-cam-clay.json'];read(b+'frozen/models/modified-cam-clay.json')
 for n in ('manifest.json','evidence-manifest.json'):
  manifest=read(b+n)
  for name,h in manifest.items():
   pp=r/b/name
   if not pp.exists():pp=r/b/'frozen'/name
   assert sha(pp)==h,(name,h)
 out['frozen_package_integrity']=True
 for role in ('native','wasm','post'):
  receipt=read(b+role+'/receipt.json');assert receipt['completed'] and all(c['exit_code']==0 for c in receipt['commands'])
 read(b+'prospective-freeze.json');back=read(b+'post/backend-results.json');raw=read(b+'post/backend-results.json.raw.json');decoded=[json.loads(x['raw']) for x in raw];pairs=[]
 for pair in back['pairs']:
  if pair['specification'].get('model')!='modified-cam-clay':continue
  n=pair['native'];w=pair['wasm'];assert n in decoded and w in decoded and n['ok'] and w['ok'];assert len(n['points'])==len(w['points']);worst=0
  for x,y in zip(n['points'],w['points']):
   worst=max(worst,budget(x['state'],y['state']));assert worst<=1
   for pt in (x,y):
    s=pt['state'];vv=(1+pair['specification']['initial'][6])*math.exp(-sum(pt['strain'][:3]));assert abs((1+s[6])-vv)<1e-8;assert abs(pt['p']-mean(s))<1e-6;qq=math.sqrt(1.5*sum(v*v for v in dev(s)));assert abs(pt['q']-qq)<1e-4
  pairs.append({'name':pair['name'],'points_per_backend':len(n['points']),'parity_budget_fraction':worst,'roundtrip_replayed':pair.get('roundtrip_replayed')})
 out['historical_backend_pairs']=pairs;assert len(pairs)==11
 # Complete frozen admission pin scan preserves root drift; no repinning.
 work=read('docs/admission/production-readiness-v1/work-packages.json');drift=[];restored=0
 for n,h in work['inputs'].items():
  if sha(r/n)!=h:
   drift.append(n);snap=r/'catalogue/source-snapshots'/h/n;assert snap.exists() and sha(snap)==h;restored+=1
 out['historical_preflight_drift']=drift;out['exact_archive_reconstruction_inputs']=restored
 out['compiled_calls']=0;out['pins']=pins;out['passed']=True;txt=json.dumps(out,indent=2)+'\n'
 if a.output:a.output.write_text(txt)
 else:print(txt,end='')
if __name__=='__main__':main()
