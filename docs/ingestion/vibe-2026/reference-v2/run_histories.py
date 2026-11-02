"""Frozen v2 mechanical histories using unchanged independent v1 source oracle."""
from pathlib import Path
import sys,json,hashlib,argparse
ROOT=Path(__file__).parent
V1=ROOT.parent/'reference-v1'
# Verify the dependency against its frozen manifest before importing any source reference.
m=json.loads((V1/'manifest.json').read_text())
assert hashlib.sha256((V1/'manifest.json').read_bytes()).hexdigest()=='04dd3a8831e83cada428a38479f72908f8f1ed03ea640df4b4c9826dabf0d079'
for item in m['files']:
 if Path(item['path']).name in ['oracle.py','run_reference.py']:
  assert hashlib.sha256((V1/Path(item['path']).name).read_bytes()).hexdigest()==item['sha256']
sys.path.insert(0,str(V1))
from oracle import D,ZERO,ONE,localcontext,params,initial,rate,DomainError,stringify
from run_reference import state_comparison

def trajectory(label,n,precision):
 with localcontext() as c:
  c.prec=precision;p=params();y,s0,T0=initial(p);initial_y=list(y);duration=D(100);dt=duration/n
  base=[D(k)*D('1e-8') for k in [2,-1,3,-2,1,-3]]
  def controls(t,phase):
   sd=D(2000) if label=='coupled_mechanical_THM_100' else ZERO;td=D('.02') if label=='coupled_mechanical_THM_100' else ZERO
   mech=[-v for v in base] if label=='mechanical_reversal_100' and phase==1 else list(base)
   return s0+sd*t,T0+td*t,sd,td,mech
  def derivative(z,t,phase):
   s,T,sd,td,mech=controls(t,phase);return rate(z,s,T,sd,td,mech,p)
  def shifted(z,k,h):return [a+h*b for a,b in zip(z,k)]
  for i in range(n):
   t=dt*i;phase=0 if t<50 else 1
   k1=derivative(y,t,phase);k2=derivative(shifted(y,k1,dt/2),t+dt/2,phase);k3=derivative(shifted(y,k2,dt/2),t+dt/2,phase);k4=derivative(shifted(y,k3,dt),t+dt,phase)
   y=[v+dt*(a+2*b+2*d+e)/6 for v,a,b,d,e in zip(y,k1,k2,k3,k4)]
  s,T,sd,td,mech=controls(duration,1);rates,obs=rate(y,s,T,sd,td,mech,p,True)
  return {'partitions':n,'precision':precision,'duration_s':duration,'initial_state':initial_y,'final_state':y,'change':[b-a for a,b in zip(initial_y,y)],'endpoint_suction_Pa':s,'endpoint_temperature_K':T,'endpoint_suction_rate_Pa_per_s':sd,'endpoint_temperature_rate_K_per_s':td,'endpoint_mechanical_rate_per_s':mech,'endpoint_rate':rates,'endpoint_observables':obs}

def run(output):
 output.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256((ROOT/'plan.json').read_bytes()).hexdigest()=='6dd5a3b20eabcac10ffe82e0385d72cd37364009133a92c596898d0b322e814d'
 for label in ['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100']:
  runs=[]
  for n,precision in [(64,70),(128,70),(256,70),(256,50)]:
   try:runs.append({'status':'pass','result':trajectory(label,n,precision)})
   except (DomainError,ArithmeticError) as e:runs.append({'status':'failed','partitions':n,'precision':precision,'error':str(e)})
  out={'id':label,'runs':runs}
  if all(x['status']=='pass' for x in runs):
   out['coarse_partition_comparison']=state_comparison(runs[0]['result'],runs[1]['result']);out['partition_convergence']=state_comparison(runs[1]['result'],runs[2]['result']);out['precision_convergence']=state_comparison(runs[3]['result'],runs[2]['result'])
  (output/(label+'.json')).write_text(json.dumps(stringify(out),indent=2)+'\n');print(label,[r['status'] for r in runs],flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT);args=parser.parse_args();run(args.output)
