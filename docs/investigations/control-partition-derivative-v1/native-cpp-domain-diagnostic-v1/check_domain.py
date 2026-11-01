from pathlib import Path
import copy,hashlib,json,sys
SOURCE=Path('/private/tmp/atlas-control-partition-v1/source');sys.path.insert(0,str(SOURCE))
from atlas.model import load,defaults,evaluation_environment,state_role
from atlas.dsl import parse,evaluate
D=Path(__file__).resolve().parent
m=load(SOURCE/'models/manzari-dafalias-1997-constant-m-be-v1.json')
p=defaults(m);initial={f['name']:copy.deepcopy(f['initial'])for f in m['state']};z=copy.deepcopy(initial)
z['sigma'][:4]=[110000,95000,100000,500]
for f in m['state']:
 if state_role(f)=='plastic_multiplier':z[f['name']]=.0001
increment=[.00001,-.000005,-.000005,.000003,0,0]
def violations(s,previous=initial,de=increment):
 e=evaluation_environment(m,s,previous,de,p,_check_domain=False)
 return [c for c in m['domain']if not evaluate(parse(c),e)]
assert not violations(z)
probes=[];offset=0
for f in m['state']:
 scale=evaluate(parse(f['scale']),p);n=6 if f['shape']=='sym'else 1
 for j in range(n):
  pair=[]
  for sign in [1,-1]:
   a=copy.deepcopy(z)
   if n==6:a[f['name']][j]+=sign*1e-6*scale
   else:a[f['name']]+=sign*1e-6*scale
   pair.append({'sign':sign,'violations':violations(a),'alpha_trace':sum(a['alpha'][:3])})
  probes.append({'flat_index':offset+j,'field':f['name'],'component':j,'scale':scale,'perturbation':1e-6*scale,'probes':pair})
 offset+=n
bad=[x for x in probes if any(p['violations']for p in x['probes'])]
assert [x['flat_index']for x in bad]==[7,8,9]
assert all(v['violations']==['abs(trace(alpha)) <= 1e-10']for x in bad for v in x['probes'])
rotation=copy.deepcopy(initial);rotation['sigma'][0]=105000;rotation['sigma'][1]=95000;rotation['sigma'][3]=1000
re=evaluation_environment(m,rotation,rotation,[0]*6,p,_check_domain=False)
rejected_initial=[c for c in m['initial_checks']if not evaluate(parse(c),re)]
result={'identity':'md1997-existing-native-domain-diagnostic-v1','model_sha256':hashlib.sha256((SOURCE/'models/manzari-dafalias-1997-constant-m-be-v1.json').read_bytes()).hexdigest(),'compiled_calls':0,'model_or_gate_changes':False,'base_valid':True,'state':z,'increment':increment,'generic_fd_h':1e-6,'all14_state_probe_receipts':probes,'invalid_indices':[x['flat_index']for x in bad],'source_trace_tolerance':1e-10,'generic_alpha_diagonal_probe_trace_abs':1e-6,'generic_rotation_state':rotation,'rotation_initial_rejections':rejected_initial,'conclusion':'Independent diagonal alpha perturbations violate the declared traceless-state domain by10000times. Generic rotation prestress also violates source initial yield admissibility. This explains fixture incompatibility but does not convert the actual native failure into a pass. A distinct prospective source-admissible test profile requires independent review.'}
(D/'checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'invalid_fd_indices':result['invalid_indices'],'rotation_initial_rejections':rejected_initial,'compiled_calls':0}))
