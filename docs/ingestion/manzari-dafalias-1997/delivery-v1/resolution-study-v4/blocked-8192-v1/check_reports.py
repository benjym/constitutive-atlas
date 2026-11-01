#!/usr/bin/env python3
"""Check saved generic backend reports against frozen original-source requests."""
import argparse,hashlib,json,math
from pathlib import Path
from prepare import rot
D=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nearpoint(points,x):return next((p for p in points if p['coordinate']==x),None)
def finite(v):return isinstance(v,list) and all(isinstance(x,(int,float)) and math.isfinite(x) for x in v)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('reports',nargs='+');ap.add_argument('--output',required=True);args=ap.parse_args();plan=json.loads((D/'requests.json').read_text());checks=[]
 def add(backend,case,channel,passed,**details):checks.append({'backend':backend,'case':case,'channel':channel,'passed':bool(passed),**details})
 def vector(backend,case,channel,a,b,atol,rtol=0):
  if not finite(a) or not finite(b) or len(a)!=len(b):add(backend,case,channel,False,reason='missing, nonfinite or wrong length');return math.inf
  errors=[abs(x-y) for x,y in zip(a,b)];tols=[atol+rtol*max(1,abs(x),abs(y)) for x,y in zip(a,b)]
  worst=max([e/t for e,t in zip(errors,tols)],default=0);add(backend,case,channel,worst<=1,max_error=max(errors,default=0),max_normalized_error=worst);return worst
 for path in args.reports:
  report=json.loads(Path(path).read_text());backend=report.get('identity',{}).get('backend',str(path));case_results=report.get('cases',{});errors={}
  for key,file in [('requests_sha256','requests.json'),('policy_sha256','POLICY.md'),('manifest_sha256','manifest.json')]:add(backend,'identity',key,report.get('identity',{}).get(key)==digest(D/file))
  add(backend,'identity','model_sha256',report.get('identity',{}).get('model_sha256')==plan['model_sha256'])
  for c in plan['cases']:
   r=case_results.get(c['id'],{});cid=c['id'];add(backend,cid,'operational-success',r.get('ok') is True)
   if c['kind']=='chain':add(backend,cid,'all-increments-returned',len(r.get('points',[]))==len(c['coordinates']))
   elif c['kind']=='controls':
    add(backend,cid,'all-controls-returned',len(r.get('points',[]))==len(c['controls']))
    meta=r.get('response_metadata',{});add(backend,cid,'exact-control-bits',meta.get('loading',{}).get('controls_bits')==c['controls_bits'])
   elif c['kind']=='run':add(backend,cid,'all-public-preset-points',len(r.get('points',[]))==c['steps']+1)
   for p in r.get('points',[]):add(backend,cid,'finite-state-'+str(p['coordinate']),finite(p.get('state')) and len(p['state'])==14)
   for cp in c.get('checkpoints',[]):
    coord=cp.get('axial_strain',cp.get('t'));p=nearpoint(r.get('points',[]),coord);label=str(coord)
    if p is None:add(backend,cid,'checkpoint-'+label,False,reason='exact reference checkpoint missing');errors[(cid,coord)]=math.inf;continue
    z=p.get('state');ref=cp['sigma_Pa']
    if not finite(z) or len(z)!=14:add(backend,cid,'checkpoint-state-'+label,False,reason='invalid full state');errors[(cid,coord)]=math.inf;continue
    stress_errors=[abs(a-b)/(100+.01*max(1000,abs(b))) for a,b in zip(z[:6],ref)]
    add(backend,cid,'stress-source-'+label,max(stress_errors)<=1,max_normalized_error=max(stress_errors),errors_Pa=[abs(a-b) for a,b in zip(z[:6],ref)])
    av=vector(backend,cid,'alpha-source-'+label,z[7:13],cp['alpha'],.002);ev=vector(backend,cid,'void-source-'+label,[z[6]],[cp['e']],2e-4)
    rv=0
    if c['group']=='axis':rv=vector(backend,cid,'radial-source-'+label,p['strain'][1:3],[cp['radial_strain']]*2,2e-4)
    errors[(cid,coord)]=max(stress_errors+[av,ev,rv])
   if 'expected_state' in c:
    z=r.get('points',[{}])[-1].get('state',[]) if r.get('points') else []
    expected=c['expected_state'];stress_tol=50 if c['group']=='elastic-cycle' else 100
    vector(backend,cid,'analytic-stress',z[:6],expected[:6],stress_tol,0 if c['group']=='elastic-cycle' else .001)
    vector(backend,cid,'analytic-e',z[6:7],expected[6:7],1e-10 if c['group']=='elastic-cycle' else 2e-9)
    vector(backend,cid,'analytic-alpha',z[7:13],expected[7:13],1e-8)
   if c['group'] in ['restart','covariance']:
    source=case_results.get(c['compare_to'],{})
    if c['group']=='restart':add(backend,cid,'explicit-restart-receipt','restart_receipt' in r)
    for cp in c['checkpoints']:
     coord=cp['t'];a=nearpoint(r.get('points',[]),coord);b=nearpoint(source.get('points',[]),coord)
     if not a or not b:add(backend,cid,'matching-reference-point-'+str(coord),False);continue
     x,y=a.get('state'),b.get('state')
     if not finite(x) or not finite(y) or len(x)!=14 or len(y)!=14:add(backend,cid,'matching-valid-state-'+str(coord),False);continue
     if c['group']=='covariance':y=rot(y[:6],c['rotation'])+[y[6]]+rot(y[7:13],c['rotation'])+[0.]
     vector(backend,cid,'replay-covariance-stress-'+str(coord),x[:6],y[:6],1e-8 if c['group']=='restart' else 1e-5,0 if c['group']=='restart' else 2e-9)
     vector(backend,cid,'replay-covariance-e-'+str(coord),x[6:7],y[6:7],1e-12)
     vector(backend,cid,'replay-covariance-alpha-'+str(coord),x[7:13],y[7:13],1e-12 if c['group']=='restart' else 2e-9)
  for c in plan['cases']:
   if c['group'] not in ['axis','interior'] or c['resolution']!=8192:continue
   coarse=c['id'].rsplit('-',1)[0]+'-2048'
   for cp in c['checkpoints']:
    coord=cp.get('axial_strain',cp.get('t'))
    if coord==0:continue
    f=errors.get((c['id'],coord),math.inf);co=errors.get((coarse,coord),math.inf)
    add(backend,c['id'],'refinement-'+str(coord),math.isfinite(f) and math.isfinite(co) and (f<co or max(f,co)<1e-5),fine_normalized_error=f if math.isfinite(f) else None,coarse_normalized_error=co if math.isfinite(co) else None)
  sp=report.get('special',{});s=plan['special'];z=s['initial']
  for name in ['zero','hold','clean-valid','recovery-negative-pressure','recovery-alpha','recovery-nan-parameter','rollback-recovery']:add(backend,'special',name+'-success',sp.get(name,{}).get('ok') is True)
  for name in ['invalid-negative-pressure','invalid-alpha','invalid-nan-parameter','forced-rollback']:add(backend,'special',name+'-rejected',sp.get(name,{}).get('ok') is False and 'harness_error' not in sp.get(name,{}))
  for name in ['zero','hold','forced-rollback']:
   a=sp.get(name,{}).get('state',[]);vector(backend,'special',name+'-complete-stress',a[:6],z[:6],1e-8);vector(backend,'special',name+'-complete-parent-rest',a[6:],z[6:],1e-12)
  add(backend,'special','rollback-no-commit',sp.get('forced-rollback',{}).get('diagnostics',{}).get('partition_committed') is False)
  clean=sp.get('clean-valid',{}).get('state',[])
  for name in ['recovery-negative-pressure','recovery-alpha','recovery-nan-parameter','rollback-recovery']:
   a=sp.get(name,{}).get('state',[]);vector(backend,'special',name+'-stress',a[:6],clean[:6],1e-8);vector(backend,'special',name+'-persistent',a[6:13],clean[6:13],1e-12)
  lin=sp.get('linearize',{});tangent=lin.get('state_tangent');add(backend,'special','AD-tangent-success',lin.get('ok') is True and lin.get('tangent_ok') is True)
  add(backend,'special','AD-true-update-contract',lin.get('api_version')=='experimental-update-linearization-0.1' and lin.get('partition_policy')=='accepted_fixed' and lin.get('branch_policy')=='selected_fixed')
  shape=isinstance(tangent,list) and len(tangent)==14 and all(finite(row) and len(row)==6 for row in tangent);add(backend,'special','AD-tangent-shape',shape)
  if shape:
   for j in range(6):
    plus=sp.get('fd-'+str(j)+'-1',{});minus=sp.get('fd-'+str(j)+'--1',{});good=plus.get('ok') is True and minus.get('ok') is True and finite(plus.get('state')) and finite(minus.get('state')) and len(plus['state'])==14 and len(minus['state'])==14;add(backend,'special','FD-success-'+str(j),good)
    if not good:continue
    part=lin.get('diagnostics',{}).get('increment_fractions')
    add(backend,'special','FD-matching-partition-'+str(j),isinstance(part,list) and plus.get('diagnostics',{}).get('increment_fractions')==part and minus.get('diagnostics',{}).get('increment_fractions')==part)
    add(backend,'special','FD-plastic-branch-away-zero-'+str(j),len(lin.get('state',[]))==14 and lin['state'][13]>1e-10 and plus['state'][13]>1e-10 and minus['state'][13]>1e-10)
    for i in range(13):
     fd=(plus['state'][i]-minus['state'][i])/(2*s['fd_step']);ad=tangent[i][j];floor=1000 if i<6 else 1e-5 if i==6 else .01;tol=.002*max(1,abs(fd),abs(ad))+floor
     add(backend,'special','AD-FD-'+str(i)+'-'+str(j),abs(ad-fd)<=tol,AD=ad,FD=fd,error=abs(ad-fd),tolerance=tol)
 summary={'version':'md1997-resolution-study-checks-v4','passed':all(x['passed'] for x in checks),'checks':len(checks),'failures':sum(not x['passed'] for x in checks),'reports':[{'path':str(Path(p).resolve()),'sha256':digest(p)} for p in args.reports],'results':checks}
 Path(args.output).write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps({k:summary[k] for k in ['passed','checks','failures']}));raise SystemExit(0 if summary['passed'] else 1)
if __name__=='__main__':main()
