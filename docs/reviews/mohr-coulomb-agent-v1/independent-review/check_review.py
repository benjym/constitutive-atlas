"""Read-only/source-only independent scientific-review integrity and algebra checks."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,tarfile,subprocess,sys
ROOT=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
checks={}
freeze=load(ROOT/'docs/reviews/mohr-coulomb-agent-v1/inputs.json')
checks['input_freeze']={p:sha(ROOT/p)==v for p,v in freeze['files'].items()}
assert all(checks['input_freeze'].values())
m=load(ROOT/'models/mohr-coulomb.json');c=load(ROOT/'docs/reviews/mc-current-collector-freeze-v3/catalogue.json')
checks['exact_model_sha256']=sha(ROOT/'models/mohr-coulomb.json')
assert sha(ROOT/'docs/reviews/mc-current-collector-freeze-v3/models/mohr-coulomb.json')==checks['exact_model_sha256']
assert next(x for x in c['models']if x['id']=='mohr-coulomb')==m
checks['raw_backend_descriptor_equal_current']={}
for role in ('native','wasm'):
 with tarfile.open(ROOT/f'docs/reviews/mc-{role}-qualification-v3/observations.tar.gz')as t:
  rows=json.load(t.extractfile('observations/journal.json'))
  d=json.loads(next(x for x in rows if x['id']=='describe')['raw'])
  assert d==c;checks['raw_backend_descriptor_equal_current'][role]=True
old=load(ROOT/'catalogue/investigations/mc-stored-backends-v1/frozen/models/research/mohr-coulomb-sysala-cermak-h0-gap-classifier-v2.json')
checks['historical_research_differences'] = sorted(k for k in old.keys()|m.keys()if old.get(k)!=m.get(k))
assert set(checks['historical_research_differences'])=={'id','name','status','description','state'}
a,b=old['state'][0].copy(),m['state'][0].copy();checks['historical_initial_examples']=[a.pop('initial'),b.pop('initial')];assert a==b
# Independently expand source denominators and verify the gap apex identity,
# without importing the model DSL, candidate or existing return/reference programs.
n=0
for K in (F(1,10),F(1),F(13)):
 for G in (F(1,3),F(2),F(20)):
  for s in (F(1,100),F(3,5),F(99,100)):
   for d in (F(1,100),F(1,3),F(99,100)):
    A=2*(K-2*G/3)*d
    ds=2*A*s+4*G*(1+d*s);dl=2*A*s+G*(1+d)*(1+s)+2*G*(1-d)*(1-s);dr=2*A*s+2*G*(1+d)*(1+s)+G*(1-d)*(1-s)
    assert ds==4*K*d*s+4*G*(1+d*s/3)>0
    assert dl==4*K*d*s+G*(3-s-d+d*s/3)>0
    assert dr==4*K*d*s+G*(3+s+d+d*s/3)>0
    for t in ((F(10),F(3),F(-4)),(F(5),)*3,(F(10**20+2),F(10**20+1),F(10**20))):
     x,y=t[0]-t[1],t[1]-t[2];h=F(7);ft=(1+s)*t[0]-(1-s)*t[2]-h
     assert ft-(1+s/3)*x-(1-s/3)*y==F(2,3)*s*sum(t)-h
     a=x/(2*G*(1+d));b=y/(2*G*(1-d));L=(x+2*y)/(2*G*(3-d));R=(2*x+y)/(2*G*(3+d))
     assert L-R==3*(1-d*d)*(b-a)/(9-d*d)
     n+=1
checks['independent_fraction_coefficient_gap_cases']=n
receipt=load(ROOT/'docs/ingestion/mohr-coulomb/retention-v1/private-retention.json')
checks['durable_private_pdf_hash']=sha(Path(receipt['durable_private_path']))
assert checks['durable_private_pdf_hash']==receipt['sha256']=='bf35ee09d500b8e21aabdddbdfac363c5f68368f150890c60343bc62447c83ca'
checks['private_pdf_bytes']=Path(receipt['durable_private_path']).stat().st_size
checks['candidate_calls']=checks['compiled_calls']=0
checks['passed']=True
print(json.dumps(checks,indent=2,sort_keys=True))
