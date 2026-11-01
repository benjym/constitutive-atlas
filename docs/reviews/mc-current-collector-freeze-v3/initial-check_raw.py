"""Prospective raw-journal/provenance negatives; manufactured fixtures only."""
from pathlib import Path
import copy,json,tempfile
from assess_paths import assess as paths,load
from assess_replays import assess as replays
from assess_parity import assess as parity
p=Path(__file__).resolve().parent
original={n:load(p/'synthetic'/n) for n in ['journal.json','calls.json','replays.json','rejections.json']}
requests=load(p/'requests.json');ref=load(p/'reference/reference-p360.json');cat=load(p/'catalogue.json');checks=[]
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 def save(data):
  for n,v in data.items():(d/n).write_text(json.dumps(v)+'\n')
 def rejects(label,mutate,gate='replays',role='native'):
  data=copy.deepcopy(original);mutate(data);assert data!=original,label;save(data)
  try:
   if gate=='replays':replays(d,role)
   elif gate=='paths':paths(data['journal.json'],requests,ref,cat)
   else:parity(original['journal.json'],data['journal.json'],requests)
  except (AssertionError,ValueError,KeyError,StopIteration):checks.append(label)
  else:raise AssertionError('false pass: '+label)
 save(original);assert replays(d,'native')['passed']
 rejects('native missing all process receipts',lambda x:[c.pop('process')for c in x['calls.json']])
 rejects('native missing one process receipt',lambda x:x['calls.json'][2].pop('process'))
 # Same artifact cannot be silently reclassified as Wasm.
 save(original)
 try:replays(d,'wasm')
 except AssertionError:checks.append('wasm rejects native process receipts')
 else:raise AssertionError('role false pass')
 for key,value in [('status',False),('status',1),('signal','SIGTERM'),('error','killed'),('stderr','unexpected')]:
  rejects('success process '+key,lambda x,k=key,v=value:x['calls.json'][2]['process'].__setitem__(k,v))
 rejects('describe nonzero exit',lambda x:x['calls.json'][0]['process'].__setitem__('status',1))
 rejects('describe missing receipt',lambda x:x['calls.json'][1].pop('process'))
 rejects('failure zero exit',lambda x:x['calls.json'][57]['process'].__setitem__('status',0))
 rejects('extra raw call',lambda x:x['calls.json'].append(copy.deepcopy(x['calls.json'][0])))
 rejects('wrong scope metadata',lambda x:x['journal.json'][1].__setitem__('raw',x['journal.json'][1]['raw'].replace('"scope": "effective"','"scope": "total"')),gate='paths')
 rejects('boolean echoed target',lambda x:x['journal.json'][1]['request'].__setitem__('target',True),gate='paths')
 for kind,raw in [('duplicate','{"ok":false,'),('unused overflow','{"unused":1e999,')]:
  def corrupt(x,raw=raw):
   x['journal.json'][1]['raw']=raw+x['journal.json'][1]['raw'][1:]
  rejects('path '+kind,corrupt,gate='paths');rejects('parity '+kind,corrupt,gate='parity')
  rejects('replay '+kind,lambda x,raw=raw:x['replays.json'][0].__setitem__('raw',raw+x['replays.json'][0]['raw'][1:]))
  rejects('rejection '+kind,lambda x,raw=raw:x['rejections.json'][0].__setitem__('raw',raw+x['rejections.json'][0]['raw'][1:]))
report={'passed':True,'negative_checks':len(checks),'checks':checks,'compiled_calls':0}
(p/'raw-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
