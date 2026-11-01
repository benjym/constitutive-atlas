"""Synthetic oracle observations and deliberate corruptions; never compiled evidence."""
from pathlib import Path
import json,struct,copy,subprocess,sys,math,hashlib
p=Path(__file__).parent;out=p/'assessor-controls';assert not out.exists();out.mkdir()
cs=json.loads((p/'requests.json').read_text())['cases'];rs=json.loads((p/'references.json').read_text())['rows']
def enc(r):
 if 'rounded_bits' not in r:return copy.deepcopy(r)
 v=struct.unpack('>d',bytes.fromhex(r['rounded_bits']))[0]
 return dict(classification=r['classification'],signbit=r['signbit'],**({'value':v} if math.isfinite(v) else {}))
rows=[]
for c,r in zip(cs,rs):
 v={'value':enc(r['references'][0] if 'references' in r else r['expected'])}
 if c['kind']==2:
  ds=[]
  for k in range(38):
   active=(k==0 and c['seeds']&1) or (k==1 and c['seeds']&2)
   ds.append(enc(r['references'][k+1] if 'references' in r else r['expected_derivatives'][k]) if active else dict(classification='finite',signbit=False,value=0.))
  v['derivatives']=ds
 rows.append(dict(id=c['id'],response=v))
base=dict(backend='synthetic-oracle-assessor-control-only',rows=rows)
def get(d,id):return next(r['response'] for r in d['rows'] if r['id']==id)
finite=next(c['id'] for c,r in zip(cs,rs) if c['kind']==0 and 'references' in r and r['references'][0]['classification']=='finite' and 0<abs(enc(r['references'][0])['value'])<1e100)
jet=next(c['id'] for c,r in zip(cs,rs) if c['kind']==2 and c['seeds']&1 and 'references' in r and abs(enc(r['references'][1])['value'])>1e-100)
cases=[('baseline',None),('wrong-zero-sign',lambda d:get(d,'jet-negative-zero-linear')['value'].update(signbit=False)),('wrong-infinity-class',lambda d:get(d,'jet-finite-overflow-inactive')['value'].update(classification='nan')),('wrong-nan-class',lambda d:get(d,'jet-negative-zero-cube')['derivatives'][1].update(classification='infinity',signbit=False)),('active-derivative-error',lambda d:get(d,jet)['derivatives'][0].update(value=1e300)),('inactive-lane37-error',lambda d:get(d,'jet-finite-overflow-inactive')['derivatives'][37].update(value=1.)),('scalar-beyond-one-ulp',lambda d:get(d,finite)['value'].update(value=math.nextafter(math.nextafter(math.nextafter(get(d,finite)['value']['value'],math.inf),math.inf),math.inf)))]
summary=[]
for name,mutate in cases:
 d=copy.deepcopy(base)
 if mutate:mutate(d)
 raw=out/(name+'.json');report=out/(name+'-assessment.json');raw.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
 run=subprocess.run([sys.executable,str(p/'assess.py'),str(raw),str(report)],capture_output=True,text=True)
 (out/(name+'.log')).write_text(run.stdout+run.stderr)
 r=json.loads(report.read_text());assert run.returncode==(0 if name=='baseline' else 1),(name,run.returncode);assert r['status']==('passed' if name=='baseline' else 'failed')
 summary.append(dict(name=name,status=r['status'],failures=len(r['failures'])))
(out/'summary.json').write_text(json.dumps(dict(scope='Assessor controls only, no compiled observations',controls=summary),indent=2)+'\n');print(json.dumps(summary))
