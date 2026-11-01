"""Independent endpoint construction and full corpus recomputation; source only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util
from decimal import Decimal as Q
D=Path(__file__).resolve().parent;A=D.parent/'native-decimal-reference-v1';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
spec=importlib.util.spec_from_file_location('corpus_decimal',A/'decimal_dsl.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
f=read(A/'source-freeze.json');source=Path(f['directory']);model=read(source/'models/manzari-dafalias-1997-constant-m-be-v1.json');q=read(A/'requests.json');r=read(A/'reference.json')
ck('model identity',sha(source/'models/manzari-dafalias-1997-constant-m-be-v1.json')==q['model_sha256']==r['model_sha256']=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
for key,file in [('request_sha256','requests.json'),('base_source_freeze_sha256','source-freeze.json'),('policy_sha256','POLICY.md'),('evaluator_sha256','decimal_dsl.py'),('generator_sha256','generate.py')]:ck('corpus pin '+key,r[key]==sha(A/file))
ck('fixture hash',q['fixture_sha256']==sha(source/'tests/test_solver.cpp'))
ck('scope',q['columns']==q['rows']==14 and q['levels']==2 and r['precisions']==[80,120]and r['native_ad_observations']==0 and r['source_only']is True)
layout=[('sigma','sym',0,6),('e','scalar',6,1),('alpha','sym',7,6),('gamma','scalar',13,1)];ck('exact layout',q['layout']==[dict(name=n,shape=s,offset=o,size=z)for n,s,o,z in layout])
hexes=lambda xs:[float(x).hex()for x in xs];base=[110000,95000,100000,500,0,0,.65,0,0,0,0,0,0,.0001];previous=[]
for field in model['state']:previous.extend(field['initial']if field['shape']=='sym'else[field['initial']])
ck('base and previous',q['state_hex']==hexes(base)and q['previous_hex']==hexes(previous));ck('loading',q['loading_hex']==hexes([.00001,-.000005,-.000005,.000003,0,0]));ck('scales',q['scales_hex']==hexes([160000]*6+[1]*8));ck('all parameters',q['parameters_hex']=={n:float(d['default']).hex()for n,d in model['parameters'].items()})
ck('56 endpoints',len(q['endpoints'])==56);idx=0
for col in range(14):
 for level in range(2):
  h=(5e-11 if 7<=col<=9 else 1e-6)/(2**level)
  for sign in [1,-1]:
   # Cartesian zeros leave all other values unchanged; match the exact sequential binary64 +/- expression.
   v=list(map(float,base));delta=h*(160000. if col<6 else 1.)
   v[col]=v[col]+delta if sign==1 else v[col]-delta
   expected=dict(column=col,level=level,sign=sign,step_hex=h.hex(),direction_hex=hexes([int(j==col)for j in range(14)]),state_hex=hexes(v));ck('endpoint '+str(idx),q['endpoints'][idx]==expected);idx+=1
unflatten=lambda xs:{n:tuple(xs[o:o+z])if s=='sym'else xs[o]for n,s,o,z in layout}
decode=lambda xs:[Q.from_float(float.fromhex(x))for x in xs]
for precision in [80,120]:
 with m.context(precision):
  params={n:Q.from_float(float.fromhex(v))for n,v in q['parameters_hex'].items()};out,env=m.evaluate_model(model,unflatten(decode(q['state_hex'])),unflatten(decode(q['previous_hex'])),decode(q['loading_hex']),params);branch=[m.expression(s,env)for s in q['branch_expressions']];ck('base branches '+str(precision),branch==r['branch'][str(precision)])
  data=r['data'][str(precision)];ck('full residual/secant coverage '+str(precision),len(data['residuals'])==56 and len(data['secants'])==28 and all(len(x)==14 for k in ['residuals','secants']for x in data[k]))
  for i,e in enumerate(q['endpoints']):
   out,env=m.evaluate_model(model,unflatten(decode(e['state_hex'])),unflatten(decode(q['previous_hex'])),decode(q['loading_hex']),params);ck('all residual '+str(precision)+'/'+str(i),list(map(str,out))==data['residuals'][i]and[m.expression(s,env)for s in q['branch_expressions']]==branch and all(env[n]!=0 for n in q['nonzero_symbols']))
  for i in range(28):
   den=2*Q.from_float(float.fromhex(q['endpoints'][2*i]['step_hex']));sec=[(Q(a)-Q(b))/den for a,b in zip(data['residuals'][2*i],data['residuals'][2*i+1])];ck('all secant '+str(precision)+'/'+str(i),list(map(str,sec))==data['secants'][i])
with m.context(120):
 differences=[]
 for kind in ['residuals','secants']:
  for a,b in zip(r['data']['80'][kind],r['data']['120'][kind]):
   for aa,bb in zip(a,b):
    aa,bb=Q(aa),Q(bb);v=abs(aa-bb)/max(1,abs(aa),abs(bb));ck('fixed precision stability '+str(len(differences)),v<=Q('1e-20'));differences.append(v)
 ck('stability summary exact',str(max(differences))==r['precision_max_scaled_difference'])
 for col in range(14):
  for row in range(14):
   a,b=[Q(r['data']['120']['secants'][2*col+level][row])for level in range(2)];ck('reference convergence '+str(col)+'/'+str(row),abs(a-b)<Q('1.5e-5')*max(1,abs(a),abs(b)))
print(json.dumps({'identity':'independent-decimal-corpus-review','checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0,'native_ad_observations':0},indent=2))
