"""Source-only request/corpus generation; never observes native AD."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
from decimal import Decimal
import json,hashlib,math
from decimal_dsl import context,evaluate_model,expression,Sym,binary,Rejected
def unique_pairs(xs):
 d={}
 for k,v in xs:
  if k in d:raise Rejected('duplicate JSON key')
  d[k]=v
 return d
def input_float(text):
 x=float(text)
 if x!=x or abs(x)==float('inf'):raise Rejected('nonfinite JSON number')
 return x
D=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text(),object_pairs_hook=unique_pairs,parse_float=input_float,parse_constant=lambda x:(_ for _ in()).throw(Rejected('nonfinite JSON')));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
SOURCE=Path(read(D/'source-freeze.json')['directory']);MODEL=SOURCE/'models/manzari-dafalias-1997-constant-m-be-v1.json'
hexes=lambda xs:[float(x).hex()for x in xs]
def layout(model):
 rows=[];offset=0
 for field in model['state']:
  size=6 if field['shape']=='sym'else 1;rows.append(dict(name=field['name'],shape=field['shape'],offset=offset,size=size));offset+=size
 return rows,offset

def unflatten(vals,fields):
 return {x['name']:tuple(vals[x['offset']:x['offset']+x['size']])if x['shape']=='sym'else vals[x['offset']]for x in fields}
def decode(xs):return [Decimal.from_float(float.fromhex(x))for x in xs]
def calculate(model,requests,flat,precision):
 with context(precision):
  params={k:Decimal.from_float(float.fromhex(v))for k,v in requests['parameters_hex'].items()};fields=requests['layout'];out,env=evaluate_model(model,unflatten(decode(flat),fields),unflatten(decode(requests['previous_hex']),fields),decode(requests['loading_hex']),params)
  branch=[expression(s,env)for s in requests['branch_expressions']]
  # Exclude nondifferentiable sign-zero points explicitly.
  for name in requests['nonzero_symbols']:
   if env[name]==0:raise Rejected('nondifferentiable '+name)
  return out,branch

def main():
 model=read(MODEL);fields,n=layout(model);assert n==14
 initial=[]
 for f in model['state']:initial.extend(f['initial']if f['shape']=='sym'else[f['initial']])
 z=list(initial);z[:4]=[110000.,95000.,100000.,500.];z[13]=.0001;params={k:v['default']for k,v in model['parameters'].items()}
 with context(120):scales=[]
 # Scale expressions are transported as original binary64 state seeds.
 for f in model['state']:
  with context(120):s=float(expression(f['scale'],{k:binary(v)for k,v in params.items()}))
  scales.extend([s]*(6 if f['shape']=='sym'else 1))
 assert scales==[160000.]*6+[1.]*8
 q=dict(identity='md1997-decimal-fd-requests-v1',model_sha256=sha(MODEL),base_source_freeze_sha256=sha(D/'source-freeze.json'),fixture_sha256=sha(SOURCE/'tests/test_solver.cpp'),layout=fields,state_hex=hexes(z),previous_hex=hexes(initial),loading_hex=hexes([.00001,-.000005,-.000005,.000003,0.,0.]),parameters_hex={k:float(v).hex()for k,v in params.items()},scales_hex=hexes(scales),branch_expressions=['relative_norm>0','psi>0','bn>0','D_raw>0'],nonzero_symbols=['relative_norm','psi','bn','D_raw'],columns=14,rows=14,levels=2,endpoints=[])
 for column in range(n):
  direction=[float(j==column)for j in range(n)];h=5e-11 if 7<=column<=9 else 1e-6
  for level in range(2):
   step=h/(2**level)
   for sign in [1,-1]:
    state=list(z)
    for j in range(n):
     delta=step*scales[j]*direction[j]
     if sign==1:state[j]+=delta
     else:state[j]-=delta
    q['endpoints'].append(dict(column=column,level=level,sign=sign,step_hex=step.hex(),direction_hex=hexes(direction),state_hex=hexes(state)))
 write(D/'requests.json',q)
 byprecision={};branches={}
 for prec in [80,120]:
  _,branch=calculate(model,q,q['state_hex'],prec);branches[str(prec)]=branch;rows=[]
  for e in q['endpoints']:
   r,b=calculate(model,q,e['state_hex'],prec)
   if b!=branch:raise Rejected('endpoint branch changed')
   rows.append([str(x)for x in r])
  secants=[]
  with context(prec):
   for i in range(0,56,2):
    plus,minus=rows[i:i+2];den=2*Decimal.from_float(float.fromhex(q['endpoints'][i]['step_hex']));secants.append([str((Decimal(a)-Decimal(b))/den)for a,b in zip(plus,minus)])
  byprecision[str(prec)]=dict(residuals=rows,secants=secants)
 stability=[]
 with context(120):
  for kind in ['residuals','secants']:
   for idx,(a,b)in enumerate(zip(byprecision['80'][kind],byprecision['120'][kind])):
    for row,(aa,bb)in enumerate(zip(a,b)):
     aa,bb=Decimal(aa),Decimal(bb);err=abs(aa-bb);budget=Decimal('1e-20')*max(1,abs(aa),abs(bb))
     if err>budget:raise Rejected('precision disagreement')
     stability.append(err/max(1,abs(aa),abs(bb)))
  # This is a frozen source-only reference h/h2 check, not native AD.
  for col in range(14):
   for a,b in zip(byprecision['120']['secants'][2*col],byprecision['120']['secants'][2*col+1]):
    a,b=Decimal(a),Decimal(b)
    if abs(a-b)>=Decimal('1.5e-5')*max(1,abs(a),abs(b)):raise Rejected('reference h/h2 gate')
 ref=dict(identity='md1997-decimal-fd-reference-v1',request_sha256=sha(D/'requests.json'),model_sha256=sha(MODEL),base_source_freeze_sha256=sha(D/'source-freeze.json'),policy_sha256=sha(D/'POLICY.md'),evaluator_sha256=sha(D/'decimal_dsl.py'),generator_sha256=sha(D/'generate.py'),precisions=[80,120],data=byprecision,branch=branches,precision_max_scaled_difference=str(max(stability)),native_ad_observations=0,source_only=True)
 write(D/'reference.json',ref);print('Frozen56endpoint/28secant corpus; precision stability',ref['precision_max_scaled_difference'])
if __name__=='__main__':main()
