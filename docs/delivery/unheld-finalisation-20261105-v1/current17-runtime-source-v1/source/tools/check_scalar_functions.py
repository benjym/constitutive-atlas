from pathlib import Path
from decimal import Decimal,localcontext
import struct,json,sys,math,hashlib
p=Path(__file__).resolve().parents[1]/'tests/fixtures/scalar-functions';output=Path(sys.argv[2]);assert not output.exists();raw=json.load(open(sys.argv[1]));requests=json.loads((p/'requests.json').read_text())['cases'];references=json.loads((p/'references.json').read_text())['rows'];assert len(raw['rows'])==len(requests)==len(references)==391
checks=[]
def record(id,check,passed,**kw):checks.append(dict(id=id,check=check,passed=passed,**kw))
def expected(id,x,e,label):
 ok=x['classification']==e['classification'];record(id,label+'/classification',ok)
 if not ok:return
 if e.get('signbit') is not None:record(id,label+'/signbit',x['signbit']==e['signbit'])
 if e['classification']=='finite':record(id,label+'/value',x['value']==e['value'])
def reference(id,x,r,label,derivative=False):
 ok=x['classification']==r['classification'];record(id,label+'/classification',ok)
 if not ok:return
 if not derivative:record(id,label+'/signbit',x['signbit']==r['signbit'])
 if r['classification']!='finite':return
 v=x['value'];rounded=struct.unpack('>d',bytes.fromhex(r['rounded_bits']))[0]
 with localcontext() as ctx:
  ctx.prec=180;ref=Decimal(r['decimal']);error=abs(Decimal.from_float(v)-ref)
  budget=Decimal('2e-300')+Decimal('2e-14')*abs(ref) if derivative else Decimal.from_float(math.ulp(rounded))
  record(id,label+'/accuracy',error<=budget,absolute_error=str(error),budget=str(budget))
for c,r,o in zip(requests,references,raw['rows']):
 assert c['id']==r['id']==o['id'];id=c['id'];v=o['response'];assert 'error' not in v
 if 'references' in r:reference(id,v['value'],r['references'][0],'value')
 else:expected(id,v['value'],r['expected'],'value')
 if c['kind']==2:
  ds=v['derivatives'];assert len(ds)==38
  for k,d in enumerate(ds):
   active=k==0 and c['seeds']&1 or k==1 and c['seeds']&2
   if not active:expected(id,d,dict(classification='finite',signbit=False,value=0.),f'd{k}/inactive')
   elif 'references' in r:reference(id,d,r['references'][k+1],f'd{k}',True)
   else:expected(id,d,r['expected_derivatives'][k],f'd{k}')
report=dict(status='passed' if all(c['passed'] for c in checks) else 'failed',backend=raw['backend'],cases=len(requests),checks=len(checks),failures=[c for c in checks if not c['passed']],bindings={str(p/'requests.json'):hashlib.sha256((p/'requests.json').read_bytes()).hexdigest(),str(p/'references.json'):hashlib.sha256((p/'references.json').read_bytes()).hexdigest(),str(Path(sys.argv[1])):hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()});output.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['cases'],report['checks'],len(report['failures']));sys.exit(0 if report['status']=='passed' else 1)
