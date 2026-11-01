"""Independent saved-evidence assessor. Never invokes a compiled artifact."""
import hashlib,json,math,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent; D=Path('/private/tmp/atlas-barodesysand-delivery-v1/docs/ingestion/barodesy-sand/delivery-v1'); ROOT=Path('/private/tmp/atlas-barodesysand-delivery-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strict(s):
 def pairs(items):
  d={}
  for k,v in items:
   assert k not in d,'duplicate JSON key';d[k]=v
  return d
 return json.loads(s,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def read(p):return strict(p.read_text())
def finite(v,n):assert len(v)==n and all(type(x) in (int,float) and math.isfinite(x) for x in v)
def bits(v):return [struct.pack('>d',x).hex() for x in v]
def audit():
 freeze=read(D/'prospective-freeze.json'); src=Path(freeze['source_root_private'])
 for p,h in freeze['source_inputs'].items():
  if p!='atlas/measurement_units.py':assert sha(src/p)==h,p
  else:assert sha(src/p)=='9e3dd3c586c46206a783a972f29b8ae2d959865ef7d14a5dfab45a9e6e18a132'
 for p,h in freeze['prospective_inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in read(D/'transport-freeze.json')['files'].items():assert sha(D/p)==h,p
 assert sha(ROOT/'models/barodesy-sand.json')=='3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239'
 policy=read(D/'policy.json'); limits=policy['budgets']; settings=policy['settings']
 old=read(ROOT/'catalogue/investigations/barodesy2015-rates-v2/protocol.json')['cases']
 refs=read(D/'references.json'); oblique=read(D/'oblique-reference.json'); journals={}; outputs={}; summaries={}
 for backend in ('native','wasm'):
  rows=read(D/f'release-v3/{backend}-results/journal.json'); assert len(rows)==668
  by={r['id']:r for r in rows}; assert len(by)==len(rows)
  out={k:strict(v['raw']) for k,v in by.items()};journals[backend]=rows;outputs[backend]=out
  embedded=out['describe']['models'];assert next(x for x in embedded if x['id']=='barodesy-sand')==read(ROOT/'models/barodesy-sand.json')
  for c in old:
   row=by['rate/'+c['id']];q=row['request'];args=c['args'];assert q['model']=='barodesy-sand' and [q['parameters'],q['initial'],q['strain']]==args[1:]
   a=out[row['id']];e=c['expectation'];assert a['ok'] is e['ok']
   if e['ok']:
    finite(a['values'],7);assert all(abs(x-y)<=b for x,y,b in zip(a['values'],e['values'],e['absolute_budgets']))
  maxima={v:[0.,0.,0.] for v in ('default','tight')}; count=0; restarts=0
  for name,ref in refs.items():
   c=ref['case']
   for variant in maxima:
    row=by[name+'/'+variant];q=row['request'];a=out[row['id']]
    assert q['settings']==settings[variant] and all(q[k]==c[k] for k in ('protocol','target','steps','cycles'))
    assert a['ok'] is True and len(a['points'])==len(ref['points'])
    for point,z in zip(a['points'],ref['points']):
     finite(point['state'],7);finite(point['strain'],6);assert point['state'][3:6]==[0,0,0]
     errors=[max(abs(x-y) for x,y in zip(point['state'][:3],z[:3])),abs(point['state'][6]-z[3]),max(abs(x-y) for x,y in zip(point['strain'][:3],z[4:]))]
     for j,(err,budget) in enumerate(zip(errors,[5.,2e-7,2e-7])):assert err<=budget;maxima[variant][j]=max(maxima[variant][j],err)
     assert abs(point['state'][6]-(1.75*math.exp(-math.fsum(point['strain'][:3]))-1))<=2e-7
     count+=1
    if variant=='default':
     points=a['points'];middle=len(points)//2;state=points[middle]['state']
     for i in range(middle+1,len(points)):
      tag=name+f'/restart-{i}';rq=by[tag]['request'];expected_d=[x-y for x,y in zip(points[i]['strain'],points[i-1]['strain'])]
      assert [float(x) for x in rq['initial'].split(',')]==state
      assert [float(x) for x in rq['strain'].split(',')]==expected_d
      a1=out[tag];assert a1['ok'] is True;finite(a1['state'],7);state=a1['state'];restarts+=1
     assert max(abs(x-y) for x,y in zip(state[:6],points[-1]['state'][:6]))<=1e-6 and abs(state[6]-points[-1]['state'][6])<=1e-12
   assert maxima['tight'][0]<=maxima['default'][0]+.01 and maxima['tight'][1]<=maxima['default'][1]+1e-10
  state=oblique['initial']
  for i,d in enumerate(oblique['increments']):
   tag=f'oblique/{i}';q=by[tag]['request'];assert list(map(float,q['initial'].split(',')))==state and list(map(float,q['strain'].split(',')))==d
   a=out[tag];assert a['ok'] is True;finite(a['state'],7)
   assert max(abs(x-y) for x,y in zip(a['state'][:6],oblique['points'][i+1][:6]))<=5 and abs(a['state'][6]-oblique['points'][i+1][6])<=2e-7
   if not any(d):assert bits(state)==bits(a['state'])
   state=a['state']
  parent=[100000.,100000.,100000.,0.,0.,0.,.75]
  for tag in ('zero','after-failure'):assert out[tag]['ok'] is True and bits(out[tag]['state'])==bits(parent)
  fail=out['forced-failure'];assert fail['ok'] is False and bits(fail['state'])==bits(parent) and fail['diagnostics']['rejected']>0
  saved=read(D/f'release-v3/{backend}-results/assessment.json');assert maxima==saved['maximum_errors'] and saved['pass_all'] is True
  summaries[backend]={'calls':len(rows),'rate_cases':len(old),'reference_points':count,'restart_updates':restarts,'maximum_errors':maxima,'forced_failure_accepted_substeps':fail['diagnostics']['substeps']}
 comparisons=0
 for n,w in zip(journals['native'],journals['wasm']):
  assert n['id']==w['id'] and n['request']==w['request']
  a,b=outputs['native'][n['id']],outputs['wasm'][w['id']]
  for key in ('state','values'):
   if key in a:assert a[key]==b[key];comparisons+=len(a[key])
  if 'points' in a:
   assert len(a['points'])==len(b['points'])
   for x,y in zip(a['points'],b['points']):
    for key in ('state','strain'):assert x[key]==y[key];comparisons+=len(x[key])
    for key in ('control','p','q','q_signed','u'):assert x[key]==y[key];comparisons+=1
 supplement={}
 for backend in ('native','wasm'):
  rows=read(D/f'release-v3/{backend}-supplement.json');assert [x['id'] for x in rows]==['before','partial-failure','after','zero']
  a,b,c,z=[strict(x['raw']) for x in rows]
  assert rows[0]['request']==rows[2]['request'] and rows[1]['request']['settings']=='2e-10,1e-8,45,14,4,11'
  assert all(x['ok'] is True for x in (a,c,z)) and b['ok'] is False
  assert bits(a['state'])==bits(c['state']) and bits(b['state'])==bits(parent)==bits(z['state'])
  assert b['diagnostics']['attempted_substeps']==b['diagnostics']['discarded_substeps']==4 and not b['diagnostics']['partition_committed']
  assert all(x['catalogue_hash']==outputs[backend]['zero']['catalogue_hash'] for x in (a,b,c,z))
  supplement[backend]={'calls':4,'partial_progress_discarded':4,'parent_exact':True,'nonzero_recovery_exact':True,'journal_sha256':sha(D/f'release-v3/{backend}-supplement.json')}
 return {'transaction_supplement':supplement,'reviewer':'/root/barodesy_sand_interface_review','pass':True,'source_pins_unchanged':len(freeze['source_inputs'])-1,'non_governing_unit_alias_delta':'atlas/measurement_units.py','assessor_basis':'Adapted accepted saved-only reviewer audit; exact artifact reuse independently bound in prospective-reuse.json','source_revision':freeze['source_revision'],'backend_checks':summaries,'equal_physical_channels':comparisons,'compiled_calls':0,'journal_hashes':{b:sha(D/f'release-v3/{b}-results/journal.json') for b in journals}}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
