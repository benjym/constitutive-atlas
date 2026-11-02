"""Execute only the frozen independent reference study; preserve domain/convergence failures."""
from oracle import *
import time
ROOT=Path(__file__).parent

def cases():
 zero=[ZERO]*6
 out=[{'id':'dry_hold','dry':True},{'id':'near_hold'}]
 for k in range(6):
  for sign in [-1,1]:
   v=list(zero);v[k]=D(sign)*D('2e-8');out.append({'id':f'basis_{k}_{sign:+}','mech':v})
 out += [{'id':'anisotropic_hold','anisotropic':True},{'id':'anisotropic_mixed_mechanical','anisotropic':True,'mech':[D(k)*D('1e-8') for k in [2,-1,3,-2,1,-3]]}]
 for branch in [False,True]:
  for label,sd,td in [('drying','2000','0'),('wetting','-2000','0'),('heating','0','.02'),('cooling','0','-.02'),('opposing_mixed','2000','.02')]:
   out.append({'id':('branch_' if branch else 'BCV_')+label,'branch':branch,'sd':D(sd),'Td':D(td)})
 for scan in ['0','1']:
  for sd in ['-2000','2000']:out.append({'id':f'scan_{scan}_sd_{sd}','scan':D(scan),'sd':D(sd)})
 out += [{'id':'rate_independent_hold','overrides':{'vf':ZERO}},{'id':'IvT_zero_hold','overrides':{'IvT':ZERO}}]
 return out

def point(case,precision):
 with localcontext() as c:
  c.prec=precision;p=params(case.get('branch',False));p.update(case.get('overrides',{}));y,s,T=initial(p,case.get('scan',D('.35')),case.get('dry',False),case.get('anisotropic',False));sd=case.get('sd',ZERO);Td=case.get('Td',ZERO);mech=case.get('mech',[ZERO]*6)
  rates,obs=rate(y,s,T,sd,Td,mech,p,True)
  return {'initial_state':y,'suction_Pa':s,'temperature_K':T,'suction_rate_Pa_per_s':sd,'temperature_rate_K_per_s':Td,'mechanical_rate_per_s':mech,'parameter_overrides':case.get('overrides',{})|({'ns':p['ns'],'ls':p['ls'],'lT':p['lT']} if case.get('branch') else {}),'rate':rates,'observables':obs}

def compare(a,b,absolute,relative):
 errors=[abs(x-y) for x,y in zip(a,b)];ratios=[err/(absolute+relative*max(abs(x),abs(y))) for x,y,err in zip(a,b,errors)]
 return {'pass':all(r<=1 for r in ratios),'absolute_errors':errors,'max_tolerance_ratio':max(ratios,default=ZERO)}
def rate_comparison(a,b):
 return {'stress':compare(a[:6],b[:6],D('1e-8'),D('1e-7')),'scalar':compare(a[6:],b[6:],D('1e-12'),D('1e-7'))}

def points():
 result=[]
 for case in cases():
  try:
   a=point(case,70);b=point(case,100);result.append({'id':case['id'],'status':'pass','reference':b,'precision_convergence':rate_comparison(a['rate'],b['rate'])})
  except (DomainError,ArithmeticError) as e:result.append({'id':case['id'],'status':'failed','error':str(e)})
 invalid=[]
 with localcontext() as c:
  c.prec=70;p=params();y,s,T=initial(p)
  for label in ['zero_suction','negative_suction','negative_macrovoid','Iv_nonpositive','scan_below_zero','scan_above_one','nonpositive_micro_pressure']:
   z=list(y);ss=s;tt=T
   if label=='zero_suction':ss=ZERO
   if label=='negative_suction':ss=-ONE
   if label=='negative_macrovoid':z[6]=D('.1')
   if label=='Iv_nonpositive':tt=D(100)
   if label=='scan_below_zero':z[7]=D('-.01')
   if label=='scan_above_one':z[7]=D('1.01')
   if label=='nonpositive_micro_pressure':z[:3]=[-2*s]*3
   try:rate(z,ss,tt,ZERO,ZERO,[ZERO]*6,p);invalid.append({'id':label,'status':'failed','error':'invalid context was accepted'})
   except (DomainError,ArithmeticError) as e:invalid.append({'id':label,'status':'refused','reason':str(e)})
 return {'identity':'frozen plan independent point reference','plan_sha256':'facc17e21d786328f4b28e8c20d9d3e5b1909becb3e3d971195ca5d7c9435a63','cases':result,'invalid_cases':invalid}

def trajectory(label,n,precision):
 with localcontext() as c:
  c.prec=precision;p=params();y,s0,T0=initial(p,dry=label.startswith('dry'));initial_y=list(y)
  duration=D(3600 if label=='near_hold_3600' else 1000 if label.endswith('1000') else 100);dt=duration/n
  def controls(t,phase):
   sd=ZERO;td=ZERO;s=s0;T=T0
   if label=='mixed_ramp_100':sd=D(2000);td=D('.02');s=s0+sd*t;T=T0+td*t
   if label=='hydraulic_reversal_100':
    sd=D(2000) if phase==0 else D(-2000);s=s0+D(2000)*(t if t<=50 else 100-t)
   return s,T,sd,td
  def derivative(z,t,phase):
   s,T,sd,td=controls(t,phase);return rate(z,s,T,sd,td,[ZERO]*6,p)
  def shifted(z,k,h):return [a+h*b for a,b in zip(z,k)]
  for i in range(n):
   t=dt*i;phase=0 if t<50 else 1;k1=derivative(y,t,phase);k2=derivative(shifted(y,k1,dt/2),t+dt/2,phase);k3=derivative(shifted(y,k2,dt/2),t+dt/2,phase);k4=derivative(shifted(y,k3,dt),t+dt,phase)
   y=[v+dt*(a+2*b+2*d+e)/6 for v,a,b,d,e in zip(y,k1,k2,k3,k4)]
  s,T,sd,td=controls(duration,1);rates,obs=rate(y,s,T,sd,td,[ZERO]*6,p,True)
  return {'partitions':n,'precision':precision,'duration_s':duration,'initial_state':initial_y,'final_state':y,'change':[b-a for a,b in zip(initial_y,y)],'endpoint_suction_Pa':s,'endpoint_temperature_K':T,'endpoint_rate':rates,'endpoint_observables':obs}

def state_comparison(a,b):
 return {'stress':compare(a['final_state'][:6],b['final_state'][:6],D('.01'),D('1e-7')),'scalar':compare(a['final_state'][6:],b['final_state'][6:],D('1e-9'),D('1e-7')),'observables':compare([a['endpoint_observables'][k] for k in ['em','eM','S','Sr','OA','re']],[b['endpoint_observables'][k] for k in ['em','eM','S','Sr','OA','re']],D('1e-8'),D('1e-7'))}

def run_trajectories():
 for label in ['near_hold_1000','near_hold_3600','dry_hold_1000','mixed_ramp_100','hydraulic_reversal_100']:
  runs=[];started=time.monotonic()
  for n,precision in [(64,70),(128,70),(256,70),(256,50)]:
   try:runs.append({'status':'pass','result':trajectory(label,n,precision)})
   except (DomainError,ArithmeticError) as e:runs.append({'status':'failed','partitions':n,'precision':precision,'error':str(e)})
  out={'id':label,'runs':runs,'runtime_seconds':str(time.monotonic()-started)}
  if all(x['status']=='pass' for x in runs):
   out['partition_convergence']=state_comparison(runs[1]['result'],runs[2]['result']);out['precision_convergence']=state_comparison(runs[3]['result'],runs[2]['result'])
  (ROOT/(label+'.json')).write_text(json.dumps(stringify(out),indent=2)+'\n');print(label,[r['status'] for r in runs],flush=True)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('mode',nargs='?',choices=['points','trajectories'],default='points');parser.add_argument('--output',type=Path,default=ROOT);args=parser.parse_args();ROOT=args.output;ROOT.mkdir(parents=True,exist_ok=True)
 if args.mode=='trajectories':run_trajectories()
 else:
  out=points();(ROOT/'point-results.json').write_text(json.dumps(stringify(out),indent=2)+'\n');print('points',len(out['cases']),'accepted',sum(x['status']=='pass' for x in out['cases']),'invalid refused',sum(x['status']=='refused' for x in out['invalid_cases']))
