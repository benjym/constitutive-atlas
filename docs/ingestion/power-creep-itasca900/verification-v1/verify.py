"""Independent source-equation history check. Prepare must precede observe."""
import sys,json,hashlib,subprocess,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from power_creep_study import reference_rate,csv
BINARY=Path('/private/tmp/atlas-power-creep-execution-v1/native/atlas_power_creep_solver')
MODEL=ROOT/'models/research/power-creep/power-creep-itasca900-both-active-ode.json'
P=[20e6,12e6,1e6,.002,1.5,.001,2.2,1]
INITIAL=[1.2e6,.9e6,.9e6,40000,-20000,10000]
PATH=[(2.,[.001,-.0004,.0001,.0003,-.0002,.0001]),(2.,[-.001,.0004,-.0001,-.0003,.0002,-.0001]),(1.,[.0002,.0002,.0002,0,0,0]),(3.,[0]*6)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def load(n):return json.loads((HERE/n).read_text())
def rk4(y,d,t,n):
 h=t/n
 for _ in range(n):
  a=reference_rate(y,d,P)[0];b=reference_rate([v+h*x/2 for v,x in zip(y,a)],d,P)[0]
  c=reference_rate([v+h*x/2 for v,x in zip(y,b)],d,P)[0];e=reference_rate([v+h*x for v,x in zip(y,c)],d,P)[0]
  y=[v+h*(aa+2*bb+2*cc+ee)/6 for v,aa,bb,cc,ee in zip(y,a,b,c,e)]
 return y
def energy(s):
 p=sum(s[:3])/3;dev=[v-(p if i<3 else 0) for i,v in enumerate(s)]
 return p*p/(2*P[0])+sum(v*v for v in dev)/(4*P[1])
def err(a,b):return max(abs(x-y) for x,y in zip(a,b))
def prepare():
 assert not (HERE/'freeze.json').exists()
 refs=[]
 for n in [1024,2048]:
  y=INITIAL[:];states=[]
  for t,d in PATH:y=rk4(y,d,t,n);states.append(y)
  refs.append(states)
 discrepancy=max(err(a,b) for a,b in zip(*refs))
 assert discrepancy<1e-5,discrepancy
 save('reference.json',{'method':'Independent Cartesian source RHS; classical RK4 with 1024 and 2048 steps per segment; no compiled observations','parameters':P,'initial':INITIAL,'path':PATH,'states':refs[1],'coarse_states':refs[0],'refinement_discrepancy_Pa':discrepancy})
 save('policy.json',{'scope':'Both active, dry small strain zero spin, n>=1; no threshold family validation','state_budget_Pa':.06,'invariance_budget_Pa':.06,'reference_refinement_budget_Pa':1e-5,'energy_increase_budget_J_per_m3':1e-7,'settings':{'rtol':1e-10,'atol':1e-13,'min_step':1e-12,'max_step':.1,'budget':200000},'variants':['baseline','restart_split_each_segment','clock_shift_100s','reference_stress_scaled_2','observable_time_scale_7'],'existing_evidence':'execution-v1/refinement-v2: 27 native and 27 Wasm requests; original failures retained'})
 files=[Path(__file__),ROOT/'tools/power_creep_study.py',MODEL,BINARY,HERE/'reference.json',HERE/'policy.json']
 save('freeze.json',{'files':{str(p):sha(p) for p in files},'observed':False})
 print('Prepared reference and prospective gates; discrepancy',discrepancy)
def observe():
 for p,h in load('freeze.json')['files'].items():assert sha(Path(p))==h,p
 ref=load('reference.json');policy=load('policy.json');checks=[];raw=HERE/'raw';raw.mkdir(exist_ok=False)
 for variant in policy['variants']:
  p=P[:];y=INITIAL[:];time=107. if variant=='clock_shift_100s' else 7.;states=[]
  if variant=='reference_stress_scaled_2':p[2]*=2;p[3]*=2**p[4];p[5]*=2**p[6]
  if variant=='observable_time_scale_7':p[7]=7
  for i,(t,d) in enumerate(PATH):
   before=y[:];parts=2 if variant=='restart_split_each_segment' else 1
   for j in range(parts):
    command=[str(BINARY),'--mode','integrate-time','--model','power-creep-itasca900-both-active-ode','--parameters',csv(p),'--initial',csv(y),'--strain-rate',csv(d),'--start-time',str(time),'--duration',str(t/parts),'--rtol','1e-10','--atol','1e-13','--min-time-step','1e-12','--max-time-step','.1','--max-substeps','200000']
    out=subprocess.run(command,capture_output=True,text=True);stem=f'{variant}-{i}-{j}'
    (raw/(stem+'.stdout')).write_text(out.stdout);(raw/(stem+'.stderr')).write_text(out.stderr)
    save('raw/'+stem+'.request.json',{'command':command,'returncode':out.returncode})
    assert out.returncode==0,(stem,out.stderr)
    result=json.loads(out.stdout);y=result['state'];time=result['time']
   states.append(y)
   delta=err(y,ref['states'][i]);checks.append({'id':f'{variant}-reference-{i}','error_Pa':delta,'passed':delta<=policy['state_budget_Pa']})
   if i==3:
    diff=energy(y)-energy(before);checks.append({'id':variant+'-hold-energy','energy_change_J_per_m3':diff,'passed':diff<=policy['energy_increase_budget_J_per_m3']})
  if variant=='baseline':baseline=states
  else:
   delta=max(err(a,b) for a,b in zip(states,baseline));checks.append({'id':variant+'-invariance','error_Pa':delta,'passed':delta<=policy['invariance_budget_Pa']})
 save('report.json',{'passed':all(c['passed'] for c in checks),'checks':checks,'observations':24,'scientific_admission':False})
 print(json.dumps(load('report.json'),indent=2))
if __name__=='__main__':{'prepare':prepare,'observe':observe}[sys.argv[1]]()
