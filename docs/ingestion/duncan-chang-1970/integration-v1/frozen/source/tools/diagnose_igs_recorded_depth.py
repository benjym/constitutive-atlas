"""Read-only Python reproduction of IGS midpoint trials on the first recursive left descent.
No native execution, integration success claim, or repository mutations.
"""
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.model import load,interpret,evaluation_environment
from atlas.dsl import evaluate,parse
model_path=ROOT/'models/hypoplastic-sand-igs97.json'
m=load(model_path); params={n:v['default'] for n,v in m['parameters'].items()}
initial=[1e5,1e5,1e5,0,0,0,.7,0,0,0,0,0,0]
scales=[1e5]*6+[1]+[1e-4]*6
names=['sigma_'+x for x in ['xx','yy','zz','xy','yz','xz']]+['e']+['h_'+x for x in ['xx','yy','zz','xy','yz','xz']]
def state(z):return {'sigma':z[:6],'e':z[6],'h':z[7:]}
def sample(z,d,label,stages,return_rate=True):
 rec={'stage':label,'state':z,'increment':d}
 stages.append(rec)
 try:
  s=state(z);env=evaluation_environment(m,s,s,d,params,_check_domain=False)
  failed=[c for c in m['domain'] if not evaluate(parse(c),env)]
  rec.update(admissible=not failed,failed_conditions=failed,history_norm=env['hn'],rho=env['rho'])
  if failed:raise ValueError('state outside model domain')
  r=interpret(m,s,s,d,params)
  flat=list(r['sigma'].v)+[r['e']]+list(r['h'].v)
  rec['finite_rate']=all(math.isfinite(x) for x in flat)
  if not rec['finite_rate']:raise ValueError('nonfinite rate')
  return flat
 except Exception as e:
  rec['error']=str(e);raise

def mid(z,d,label,stages,endpoint_defect=False):
 k1=sample(z,d,label+' start',stages)
 zm=[a+.5*b for a,b in zip(z,k1)]
 k2=sample(zm,d,label+' midpoint',stages)
 out=[a+b for a,b in zip(z,k2)]
 # C++ domain(z) evaluates equations with zero increment.
 sample(out,[0.]*6,label+' domain(endpoint,zero increment)',stages)
 if not endpoint_defect:return out,None
 k3=sample(out,d,label+' endpoint defect',stages)
 return out,[(a-2*b+c)/6 for a,b,c in zip(k1,k2,k3)]

cases=[]
for total,tol,limit in [(.003,1e-6,14),(.003,1e-8,18),(.0015,1e-8,18)]:
 case=dict(total_increment=[total,0,0,0,0,0],rate_tolerance=tol,max_depth=limit,depths=[])
 for depth in range(21):
  d=[total/2**depth,0,0,0,0,0];stages=[]
  rec=dict(depth=depth,increment=d,stages=stages,within_configured_depth=depth<=limit)
  case['depths'].append(rec)
  try:
   full,_=mid(initial,d,'full',stages)
   half,ha=mid(initial,[x/2 for x in d],'first half',stages,True)
   two,hb=mid(half,[x/2 for x in d],'second half',stages,True)
   errors=[]
   for i,(a,b,c,e,s) in enumerate(zip(full,two,ha,hb,scales)):
    values=dict(component=names[i],full_minus_two=a-b,first_endpoint_defect=c,second_endpoint_defect=e,
                scaled_full_minus_two=abs(a-b)/s,scaled_first_endpoint_defect=abs(c)/s,scaled_second_endpoint_defect=abs(e)/s)
    values['scaled_max']=max(values[k] for k in ['scaled_full_minus_two','scaled_first_endpoint_defect','scaled_second_endpoint_defect'])
    errors.append(values)
   worst=max(errors,key=lambda a:a['scaled_max'])
   rec.update(stages_admissible=True,full=full,two=two,component_errors=errors,max_scaled_error=worst['scaled_max'],worst_component=worst['component'],passes_local_error=worst['scaled_max']<tol)
  except Exception as e:rec.update(stages_admissible=False,failure=str(e))
 cases.append(case)
report=dict(kind='python-midpoint-first-left-descent-diagnostic',repo='.',model='models/hypoplastic-sand-igs97.json',
 model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),solver_sha256=hashlib.sha256((ROOT/'cpp/include/atlas/solver.hpp').read_bytes()).hexdigest(),
 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),initial=initial,parameters=params,state_scales=scales,cases=cases,
 scope='Reproduces C++ midpoint evaluation order and local error at unchanged initial state for successive first-left dyadic increments. Does not execute native code, integrate full intervals, exercise mixed controls, prove global accuracy, or change scientific status.',
 asymptotic='For collinear positive loading from h=0, beta_r=1/2 gives dh/ds=1-sqrt(h/R). Its h(s) has a fractional s^(3/2) correction at the origin; full-vs-two and endpoint estimates therefore scale like increment^(3/2) locally, not smooth-path increment^3. Other state components and later segments require separate checks.')
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
out=args.output
with gzip.GzipFile(filename=str(out),mode='wb',mtime=0) as f:f.write((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({'report':str(out),'model_sha256':report['model_sha256'],'cases':[{'total':c['total_increment'][0],'first_passing_depth':next((r['depth'] for r in c['depths'] if r.get('passes_local_error')),None),'configured_depth':c['max_depth']} for c in cases]},indent=2))
