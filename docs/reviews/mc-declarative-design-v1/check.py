"""Source-only declaration checks; no candidate compilation/execution."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,math,subprocess,hashlib,tempfile
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'frozen'))
from atlas.model import load,validate,evaluation_environment,interpret,defaults
from atlas.dsl import evaluate,parse,Type,infer,Sym,ValidationError
m=load(P/'model.json');validate(m)
freeze=json.loads((P/'prospective-policy.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'model.json')==freeze['model_sha256'] and sha(P/'policy.json')==freeze['policy_sha256']
source=P/'frozen/docs/ingestion/mohr-coulomb'
z=subprocess.run([sys.executable,'-B',str(source/'check_certificates.py')],capture_output=True,check=True)
cert=json.loads(z.stdout);assert cert==json.loads((source/'results.json').read_text())
parameters={'E':2.25,'nu':.125,'c':5.,'phi':math.asin(.6),'psi':math.asin(1/3),'p_ref':1.}
mandel=lambda a:[float(a[0][0]),float(a[1][1]),float(a[2][2]),math.sqrt(2)*float(a[0][1]),math.sqrt(2)*float(a[1][2]),math.sqrt(2)*float(a[0][2])]
diag=lambda a:[[a[i] if i==j else F(0) for j in range(3)]for i in range(3)]
rows=[];branches={0:'elastic',1:'face',2:'left',3:'right',4:'apex'}
for c in cert['certificates']:
 if 'source_tension_principal_trial'in c:
  t=list(map(F,c['source_tension_principal_trial']));ret=list(map(F,c['source_tension_return']))
 else:t=list(map(F,c['trial']));ret=t
 de=[-((x-sum(t)/3)/2+sum(t)/9)for x in t]
 cases=[('diagonal',mandel(diag(de)),mandel(diag([-x for x in ret])))]
 if 'compression_cartesian_increment'in c:
  frac=lambda a:[[F(x)for x in row]for row in a]
  cases.append(('rotated',mandel(frac(c['compression_cartesian_increment'])),mandel(frac(c['compression_cartesian_return']))))
 for form,loading,want in cases:
  parent={'sigma':[0.]*6};state={'sigma':want};snapshot=json.loads(json.dumps([parent,state,loading]))
  env=evaluation_environment(m,state,parent,loading,parameters)
  got=[-x for x in env['returned_source'].v];error=math.hypot(*[a-b for a,b in zip(got,want)])
  scale=max(1.,5.,math.hypot(*env['trial'].v),math.hypot(*want));bound=4096*sys.float_info.epsilon*scale
  assert error<=bound,(c['case'],form,error,bound)
  residual=interpret(m,state,parent,loading,parameters)['sigma'].v;assert list(residual)==[a-b for a,b in zip(want,got)]
  # Initial roundoff policy and zero-increment hold on returned stress.
  hold=evaluation_environment(m,{'sigma':got},{'sigma':got},[0.]*6,parameters)
  assert all(evaluate(parse(q),hold)for q in m['initial_checks'])
  hold_error=math.hypot(*[a+b for a,b in zip(got,hold['returned_source'].v)]);assert hold_error<=bound
  assert [parent,state,loading]==snapshot
  rows.append({'case':c['case'],'form':form,'exact_source_branch':c['branch'],'rounded_selected_branch':branches[int(env['branch'])],'error':error,'bound':bound,'fraction':error/bound,'hold_error':hold_error})
# Invalid parameter limits must reject; eager division may reject before domain.
invalid=[]
for k,v in [('E',0.),('c',0.),('nu',-1.),('nu',.5),('phi',0.),('phi',math.pi/2),('psi',0.),('psi',math.pi/2),('psi',-.1)]:
 try:evaluation_environment(m,{'sigma':[0.]*6},{'sigma':[0.]*6},[0.]*6,{**parameters,k:v})
 except (ValueError,ZeroDivisionError,OverflowError):invalid.append({'parameter':k,'value':v})
 else:raise AssertionError(('invalid parameter accepted',k,v))
with tempfile.TemporaryDirectory(prefix='atlas-mc-design-replay-')as tmp:
 out=Path(tmp);subprocess.run([sys.executable,'-B',str(P/'generate.py'),str(P/'frozen'),str(out)],capture_output=True,check=True)
 for rel in ['model.json','generated/models.hpp','generated/models.json']:assert (P/rel).read_bytes()==(out/rel).read_bytes(),rel
result={'identity':'mc-declarative-design-source-checks-v1','validated':True,'certificate_source_exact':True,'source_certificates':14,'floating_value_cases':len(rows),'rows':rows,'invalid_parameter_rejections':invalid,'copied_source_generated_files_exact':3,'compiled_observations':0,'scientific_admission':False}
print(json.dumps(result,indent=2))
