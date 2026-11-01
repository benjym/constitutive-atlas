"""Replay retained local integration evidence; no browser or compiled execution."""
from pathlib import Path
import hashlib,json,math,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
MID='tresca-associated-perfect-bk2022v1-be'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for name in ['source-pins.json','manifest.json']:
  for path,h in read(P/name)['files'].items():checked_receipt(ROOT,(P/name).relative_to(ROOT),path,h)
 pins=read(P/'source-pins.json')['files']
 def source(path):return checked_receipt(ROOT,(P/'source-pins.json').relative_to(ROOT),path,pins[path])
 assert source('models/'+MID+'.json').read_bytes()==source('docs/reviews/tresca-v5-source-integration-v1/public-model.json').read_bytes()
 assert source('catalogue/reviews/'+MID+'-source-v1.json').read_bytes()==source('docs/reviews/tresca-v5-source-integration-v1/pending-review.json').read_bytes()
 review=read(source('catalogue/reviews/'+MID+'-source-v1.json'))
 assert review['status']=='pending'and review['independent']is False and not review.get('reviewer')
 inventory=read(P/'package-inventory.json');assert inventory['executable_models']==10 and inventory['source_reviews']==inventory['pending_reviews']==19
 artifacts=read(source('catalogue/investigations/tresca-mixed-catalogue-v1/wasm-artifacts.json'))
 for path,h in artifacts.items():assert inventory['files'][Path(path).name]==h
 for path,asset in inventory['source_assets'].items():
  if path in pins:assert pins[path]==inventory['files'][asset]
 smoke=read(P/'package-check.json');assert smoke['status']=='passed'and smoke['catalogue_hash']==inventory['catalogue_hash']
 assert len(smoke['models'])==10 and len({m['id']for m in smoke['models']})==10
 for m in smoke['models']:
  result=m['result'];assert result['ok']and len(result['points'])==101
  for point in result['points']:
   assert all(math.isfinite(v)for v in point['state']+point['strain']+[point['p'],point['q']])
   if result['pore_pressure']['availability']=='unavailable':assert point['u']is None
 good=read(P/'browser/browser-export.json');bad=read(P/'browser/failed-browser-export.json')
 for d in [good,bad]:
  s=d['specification'];assert d['catalogue_hash']==inventory['catalogue_hash']and s['model']==MID
  assert s['stress_scope']=='total'and s['response_contract']=='stress-scope-0.1'
  assert s['initial']==[100000,100000,100000,0,0,0,.001,-.002,.003,.004,-.005,.006]
  assert s['steps']==100 and s['cycles']==1 and s['target']==.002
  assert d['result']['points'][0]['state']==s['initial']
  assert all(p['u']is None for p in d['result']['points'])
 assert good['result']['ok']and len(good['result']['points'])==101
 assert bad['result']['ok']is False and len(bad['result']['points'])==1
 assert bad['specification']['integration_settings']['max_iterations']==1
 assert bad['specification']['integration_settings']['max_depth']==0
 for name in ['python-tests','node-tests']:assert read(P/(name+'-process.json'))['returncode']==0
 assert 'Ran 57 tests' in read(P/'python-tests-process.json')['stderr']
 assert 'tests 8' in read(P/'node-tests-process.json')['stdout']
 checks={'invalid-import.ax.txt':['Explicit finite initial state required'],'forced-failure.ax.txt':['last committed point retained'],'form-restoration-after-fix.ax.txt':['100 increments','Value: 45','Value: 14'],'final-preserved-run.ax.txt':['1 sinusoidal cycle','100 increments','total stress','Unavailable: total stress has no pore-pressure law.'],'readable-dossier.ax.txt':['Tresca'],'final-import.ax.txt':['100 increments']}
 for path,words in checks.items():
  text=(P/'browser'/path).read_text()
  for word in words:assert word in text,(path,word)
 observations=read(P/'observations.json');assert observations['scientific_admission']is False and observations['deployed']is False
 return {'overall_pass':True,'executable_models_at_delivery':10,'pending_source_reviews_at_delivery':19,'compiled_artifacts_executed':False,'scientific_admission':False,'deployed':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
