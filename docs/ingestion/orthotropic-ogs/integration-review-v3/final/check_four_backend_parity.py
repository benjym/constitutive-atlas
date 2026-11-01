"""Independent pairwise saved final-run backend audit; no compiled execution."""
from pathlib import Path
import json,sys,itertools,hashlib
ROOT=Path(__file__).resolve().parents[5]
refs=json.loads((ROOT/'docs/ingestion/orthotropic-ogs/execution-v1/references.json').read_text())['cases'];assert len(sys.argv)==5,'Supply exactly four distinct final-run backend/OS raw files'
paths=list(map(Path,sys.argv[1:]));assert len(set(p.resolve() for p in paths))==4
raw=[json.loads(p.read_text()) for p in paths]
for rows in raw:assert len(rows)==len(refs)==121
pairs=[]
for i,j in itertools.combinations(range(4),2):
 scalars=tangents=0;maxerr=0.
 for c,a,b in zip(refs,raw[i],raw[j]):
  assert a['id']==b['id']==c['id'];a,b=a['response'],b['response'];assert a['ok']==b['ok']==c['ok']
  if not c['ok']:continue
  assert a['model']==b['model']=='orthotropic-linear-elastic-ogs' and a['parameters']==b['parameters']==c['parameters'] and a['strain']==b['strain']==c['strain']
  assert a['catalogue_hash']==b['catalogue_hash']=='5f394a724f409f9e1cbdea9f7ff536bd1566550eb7071c39987c1cb03f528abc'
  assert a['diagnostics']['increment_fractions']==b['diagnostics']['increment_fractions']==[1]
  assert len(a['state'])==len(b['state'])==6;scale=max(c['parameters'][:6])
  for x,y in zip(a['state'],b['state']):
   e=abs(x-y);assert e<=5e-10+2e-11*scale;maxerr=max(maxerr,e);scalars+=1
  if c['mode']=='linearize':
   for ar,br in zip(a['state_tangent'],b['state_tangent']):
    for x,y in zip(ar,br):assert abs(x-y)<=1e-7+2e-10*scale;tangents+=1
 assert scalars==648 and tangents==144
 pairs.append({'a':str(paths[i]),'b':str(paths[j]),'state_pairs':scalars,'tangent_pairs':tangents,'max_absolute_stress_difference_Pa':maxerr})
print(json.dumps({'passed':True,'backend_OS_sets':4,'pairwise_comparisons':pairs,'state_pairs_total':sum(p['state_pairs'] for p in pairs),'tangent_pairs_total':sum(p['tangent_pairs'] for p in pairs),'raw_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'gate':'Original frozen source-reference state/tangent budgets; pairwise agreement supplements independent Decimal source checks, never replaces them'},indent=2))
