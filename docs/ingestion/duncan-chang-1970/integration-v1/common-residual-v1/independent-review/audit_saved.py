"""Independent saved-only probe/oracle/coverage audit; no compiled imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,hashlib,math,struct,re
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(x):return struct.pack('>d',float(x))
probes=[]
for sub,number in [('',224),('modulus-v2',24),('power-v3',36)]:
 b=B/sub;freeze=read(b/'freeze.json')
 for path,h in freeze['files'].items():assert sha(ROOT/path)==h,path
 req=read(b/'requests.json')['cases'];out=read(b/'results.json')['results'];summary=read(b/'summary.json')
 assert len(req)==len(out)==summary['cases']==number
 stats={}
 for backend in ['baseline','no_contraction']:
  differences=[];domains=[]
  for c,row in zip(req,out):
   assert c['id']==row['id']
   for name in ['baseline','no_contraction','wasm']:assert json.loads(row[name]['raw'])==row[name]['response']
   n=row[backend]['response'];w=row['wasm']['response']
   if n['ok']!=w['ok']:domains.append(row['id'])
   elif n['ok']:
    assert len(n['values'])==len(w['values'])==7
    for i,(x,y) in enumerate(zip(n['values'],w['values'])):
     if x!=y:differences.append(dict(id=row['id'],component=i,native=x,wasm=y,difference=x-y))
  assert dict(domain_disagreements=domains,component_differences=differences)==summary['summaries'][backend]
  stats[backend]=dict(domain_disagreements=len(domains),numeric_component_differences=len(differences))
 probes.append(dict(study=sub or 'common-full-residual',cases=number,stats=stats))
power=B/'power-v3';req=read(power/'requests.json')['cases'];out=read(power/'results.json')['results'];saved=read(power/'precision-results.json')['rows'];oracle=[]
for freeze in ['precision-freeze.json']:
 for path,h in read(power/freeze)['files'].items():assert sha(ROOT/path)==h,path
for c,row,expected in zip(req,out,saved):
 assert c['id']==row['id']==expected['id'];p=c['parameters'];z=c['current']
 assert c['current']==c['previous'] and z[0]<z[1]<z[2] and z[3:6]==[0,0,0]
 assert z[6]>z[2]-z[0] and p[8]==0 and p[2]==p[3] and p[2]*p[1]==1 and c['strain']==[0,0,0,1,0,0]
 x=z[0]/p[1];n=p[4];vals=[]
 for backend in ['baseline','no_contraction','wasm']:
  values=row[backend]['response']['values'];assert row[backend]['response']['ok'] and all(v==0 for i,v in enumerate(values) if i!=3)
  if n in [0,1]:assert values[3]==(-1 if n==0 else -x)
 for prec in [100,160]:
  with localcontext() as ctx:
   ctx.prec=prec;xx=D.from_float(x);nn=D.from_float(n);ref=xx**nn;term=D(1);series=D(1);t=xx-1;assert abs(t)<D('.1')
   for k in range(200):term*=((nn-k)/(k+1))*t;series+=term
   assert abs(ref-series)<D(10)**(-prec+4)
   vals.append(ref)
 assert float(vals[0])==float(vals[1])==expected['rounded_reference']
 assert str(vals[1])==expected['reference_160']
 with localcontext() as ctx:
  ctx.prec=160;ulp=D.from_float(math.ulp(float(vals[1])))
  errors={backend:str((D.from_float(-row[backend]['response']['values'][3])-vals[1])/ulp) for backend in ['baseline','no_contraction','wasm']}
 assert errors==expected['backend_error_ulps']
 oracle.append(dict(id=c['id'],rounded_reference=float(vals[1]),independent_binomial_series_agrees=True,backend_error_ulps=errors))
coverage=B/'case-coverage-v1';freeze=read(coverage/'freeze.json')
for path,h in freeze['files'].items():assert sha(ROOT/path)==h,path
original=(ROOT/'tools/test_browser_loading.mjs').read_text();collector=(coverage/'collect.mjs').read_text()
def comparison(s):return s[s.index('function compare('):s.index('\nfunction check(')]
assert comparison(original)==comparison(collector)
assert hashlib.sha256((comparison(collector)+'\n').encode()).hexdigest()==freeze['comparison_function_sha256']
# Strip precisely the intentional continuation/final reporting and import-path edits.
normalized=collector.replace(str(ROOT)+'/tools/','./').replace(str(ROOT)+'/web/','../web/').replace("try{compare(row.native,row.wasm,tol);row.comparison_passed=true;}catch(error){row.comparison_passed=false;row.comparison_failure=String(error.message);}writeFileSync(outfile,JSON.stringify(report)+'\\n');return row;","compare(row.native,row.wasm,tol);return row;")
normalized=normalized.replace("report.status=report.pairs.some(r=>r.comparison_passed===false)?'failed':'passed';","report.status='passed';")
normalized=normalized[:normalized.index("\nif(report.status==='failed')")]
normalized=normalized.replace('failed-prefix recovery completed; see status and per-pair comparisons.','failed-prefix recovery passed.')
assert normalized.rstrip()==original.rstrip()
saved=read(coverage/'results.json');assert saved['status']=='failed' and len(saved['pairs'])==156 and saved['backend_runs']==312 and saved['same_instance_wasm_export_import_replays']==130
def difference(a,b,tol,path='result'):
 if isinstance(b,(int,float)) and not isinstance(b,bool):
  assert isinstance(a,(int,float)) and math.isfinite(a) and math.isfinite(b)
  return None if abs(a-b)<=tol*max(1,abs(a),abs(b)) else (path,a,b)
 if isinstance(b,list):
  assert isinstance(a,list) and len(a)==len(b)
  for i,(x,y) in enumerate(zip(a,b)):
   d=difference(x,y,tol,path+f'[{i}]')
   if d:return d
 elif isinstance(b,dict):
  assert a.keys()==b.keys()
  for k in b:
   if k=='elapsed_ms':continue
   d=difference(a[k],b[k],tol,path+'.'+k)
   if d:return d
 else:assert a==b,path
 return None
for row in saved['pairs']:
 if row.get('expected_contract_rejection'):
  assert row['native']==row['wasm'] and not row['native']['ok']
 else:
  tol=1e-7 if row['name'].startswith('legacy/') else 1e-10
  d=difference(row['native'],row['wasm'],tol)
  assert row['comparison_passed']==(d is None),row['name']
  if d:assert row['comparison_failure'].startswith(d[0]+': '),row['name']
failures=[dict(name=row['name'],failure=row['comparison_failure']) for row in saved['pairs'] if row.get('comparison_passed') is False]
assert len(failures)==6 and all('/duncan-chang-1970-endpoint-average' in row['name'] for row in failures)
print(json.dumps({'identity':'independent-common-residual-power-coverage-v1','bounded_audit_pass':True,'probes':probes,'power_reference_rows':len(oracle),'independent_binomial_series_and_decimal100_160_roundings_agree':True,'power_oracle_rows':oracle,'original_compare_function_unchanged':True,'coverage_pairs':156,'coverage_runs':312,'same_instance_wasm_export_import_replays':130,'coverage_status':'failed','coverage_failures':failures,'causal_newton_claim':False,'production_remedy_approved':False,'e6_e7_accepted':False,'compiled_calls':0},indent=2))
