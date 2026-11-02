"""Prospective coordinator freeze: reads Git/source/assets only, writes NEW freeze here.
Never provisions, executes modules/materials/builds/browser, or mutates Git.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;REPO=Path('/Users/bmar5496/code/constitutive-atlas')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def parents(revision):
 row=git('rev-list','--parents','-n','1',revision).decode().split();assert row[0]==revision;return row[1:]
def tree(revision):
 result={}
 for item in git('ls-tree','-r','-z',revision).split(b'\0'):
  if not item:continue
  meta,name=item.split(b'\t');mode,kind,oid=meta.decode().split();assert kind=='blob';result[name.decode()]={'git_blob':oid,'mode':mode}
 return result
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--revision',required=True);a=ap.parse_args();plan=json.loads((HERE/'plan.json').read_text());root=Path(plan['cwd']);assert root.is_dir();assert parents(a.revision)==plan['parents'];assert not (HERE/'source-freeze.json').exists();tracked=tree(a.revision)
 changed=set()
 for parent in plan['parents']:changed.update(n.decode() for n in git('diff-tree','-r','--no-commit-id','--name-only','-z',parent,a.revision).split(b'\0') if n)
 prefixes=('tools/','atlas/','web/','models/','schemas/','cpp/','catalogue/','data/','docs/models/','docs/benchmarks/','docs/capabilities/','docs/development/')
 selected={n for n in tracked if n.startswith(prefixes) and not n.startswith('catalogue/source-snapshots/') and '/dist/' not in n and '/preview/' not in n}|{n for n in changed if n in tracked}
 selected.update(n for n in ['CMakeLists.txt','pyproject.toml','requirements.txt','requirements-dev.txt'] if n in tracked)
 # Follow explicit source/receipt SHA pairs, including canonical snapshots, without scanning all historical evidence.
 def references(value):
  if isinstance(value,dict):
   if any(isinstance(value.get(k),str) and len(value[k])==64 for k in ['sha256','hash']):
    for field in ['path','original_path','archived_path']:
     if isinstance(value.get(field),str):yield value[field]
   for k,v in value.items():
    if isinstance(k,str) and '/' in k and isinstance(v,str) and len(v)==64:yield k
    yield from references(v)
  elif isinstance(value,list):
   for item in value:yield from references(item)
 parsed=set()
 while True:
  queue=sorted(n for n in selected-parsed if n.endswith('.json'))
  if not queue:break
  for n in queue:
   parsed.add(n)
   try:obj=json.loads((root/n).read_text())
   except (UnicodeError,json.JSONDecodeError):continue
   selected.update(n for n in references(obj) if n in tracked)
 # No historical-tree byte scan. Every selected actual file must equal its target Git blob.
 total=sum((root/n).stat().st_size for n in selected);assert total<=750*1024*1024,('Closure unexpectedly large; retain diagnostic and explicitly review closure rather than silently omit',total)
 source={}
 for n in sorted(selected):
  q=root/n;assert q.is_file() and not q.is_symlink();data=q.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==tracked[n]['git_blob'],('Actual source differs from commit',n)
  source[n]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),**tracked[n]}
 deleted=sorted(n for n in changed if n not in tracked)
 for n in deleted:assert not (root/n).exists(),('Deleted commit path present',n)
 assets={}
 for i,arg in enumerate(plan['argv']):
  if not arg.endswith('-wasm-dir'):continue
  directory=Path(plan['argv'][i+1]);assert directory.is_dir(),('Provision/retain exact assets first',directory)
  for q in directory.rglob('*'):
   if q.is_file() and q.suffix in ['.js','.mjs','.wasm','.json'] and not any(n in q.parts for n in ['CMakeFiles','node_modules','.cache','_deps']):assets[str(q)]={'sha256':sha(q),'bytes':q.stat().st_size}
 # Normal dataset builder's implicit asset paths (including ignored retained copies).
 grants={g['archive_sha256'] for g in json.loads((root/'data/experiment_releases.json').read_text())['grants']}
 for item in json.loads((root/'data/sources.json').read_text())['sources']:
  if item['sha256'] in grants:
   q=root/'data/raw'/item['filename'];assert sha(q)==item['sha256'];assets[str(q)]={'sha256':item['sha256'],'bytes':q.stat().st_size}
 curated=root/'data/curated/index.json'
 if curated.exists():
  for item in json.loads(curated.read_text())['records']:
   q=curated.parent/item['path'];n=q.relative_to(root).as_posix()
   if n in source:assert source[n]['sha256']==item['sha256']
   else:assert sha(q)==item['sha256'];assets[str(q)]={'sha256':item['sha256'],'bytes':q.stat().st_size}
 witness=root/'.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json';assert sha(witness)=='ee7e4ad4b34c14843c6f7d0b2d66a936d8c8409fa1e2dc2c493949a9411589f9';assets[str(witness)]={'sha256':sha(witness),'bytes':witness.stat().st_size}
 report={'status':'frozen-source-only; no package execution','revision':a.revision,'parents':plan['parents'],'cwd':str(root),'plan_sha256':sha(HERE/'plan.json'),'wrapper_sha256':sha(HERE/'run_package.py'),'freeze_script_sha256':sha(__file__),'branch_delta_paths':sorted(changed),'source':source,'deleted_paths':deleted,'qualified_assets_and_ignored_witness':assets,'source_bytes':total,'selection':'union of both parent deltas; runtime/source/model/schema/catalogue/data roots; public dossiers/benchmark/capability/development inputs; recursive explicit JSON receipt hash references. No all-history byte scan.'}
 with (HERE/'source-freeze.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'status':report['status'],'source_files':len(source),'source_bytes':total,'assets':len(assets),'revision':a.revision},indent=2))
if __name__=='__main__':main()
