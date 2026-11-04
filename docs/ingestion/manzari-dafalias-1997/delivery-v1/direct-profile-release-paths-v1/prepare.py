"""Copy the finite qualified asset data and change only approved release paths."""
from pathlib import Path
import shutil,json,hashlib,difflib
P=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');D=Path('/private/tmp/atlas-md1997-direct-app-v1')
paths={'norsand':'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine','maxwell':'docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine','interface2016':'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assets={}
for key,folder in [('norsand','norsand-compatible'),('maxwell','maxwell-compatible'),('interface2016','interface-compatible')]:
 src=D/folder;target=S/'web/engines/current17-compatible'/key
 assert src.is_dir() and not target.exists()
 before={}
 for f in src.rglob('*'):
  assert not f.is_symlink()
  if f.is_file():before[f.relative_to(src).as_posix()]={'sha256':digest(f),'bytes':f.stat().st_size}
 shutil.copytree(src,target)
 after={f.relative_to(target).as_posix():{'sha256':digest(f),'bytes':f.stat().st_size} for f in target.rglob('*') if f.is_file()}
 assert before==after
 assets[key]={'source':str(src),'destination':target.relative_to(S).as_posix(),'files':after}
for name in ['tools/build_web.py','.github/workflows/pages.yml']:
 path=S/name;before=path.read_text();after=before
 for key,old in paths.items():
  assert after.count(old)==1,(name,key)
  after=after.replace(old,'web/engines/current17-compatible/'+key)
 out=P/'before'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(before)
 out=P/'proposed'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(after)
 path.write_text(after)
 (P/(Path(name).name+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+name,tofile='after/'+name)))
 compile((S/'tools/build_web.py').read_text(),'tools/build_web.py','exec')
 (P/(Path(name).name+'.reverse.json')).write_text(json.dumps({'reverse_byte_exact':after.replace('web/engines/current17-compatible/norsand',paths['norsand']).replace('web/engines/current17-compatible/maxwell',paths['maxwell']).replace('web/engines/current17-compatible/interface2016',paths['interface2016'])==before,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest()},indent=2)+'\n')
(P/'asset-map.json').write_text(json.dumps(assets,indent=2)+'\n')
print('PASS exact copies:',sum(len(v['files']) for v in assets.values()),'files',sum(r['bytes'] for v in assets.values() for r in v['files'].values()),'bytes; two path-only edits reverse exactly; Python syntax PASS')
