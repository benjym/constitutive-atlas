"""Restore exact retained data only; no engine or scientific guard execution."""
from pathlib import Path
import tarfile,json,hashlib,shutil
R=Path('/Users/bmar5496/code/constitutive-atlas');S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');P=Path(__file__).resolve().parent;O=Path('/private/tmp/atlas-md1997-direct-app-v1')
proof=R/'docs/ingestion/manzari-dafalias-1997/delivery-v1/direct-profile-compatibility-v1'
res=json.loads((proof/'results.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
profiles={}
with tarfile.open(R/'.local/private-evidence/md1997-current-package-v7/complete-output.tar.gz') as t:
 for key,src,mapping in [('norsand','site/engine-path',{'engine.mjs':'atlas_path_capability.mjs','engine.wasm':'atlas_path_capability.wasm','qualification.json':'controlled-path-qualification.json','build-review.json':'build-review.json'}),('maxwell','site/engine-maxwell',{'maxwell.mjs':'maxwell.mjs','maxwell.wasm':'maxwell.wasm','qualification.json':'maxwell-qualification.json','build-review.json':'build-review.json'})]:
  dest=O/(key+'-compatible');dest.mkdir(parents=True,exist_ok=False)
  for old,new in mapping.items():(dest/new).write_bytes(t.extractfile(src+'/'+old).read())
  shutil.copytree(proof/'generated'/key,dest/'generated')
  profiles[key]={'directory':str(dest),'qualification':mapping['qualification.json'],'review':'build-review.json'}
src=S/'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine';dest=O/'interface-compatible';shutil.copytree(src,dest)
profiles['interface2016']={'directory':str(dest),'qualification':'refresh-qualification.json','review':'build-review.json'}
base={}
for directory in ['atlas','cpp','schemas']:
 for f in (S/directory).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and (f.suffix in ({'.py'} if directory=='atlas' else {'.json'} if directory=='schemas' else {'.cpp','.hpp'}) or directory=='cpp' and f.is_relative_to(S/'cpp/scalar-functions')):base[f.relative_to(S).as_posix()]=sha(f)
for key,row in profiles.items():
 dest=Path(row['directory']);q=json.loads((dest/row['qualification']).read_bytes());review=json.loads((dest/row['review']).read_bytes())
 assert q['status']=='passed' and review['status']=='accepted' and q['binding']==review['binding']
 source=dict(base)
 prior=res[key]['current_sources'] if key!='interface2016' else q['binding']['source_closure']
 source.update({n:sha(S/n) for n in prior})
 row.update(identity='current17-dedicated-profile-compatibility-v1',profile=key,source_files=dict(sorted(source.items())),files={f.relative_to(dest).as_posix():sha(f) for f in sorted(dest.rglob('*')) if f.is_file()},gates=q['gates'],old_binding=q['binding'],model=q['model'],proof_manifest_sha256='e156545f0e04bf9f9e29fa93afd99086444e2e94d53e7d9186952a5f686f6abf')
 row.pop('directory')
 if key=='interface2016':
  row['retained_repository_evidence']={n:h for group in ['commands','results'] for n,h in q['binding'][group].items()}
 write(dest/'source-compatibility.json',row)
write(P/'bindings.json',profiles)
print('Restored three dedicated asset directories; no runtime calls; no review decision created')
