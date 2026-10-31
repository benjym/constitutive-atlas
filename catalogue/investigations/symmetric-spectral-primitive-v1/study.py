"""Frozen request assembly and independent primitive assessment, no Atlas imports."""
from pathlib import Path
import json,math,sys,subprocess,hashlib,gzip
from decimal import Decimal,localcontext
P=Path(__file__).resolve().parent
OPS=('max_value','mid_value','min_value','max','mid','min','upper_sum','lower_sum','projector_max','projector_min')
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix==".gz" else p.read_bytes())
def decfloat(x):return Decimal.from_float(x)
def norm(v):return sum(x*x for x in v).sqrt()
def cart_to_mandel(a):
 r=Decimal(2).sqrt();return [Decimal(a[0][0]),Decimal(a[1][1]),Decimal(a[2][2]),r*Decimal(a[0][1]),r*Decimal(a[1][2]),r*Decimal(a[0][2])]
def scalar_reference(case,op):
 ref=case['reference'];index={'max_value':0,'max':0,'mid_value':1,'mid':1,'min_value':2,'min':2}
 if op in ('upper_sum','lower_sum'):return Decimal(ref['pair_sums']['upper' if op=='upper_sum' else 'lower']['value'])
 return Decimal(ref['eigenvalues'][index[op]])
def selector(op):return 'min' if op in ('min','projector_min','upper_sum') else 'mid' if op=='mid' else 'max'
def expected(case,op,kind,seeds):
 ref=case['reference'];e=list(map(Decimal,ref['eigenvalues']));a=list(map(lambda s:decfloat(float.fromhex(s)),case['input']['mandel_hex']));n=norm(a)
 eps=Decimal(2)**-52;maximum=decfloat(sys.float_info.max)
 if op.endswith('_value'):gap=None
 else:
  i={'max':0,'mid':1,'min':2}[selector(op)];gap=min(abs(e[i]-e[j])for j in range(3)if i!=j)
  if gap<=1024*eps*n:return 'selected_eigenvalue_unresolved'
 if op.startswith('projector_'):
  if kind=='jet':
   selected=ref['selected'][selector(op)]
   for direction in selected['directions']:
    if any(not math.isfinite(float(v)) for v in cart_to_mandel(direction['projector'])):return 'derivative_range'
 else:
  if not math.isfinite(float(scalar_reference(case,op))):return 'output_range'
  if kind=='jet' and not op.endswith('_value'):
   if op in ('upper_sum','lower_sum'):ds=ref['pair_sums']['upper' if op=='upper_sum' else 'lower']['directions']
   else:ds=[d['eigenvalue']for d in ref['selected'][selector(op)]['directions']]
   if any(not math.isfinite(float(Decimal(v))) for v in ds):return 'derivative_range'
 return 'ok'
def assemble():
 reference=load(P/'reference/reference-p360.json.gz');requests=[]
 with localcontext()as ctx:
  ctx.prec=500
  for case in reference['cases']:
   for op in OPS:
    for kind in ('double','jet'):
     requests.append({'id':case['input']['id']+'-'+op+'-'+kind,'case':case['input']['id'],'operation':op,'kind':kind,'values':case['input']['mandel_hex'],'seeds':reference['seeds_mandel_hex'],'expected_status':expected(case,op,kind,reference['seeds_mandel_hex'])})
 base=next(c for c in reference['cases']if c['input']['id']=='distinct')
 # Each invalid call is immediately followed by the same valid operation/history.
 for op in ('max_value','projector_max'):
  for k in range(6):
   r={'id':f'nonfinite-primal-{op}-{k}','operation':op,'kind':'jet','values':list(base['input']['mandel_hex']),'seeds':reference['seeds_mandel_hex'],'expected_status':'nonfinite_input'}
   r['values'][k]='nan' if k%2==0 else 'inf';requests.append(r)
   requests.append({'id':r['id']+'-recovery','case':'distinct','operation':op,'kind':'jet','values':base['input']['mandel_hex'],'seeds':reference['seeds_mandel_hex'],'expected_status':'ok'})
  for j in range(38):
   seeds=[list(x)for x in reference['seeds_mandel_hex']];seeds[j][j%6]='nan' if j%2==0 else 'inf'
   r={'id':f'nonfinite-seed-{op}-{j}','operation':op,'kind':'jet','values':base['input']['mandel_hex'],'seeds':seeds,'expected_status':'nonfinite_input'};requests.append(r)
   requests.append({'id':r['id']+'-recovery','case':'distinct','operation':op,'kind':'jet','values':base['input']['mandel_hex'],'seeds':reference['seeds_mandel_hex'],'expected_status':'ok'})
 return requests

def assess(rows):
 requests=load(P/'requests.json.gz');reference=load(P/'reference/reference-p360.json.gz');cases={c['input']['id']:c for c in reference['cases']};policy=load(P/'policy.json')
 failures=[];counts={'successful':0,'expected_failures':0,'accuracy_checks':0,'exact_diagonal_checks':0};worst={'ratio':'0','request':None,'channel':None}
 assert len(rows)==len(requests),(len(rows),len(requests))
 with localcontext()as ctx:
  ctx.prec=500;eps=Decimal(2)**-52;tiny=Decimal(2)**-1074*policy['subnormal_absolute_allowance_ulps']
  def check(error,bound,request,channel):
   counts['accuracy_checks']+=1;ratio=error/bound if bound else Decimal(0)if error==0 else Decimal('Infinity')
   if ratio>Decimal(worst['ratio']):worst.update(ratio=str(ratio),request=request,channel=channel)
   if error>bound:failures.append({'request':request,'channel':channel,'error':str(error),'bound':str(bound)})
  for r,o in zip(requests,rows):
   assert (r['id'],r['operation'],r['kind'])==(o['id'],o['operation'],o['kind'])
   if o['status']!=r['expected_status'] or o['ok']!=(r['expected_status']=='ok'):
    failures.append({'request':r['id'],'expected_status':r['expected_status'],'observed_status':o['status']});continue
   if not o['ok']:
    counts['expected_failures']+=1
    if not o['failed_output_preserved']:failures.append({'request':r['id'],'channel':'failed-output-preservation'})
    continue
   counts['successful']+=1;case=cases[r['case']];ref=case['reference'];n=norm([decfloat(float.fromhex(x))for x in r['values']]);op=r['operation'];e=list(map(Decimal,ref['eigenvalues']));name=selector(op)
   gap=min(abs(e[{'max':0,'mid':1,'min':2}[name]]-e[j])for j in range(3)if j!={'max':0,'mid':1,'min':2}[name])if not op.endswith('_value')else None
   out=o['output'];is_projector=op.startswith('projector_')
   if is_projector:
    target=cart_to_mandel(ref['selected'][name]['projector']);error=norm([decfloat(x['value'])-v for x,v in zip(out,target)]);bound=policy['projector_absolute_error_eps_factor']*eps*n/gap+tiny
   else:
    target=scalar_reference(case,op);error=abs(decfloat(out[0]['value'])-target);bound=policy['value_absolute_error_eps_factor']*eps*n+tiny
    if (case['reference']['method'].startswith('diagonal') or case['reference']['method']=='zero') and op not in ('upper_sum','lower_sum'):
     counts['exact_diagonal_checks']+=1
     if out[0]['value']!=float(target):failures.append({'request':r['id'],'channel':'exact-diagonal-value'})
   check(error,bound,r['id'],'primal')
   if r['kind']=='jet':
    for column,seed in enumerate(r['seeds']):
     h=norm([decfloat(float.fromhex(x))for x in seed])
     if op.endswith('_value'):
      if any(x['derivatives'][column]!=0 for x in out):failures.append({'request':r['id'],'channel':f'value-only-storage-{column}'})
      continue
     if is_projector:
      target=cart_to_mandel(ref['selected'][name]['directions'][column]['projector']);error=norm([decfloat(x['derivatives'][column])-v for x,v in zip(out,target)]);bound=policy['projector_derivative_absolute_error_eps_factor']*eps*(h/gap)*(1+n/gap)+tiny
     else:
      if op in ('upper_sum','lower_sum'):target=Decimal(ref['pair_sums']['upper'if op=='upper_sum'else'lower']['directions'][column])
      else:target=Decimal(ref['selected'][name]['directions'][column]['eigenvalue'])
      error=abs(decfloat(out[0]['derivatives'][column])-target);bound=policy['scalar_derivative_absolute_error_eps_factor']*eps*h*(1+n/gap)+tiny
     check(error,bound,r['id'],f'derivative-{column}')
 return {'requests':len(requests),**counts,'failures':failures,'worst_error_fraction':worst,'passed':not failures,'scientific_admission':False,'production_DSL_integrated':False}

def payload(requests):return ''.join(' '.join([r['id'],r['operation'],r['kind'],*r['values'],*(x for row in r['seeds']for x in row)])+'\n'for r in requests)
if __name__=='__main__':
 if sys.argv[1]=='assemble':(P/'requests.json.gz').write_bytes(gzip.compress((json.dumps(assemble(),separators=(',',':'))+'\n').encode(),mtime=0))
 elif sys.argv[1]=='assess':print(json.dumps(assess([json.loads(s)for s in Path(sys.argv[2]).read_text().splitlines()]),indent=2,sort_keys=True))
 else:raise SystemExit('assemble or assess')
