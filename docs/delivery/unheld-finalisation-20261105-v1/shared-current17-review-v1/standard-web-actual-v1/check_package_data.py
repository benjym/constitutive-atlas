"""Future read-only package inventory and immutable public-data audit.
Run only after coordinator hands off complete frozen actual package evidence.
No build/module/material/browser/network/Git/source installation.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,stat
H=Path(__file__).resolve().parent;N=H.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--site',required=True,type=Path);p.add_argument('--inventory',required=True,type=Path);a=p.parse_args();site=a.site.resolve();rows=read(a.inventory)['files'];checks=0
 def check(value,label):
  nonlocal checks
  assert value,label;checks+=1
 expected={}
 for r in rows:
  path=Path(r['path']);check(not path.is_absolute()and'..'not in path.parts,'safe inventory member');check(str(path)not in expected,'unique inventory member');expected[str(path)]=r
 actual={str(q.relative_to(site)):q for q in site.rglob('*')if q.is_file()or q.is_symlink()};check(set(actual)==set(expected),'complete physical file namespace')
 for name,q in actual.items():
  r=expected[name];check(not q.is_symlink()and q.resolve().is_relative_to(site),'regular contained file');check(q.stat().st_size==r.get('size_bytes',r.get('bytes'))and sha(q)==r['sha256'],'physical byte identity '+name)
  if 'mode'in r:check(stat.S_IMODE(q.stat().st_mode)==(int(r['mode'],8)if isinstance(r['mode'],str)else r['mode']),'physical mode '+name)
 identity=read(N/'standard-web-delivery-plan-v1/source-identity.json');models=read(site/'models.json');check(sha(site/'models.json')==identity['expected_catalogue_file_sha256'],'ordinary generated JSON exact');check(models['sha256']==identity['expected_runtime_catalogue_hash']and len(models['models'])==17,'ordinary17 runtime')
 for mid,r in identity['ordinary_models'].items():check(sha(site/'models'/f'{mid}.json')==r['sha256'],'model definition '+mid)
 catalogue=read(site/'catalogue.json');check(len(catalogue.get('models',catalogue.get('entries',[])))==51,'51 catalogue profiles')
 examples=read(site/'laboratory-examples.json');check([x['id']for x in examples['examples']]==identity['named_ids'],'strict9 example order');check(examples['catalogue_hash']==models['sha256'],'examples current catalogue')
 for row in examples['examples']:
  q=site/'laboratory-examples'/f"{row['id']}.json";check(sha(q)==row['document_sha256'],'input-only example exact '+row['id']);check('result'not in read(q),'no manufactured example result');check(sha(site/'models'/f"{row['model']}.json")==row['definition_sha256'],'example definition exact')
 index=site/'experiments/index.json';check(sha(index)=='beb573d848ebaa8b167aefc4d181eeb9034a52abd48f6b6083c27f5098cc88f3','original994 complete index identity');entries=read(index)['experiments'];check(len(entries)==994,'994 index entries')
 # Index bytes bind IDs/order/rights/rows/metadata and logical/wire identities.
 for e in entries:
  t=e['transport'];q=site/'experiments'/t['path'];check(t['path']==e['path']+'.gz'and t['size_bytes']==q.stat().st_size and sha(q)==t['sha256'],'exact gzip wire '+e['id'])
  with gzip.open(q,'rb')as f:raw=f.read(e['size_bytes']+1)
  check(len(raw)==e['size_bytes']and hashlib.sha256(raw).hexdigest()==e['sha256'],'bounded decoded logical bytes '+e['id']);check(len(json.loads(raw)['rows'])==e['rows'],'original measurement rows '+e['id'])
 old=read(Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/manzari-dafalias-1997/delivery-v1/final-live-v1/upload-manifest.json'));old={r['path']:r for r in old['files']}
 for name,r in old.items():
  if name.startswith('experiments/'):check(sha(site/name)==r['sha256'],'exact old994 index/transport member '+name)
 print(json.dumps({'passed':True,'checks':checks,'files':len(actual),'measurements':994,'ordinary_models':17,'profiles':51,'input_only_examples':9,'material_module_calls':0},indent=2))
if __name__=='__main__':main()
