"""Independent generated-context assessment. Standard library only; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import json,gzip,math,argparse,collections

def load(path):
 p=Path(path);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def number(x):
 if type(x)not in(int,float):return False
 try:return math.isfinite(x)and (not isinstance(x,int)or int(float(x))==x)
 except (OverflowError,ValueError):return False
def df(x):return D.from_float(float(x))
def norm(xs):return sum((x*x for x in xs),D(0)).sqrt()
def mandel(a):
 s=D(2).sqrt();return [D(a[0][0]),D(a[1][1]),D(a[2][2]),s*D(a[0][1]),s*D(a[1][2]),s*D(a[0][2])]
def selected(op):return 'min'if op in('min','projector_min','upper_sum')else'mid'if op=='mid'else'max'

class Study:
 def __init__(self,root):
  self.root=Path(root);self.requests=load(self.root/'requests.json.gz');self.policy=load(self.root/'policy.json');self.bounds=load(self.root/'reference/policy.json');self.slots=load(self.root/'slots.json');self.reference=load(self.root/'reference/reference/reference-p360.json.gz');self.cases={c['input']['id']:c for c in self.reference['cases']};self.cache={}
  assert len(self.requests)==self.policy['requests']==1589
  assert len({r['id']for r in self.requests})==len(self.requests)
  assert self.policy['columns']==38
  for r in self.requests:
   assert type(r['slot'])is int and 0<=r['slot']<len(self.slots)
   assert r['kind']in('double','jet')and type(r['expected_ok'])is bool
   assert r['expectation']in('spectral','constant','identity','none')
   assert len(r['values'])==6 and len(r['seeds'])==38 and all(len(x)==6 for x in r['seeds'])
   if r['expected_ok']and r['expectation']=='spectral':
    assert r['values']==self.cases[r['case']]['input']['mandel_hex'],r['id']
    assert r['seeds']==self.reference['seeds_mandel_hex'],r['id']
  # Assert exact old bound constants, not merely arbitrary policy keys.
  assert [self.bounds[k]for k in('value_absolute_error_eps_factor','projector_absolute_error_eps_factor','scalar_derivative_absolute_error_eps_factor','projector_derivative_absolute_error_eps_factor','subnormal_absolute_allowance_ulps')]==[512,2048,2048,8192,2]
 def spectral_target(self,r):
  key=(r['case'],r['operation'],r['kind'])
  if key in self.cache:return self.cache[key]
  c=self.cases[r['case']];ref=c['reference'];op=r['operation'];e=list(map(D,ref['eigenvalues']));isP=op.startswith('projector_');name=selected(op);i={'max':0,'mid':1,'min':2}[name]
  gap=None if op.endswith('_value')else min(abs(e[i]-e[j])for j in range(3)if i!=j)
  if isP:v=mandel(ref['selected'][name]['projector'])
  elif op in('upper_sum','lower_sum'):v=[D(ref['pair_sums']['upper'if op=='upper_sum'else'lower']['value'])]
  else:v=[e[{'max':0,'max_value':0,'mid':1,'mid_value':1,'min':2,'min_value':2}[op]]]
  derivatives=[]
  if r['kind']=='jet':
   for j in range(38):
    if op.endswith('_value'):derivatives.append([D(0)]*len(v))
    elif isP:derivatives.append(mandel(ref['selected'][name]['directions'][j]['projector']))
    elif op in('upper_sum','lower_sum'):derivatives.append([D(ref['pair_sums']['upper'if op=='upper_sum'else'lower']['directions'][j])])
    else:derivatives.append([D(ref['selected'][name]['directions'][j]['eigenvalue'])])
  ans=(v,derivatives,gap,c);self.cache[key]=ans;return ans
 def assess(self,rows):
  failures=[];counts=collections.Counter();worst={'fraction':'0','request':None,'channel':None}
  def fail(req,channel,detail=None):
   f={'request':req,'channel':channel}
   if detail is not None:f['detail']=detail
   failures.append(f)
  if not isinstance(rows,list):return {'passed':False,'failures':[{'request':None,'channel':'rows-must-be-list'}]}
  if len(rows)!=len(self.requests):fail(None,'row-count',{'expected':len(self.requests),'observed':len(rows)})
  with localcontext()as ctx:
   ctx.prec=500;eps=D(2)**-52;tiny=D(2)**-1074*2
   def accuracy(error,bound,r,channel):
    counts['independent_accuracy_checks']+=1;ratio=error/bound if bound else D(0)if error==0 else D('Infinity')
    if ratio>D(worst['fraction']):worst.update(fraction=str(ratio),request=r['id'],channel=channel)
    if error>bound:fail(r['id'],channel,{'error':str(error),'unchanged_bound':str(bound)})
   for index,(r,o)in enumerate(zip(self.requests,rows)):
    rid=r['id']
    if not isinstance(o,dict):fail(rid,'row-type');continue
    required={'id','slot','kind','ok','input_unchanged','output'};allowed=required|({'history'}if r.get('history')else set())|({'solver'}if r.get('solver')else set())
    if set(o)!=allowed:fail(rid,'row-keys',{'expected':sorted(allowed),'observed':sorted(o)});continue
    if o['id']!=rid or type(o['slot'])is not int or o['slot']!=r['slot']or o['kind']!=r['kind']:fail(rid,'request-identity-or-order');continue
    if type(o['ok'])is not bool or o['ok']!=r['expected_ok']:fail(rid,'expected-success',{'expected':r['expected_ok'],'observed':o['ok']})
    if o['input_unchanged']is not True:fail(rid,'input-mutated-or-unverified')
    if not isinstance(o['output'],list):fail(rid,'output-not-list');continue
    counts['expected_success'if r['expected_ok']else'expected_failure']+=1
    # Only solver accepted-state output is constrained even on expected failure.
    check_output=r['expected_ok']or r.get('solver',False)
    valid_output=True
    if check_output:
     expectation=r['expectation']
     if expectation=='spectral':targets,ders,gap,case=self.spectral_target(r)
     elif expectation=='constant':targets=list(map(D,r['constant']));ders=[[D(0)]*len(targets)for _ in range(38)];gap=case=None
     elif expectation=='identity':targets=[df(float.fromhex(v))for v in r['values']];ders=[[df(float.fromhex(v))for v in h]for h in r['seeds']];gap=case=None
     else:targets=[];ders=[];gap=case=None
     if len(o['output'])!=len(targets):fail(rid,'output-size',{'expected':len(targets),'observed':len(o['output'])});valid_output=False
     for item in o['output']:
      keys={'value','derivatives'}if r['kind']=='jet'else{'value'}
      if not isinstance(item,dict)or set(item)!=keys:fail(rid,'component-shape');valid_output=False;continue
      if not number(item['value']):fail(rid,'nonfinite-or-invalid-output');valid_output=False
      if r['kind']=='jet'and(not isinstance(item['derivatives'],list)or len(item['derivatives'])!=38 or not all(number(x)for x in item['derivatives'])):fail(rid,'full38-finite-derivatives-required');valid_output=False
     if valid_output and expectation=='spectral':
      n=norm([df(float.fromhex(x))for x in r['values']]);op=r['operation'];isP=op.startswith('projector_');observed=[df(v['value'])for v in o['output']]
      primal_error=norm([x-y for x,y in zip(observed,targets)])if isP else abs(observed[0]-targets[0]);bound=2048*eps*n/gap+tiny if isP else 512*eps*n+tiny
      accuracy(primal_error,bound,r,'primal')
      if not isP and op not in('upper_sum','lower_sum')and(case['reference']['method'].startswith('diagonal')or case['reference']['method']=='zero'):
       counts['exact_diagonal_checks']+=1
       if o['output'][0]['value']!=float(targets[0]):fail(rid,'exact-diagonal-value')
      if r['kind']=='jet':
       for j in range(38):
        observed=[df(v['derivatives'][j])for v in o['output']];counts['derivative_columns_checked']+=1
        if op.endswith('_value'):
         if any(v!=0 for v in observed):fail(rid,'value-only-transport-column'+str(j))
         counts['value_only_transport_columns']+=1;continue
        h=norm([df(float.fromhex(x))for x in r['seeds'][j]])
        error=norm([x-y for x,y in zip(observed,ders[j])])if isP else abs(observed[0]-ders[j][0]);bound=8192*eps*(h/gap)*(1+n/gap)+tiny if isP else 2048*eps*h*(1+n/gap)+tiny
        accuracy(error,bound,r,'derivative-column'+str(j))
     elif valid_output:
      for k,(item,target)in enumerate(zip(o['output'],targets)):
       counts['exact_context_value_checks']+=1
       if item['value']!=float(target):fail(rid,'exact-context-value-'+str(k))
       if r['kind']=='jet':
        for j in range(38):
         counts['exact_context_derivative_checks']+=1
         if item['derivatives'][j]!=float(ders[j][k]):fail(rid,'exact-context-derivative-'+str(k)+'-'+str(j))
    if r.get('history'):
     h=o['history'];expected_meta={'generation':8 if r['expected_ok']else 7,'epoch':3,'events':[0,1]if r['expected_ok']else[],'failed':-1 if r['expected_ok']else 1,'executed':2}
     if not isinstance(h,dict)or set(h)!={'values',*expected_meta}:fail(rid,'history-shape');continue
     for key,want in expected_meta.items():
      got=h[key];typed=(isinstance(got,list)and all(type(v)is int for v in got))if key=='events'else type(got)is int
      if not typed or got!=want:fail(rid,'history-'+key)
     if not isinstance(h['values'],list)or len(h['values'])!=7 or not all(number(v)for v in h['values']):fail(rid,'history-values-shape')
     elif r['expected_ok']:
      if not valid_output or len(o['output'])!=6 or h['values']!=[18.,*[v['value']for v in o['output']]]:fail(rid,'history-success-full-snapshot')
     elif h['values']!=[17.,11.,12.,13.,0.,0.,0.]:fail(rid,'history-failure-rollback')
     counts['history_transactions']+=1
    if r.get('solver'):
     s=o['solver'];keys={'tentative_reset_observed','rejected','message','recovery_matches_fresh','recovery_ok','recovery_state','fresh_state'}
     if not isinstance(s,dict)or set(s)!=keys:fail(rid,'solver-shape');continue
     for key in ('recovery_state','fresh_state'):
      got=s[key]
      if not isinstance(got,list)or len(got)!=8 or not all(number(x)for x in got)or got!=[7.,2.,-3.,0.,0.,0.,.7,1.]:fail(rid,'solver-'+key)
     for key in ('tentative_reset_observed','recovery_matches_fresh','recovery_ok'):
      if s[key]is not True:fail(rid,'solver-'+key)
     if type(s['rejected'])is not int or(type(s['message'])is not str):fail(rid,'solver-diagnostic-shape')
     elif r['expected_ok']:
      if s['rejected']!=0 or s['message']!='':fail(rid,'solver-unexpected-rejection')
     elif s['rejected']<1 or not s['message'].startswith('integration failed'):fail(rid,'solver-missing-rejection')
     counts['solver_transactions']+=1
  return {'identity':'spectral-generated-context-independent-assessor-v1','requests':len(self.requests),'observed_rows':len(rows),'counts':dict(counts),'failures':failures,'worst_error_fraction':worst,'passed':not failures,'compiled_execution_by_assessor':False,'scientific_admission':False}

def ideal_rows(study):
 """Synthetic ideal frame from independent reference only, never candidate output."""
 rows=[]
 with localcontext()as ctx:
  ctx.prec=500
  for r in study.requests:
   o={'id':r['id'],'slot':r['slot'],'kind':r['kind'],'ok':r['expected_ok'],'input_unchanged':True,'output':[]}
   if r['expected_ok']or r.get('solver'):
    if r['expectation']=='spectral':v,ds,_,_=study.spectral_target(r)
    elif r['expectation']=='constant':v=list(map(D,r['constant']));ds=[[D(0)]*len(v)for _ in range(38)]
    elif r['expectation']=='identity':v=[df(float.fromhex(x))for x in r['values']];ds=[[df(float.fromhex(x))for x in seed]for seed in r['seeds']]
    else:v=[];ds=[]
    for i,x in enumerate(v):
     item={'value':float(x)}
     if r['kind']=='jet':item['derivatives']=[float(ds[j][i])for j in range(38)]
     o['output'].append(item)
   if r.get('history'):
    o['history']={'values':[18.,*[x['value']for x in o['output']]]if r['expected_ok']else[17.,11.,12.,13.,0.,0.,0.],'generation':8 if r['expected_ok']else 7,'epoch':3,'events':[0,1]if r['expected_ok']else[],'failed':-1 if r['expected_ok']else 1,'executed':2}
   if r.get('solver'):o['solver']={'tentative_reset_observed':True,'rejected':0 if r['expected_ok']else 1,'message':''if r['expected_ok']else'integration failed: synthetic expected rejection','recovery_matches_fresh':True,'recovery_ok':True,'recovery_state':[7.,2.,-3.,0.,0.,0.,.7,1.],'fresh_state':[7.,2.,-3.,0.,0.,0.,.7,1.]}
   rows.append(o)
 return rows
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('root');parser.add_argument('rows');a=parser.parse_args();raw=Path(a.rows).read_bytes();rows=json.loads(raw)if raw.lstrip().startswith(b'[')else[json.loads(x)for x in raw.splitlines()if x.strip()];result=Study(a.root).assess(rows);print(json.dumps(result,indent=2,sort_keys=True));raise SystemExit(0 if result['passed']else 1)
