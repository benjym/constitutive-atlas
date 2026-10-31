from pathlib import Path
import sys,json,shutil,subprocess,gzip,math,copy
from decimal import Decimal,localcontext
r=Path('/Users/bmar5496/code/constitutive-atlas');stage=Path('/private/tmp/atlas-spectral-dsl-candidate-v1');out=Path('/private/tmp/atlas-spectral-source-check-results-v1');out.mkdir(exist_ok=True)
for name in ('models','atlas/numerics'):
 shutil.copytree(r/name,stage/name,dirs_exist_ok=True)
sys.path.insert(0,str(stage))
from atlas.dsl import Type,ZERO,PRESSURE,Sym,ValidationError,infer,parse,evaluate,cpp,has_value_only_dependency
from atlas.model import load,validate
from atlas.compiler import generate
from atlas.history_compiler import _expression
checks=[]
def check(label,cond):
 assert cond,label
 checks.append(label)
symbols={'A':Type('sym',PRESSURE),'B':Type('sym'),'p':Type(dim=PRESSURE),'v':Type(value_only=True),'x':Type()}
def typ(e):return infer(parse(e),symbols)
for name in ('principal_max_value','principal_mid_value','principal_min_value'):
 check(name+' units',typ(name+'(A)')==Type('scalar',PRESSURE,True))
for name in ('principal_max','principal_mid','principal_min','principal_upper_sum','principal_lower_sum'):
 check(name+' units',typ(name+'(A)')==Type('scalar',PRESSURE))
for name in ('projector_max','projector_min'):
 check(name+' units',typ(name+'(A)')==Type('sym'))
for e in ['v+x','x-v','v*x','x/v','v**x','x**v','sqrt(v)','exp(v)','log(v)','log1p(v)','sin(v)','cos(v)','abs(v)','min(x,v)','max(v,x)','trace(v*B)','norm(v*B)','dot(B,v*B)','cube_trace(v*B)','determinant(v*B)','normalized_determinant(v*B)','trace(expm(v*B))','trace(tensor_square(v*B))','trace(dev(v*B))','trace(sym(v,x,x,x,x,x))','principal_max(v*B)','trace(projector_max(v*B))','select(x>0,v,x)','select(v>0,x,v)']:
 check('propagate '+e,typ(e).value_only)
for e in ['v>x','select(v>x,x,0)','select(principal_max_value(A)>p,A,p*B)']:
 check('consume predicate '+e,not typ(e).value_only)
for e in ['(v>0)*1','1+(v>0)','-(v>0)','(v>0)**2','2**(v>0)','min(x,v>0)','principal_max(x)','projector_max(x)','principal_max(A,A)','sym(v,x,x,x,x)','principal_max(A)+x']:
 try:typ(e)
 except ValidationError:checks.append('reject '+e)
 else:raise AssertionError('accepted '+e)
# Value-only predicates never become reset-event guards through aliases.
check('reset indirect dependency',has_value_only_dependency(parse('select(v>0,1,0)'),{'v'}))
check('reset literal dependency',has_value_only_dependency(parse('select(principal_max_value(A)>p,1,0)')))
# Complete local model set validates and generates the exact previous header.
paths=sorted((r/'models').glob('*.json'))
old=out/'old-generated';new=out/'candidate-generated'
subprocess.run([sys.executable,'-B','-c','from atlas.compiler import generate;generate('+repr(str(old))+')'],cwd=r,check=True,capture_output=True)
generate(new,paths)
for name in ('models.hpp','models.json'):check('existing catalogue exact '+name,(old/name).read_bytes()==(new/name).read_bytes())
# Source validators reject numerical value-only leakage in real models.
m=load(r/'models/linear-elastic.json');stress=next(f['name']for f in m['state']if f['shape']=='sym')
for e in ['principal_max_value('+stress+')*I','select(1>0,'+stress+',principal_max_value('+stress+')*I)']:
 n=copy.deepcopy(m);n['equations'][stress]=e
 try:validate(n)
 except ValidationError:checks.append('equation rejects '+e)
 else:raise AssertionError('numeric sink accepted')
n=copy.deepcopy(m);n['derived'] += [{'name':'spectral_predicate_alias','expr':'principal_max_value('+stress+')'}];n['equations'][stress]='spectral_predicate_alias*I'
try:validate(n)
except ValidationError:checks.append('aliased numeric sink rejected')
else:raise AssertionError('alias sink accepted')
# Checked lazy contexts are present in both generators; compiled validation pending.
expr='select(principal_max_value(B)>0,projector_max(B),I)'
check('model spectral checked calls','atlas::spectral_scalar_or_mark' in cpp(parse(expr)) and 'atlas::spectral_projector_or_mark' in cpp(parse(expr)))
check('history spectral checked calls','atlas::spectral_candidate::scalar_checked' in _expression(parse(expr),{'B':'input_B'}) and 'atlas::spectral_candidate::projector_checked' in _expression(parse(expr),{'B':'input_B'}))
check('unselected failed operation is lazy',evaluate(parse('select(1>0,3,principal_max(B))'),{'B':Sym((1.,1.,1.,0.,0.,0.))})==3)
# Match independent pre-existing frozen primitive primal references and bounds.
ref=json.loads(gzip.decompress((r/'catalogue/investigations/symmetric-spectral-primitive-v1/reference/reference-p360.json.gz').read_bytes()));requests=json.loads(gzip.decompress((r/'catalogue/investigations/symmetric-spectral-primitive-v1/requests.json.gz').read_bytes()));byid={c['input']['id']:c for c in ref['cases']}
from atlas.symmetric_spectral import spectral
counts={'success':0,'expected_failure':0};worst=Decimal(0)
with localcontext()as ctx:
 ctx.prec=500;eps=Decimal(2)**-52;tiny=Decimal.from_float(float.fromhex('0x0.0000000000001p-1022'))*2
 for req in requests:
  if req['kind']!='double':continue
  op=req['operation'];values=[float.fromhex(x)for x in req['values']]
  try:observed=spectral(values,op)
  except ValueError as exc:
   check('reference failure '+req['id'],str(exc)==req['expected_status']);counts['expected_failure']+=1;continue
  check('reference success '+req['id'],req['expected_status']=='ok');counts['success']+=1;c=byid[req['case']];cr=c['reference'];e=list(map(Decimal,cr['eigenvalues']));norm=sum(Decimal.from_float(x)**2 for x in values).sqrt()
  if op.startswith('projector_'):
   i=0 if op=='projector_max'else 2;selected='max'if i==0 else'min';p=cr['selected'][selected]['projector'];p=[[Decimal(v)for v in row]for row in p];target=[p[0][0],p[1][1],p[2][2],Decimal(2).sqrt()*p[0][1],Decimal(2).sqrt()*p[1][2],Decimal(2).sqrt()*p[0][2]];error=sum((Decimal.from_float(x)-y)**2 for x,y in zip(observed,target)).sqrt();gap=min(abs(e[i]-e[j])for j in range(3)if j!=i);bound=2048*eps*norm/gap+tiny
  else:
   if op in ('upper_sum','lower_sum'):target=Decimal(cr['pair_sums']['upper'if op=='upper_sum'else'lower']['value'])
   else:target=e[0 if op in ('max','max_value')else 1 if op in ('mid','mid_value')else 2]
   error=abs(Decimal.from_float(observed)-target);bound=512*eps*norm+tiny
   if (cr['method'].startswith('diagonal')or cr['method']=='zero')and op not in('upper_sum','lower_sum'):check('exact diagonal '+req['id'],observed==float(target))
  check('independent accuracy '+req['id'],error<=bound);worst=max(worst,error/bound)
report={'checks':len(checks),'check_names':checks,'primal_reference_cases':counts,'worst_error_bound_fraction':str(worst),'compiled_observations':0,'production_installed':False,'scientific_admission':False}
(out/'source-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='check_names'}))
