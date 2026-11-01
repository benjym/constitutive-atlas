"""Independent closure and saved source-guard replay, no process/backend calls."""
import contextlib,hashlib,io,json,runpy,subprocess,sys
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;A=P/'qualification-support-v4';V3=P/'qualification-support-v3';ROOT=P.parents[2];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def inv(root):
 allpaths=list(root.rglob('*'));check('cache and symlink-free/'+str(root),not any(x.is_symlink()or'__pycache__'in x.parts or x.suffix in['.pyc','.pyo']for x in allpaths));return{str(x.relative_to(root)):h(x)for x in allpaths if x.is_file()}
check('exact frozen support manifest',h(A/'manifest.json')=='568c116033e7d3bdd66a41dcd481b80e785bc247f594d9505a93bc0ef8a3ab6e')
check('all9 frozen packet files exact',len(load(A/'manifest.json'))==9 and all(h(A/k)==v for k,v in load(A/'manifest.json').items()))
newfreeze=load(A/'source-freeze.json');oldfreeze=load(V3/'source-freeze.json');NEW=Path(newfreeze['source_directory']);OLD=Path(oldfreeze['source_directory']);new=inv(NEW);old=inv(OLD);prep=load(A/'preparation.json')
check('all2628 new and2614 old source bytes/inventory exact',new==newfreeze['files'] and old==oldfreeze['files'] and len(new)==2628 and len(old)==2614)
check('all2614 prior files byte preserved',all(new[k]==v for k,v in old.items()))
check('exact14 prior enumerated missing deps now installed',len(prep['installed'])==14 and {k:new[k]for k in set(new)-set(old)}=={v['required_path']:v['required_sha256']for v in prep['installed']})
avail=load(V3/'availability-addendum-v1.json');check('prior manifest freeze availability exact',h(V3/'manifest.json')==prep['prior_manifest_sha256'] and h(V3/'source-freeze.json')==prep['prior_source_freeze_sha256'] and h(V3/'availability-addendum-v1.json')==prep['availability_sha256'])
check('all14 exact checkout acquisition routes verified',all(any(x['kind']=='current checkout read-only'and h(Path(x['path']))==row['required_sha256']for x in row['routes'])for row in prep['installed']))
runtime=load(ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json');diff=[k for k,v in runtime['source_files'].items()if new[k]!=v]
check('582runtime itself immutable exact',len(runtime['source_files'])==582 and all(h(Path(runtime['source_directory'])/k)==v for k,v in runtime['source_files'].items()))
check('only explicitly inherited J2 test overlay differs',diff==['tests/test_j2_main_routing.mjs'] and new[diff[0]]==old[diff[0]])
for path in ['catalogue/approved-models.json','catalogue/source-archive-map.json','catalogue/agent-reviews/source-archive-map.json']:
 check('registry/map unchanged/'+path,new[path]==old[path])
 if 'map'in path:
  doc=load(NEW/path);check('canonical archived targets exact/'+path,all(h(NEW/v['archived_path'])==v['sha256']for v in doc['entries']))
profiles=load(A/'patched-source-manifests.json')['profiles'];check('matcher mapping149/121 unchanged',profiles==load(V3/'patched-source-manifests.json')['profiles'] and len(profiles['maxwell']['files'])==149 and len(profiles['norsand']['files'])==121)
for name,v in profiles.items():check(name+'/every matcher source hash exact',all(new[k]==digest for k,digest in v['files'].items()) and hashlib.sha256(json.dumps(v['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==v['sha256'])
original=(V3/'audit_guards.py').read_text();adapted=(A/'audit_guards.py').read_text();check('reversible path identity-only adapter exact',adapted.replace(str(NEW),str(OLD)).replace('actual-nine-builder-source-guard-audit-v4','actual-nine-builder-source-guard-audit-v3')==original)
# Redirect ONLY review output D. Original SOURCE and all guard ASTs are unchanged.
namespace={'__file__':str(A/'audit_guards.py'),'__name__':'independent_guard_review','REVIEW':D};adapted=adapted.replace('D=Path(__file__).resolve().parent;SOURCE=', 'D=REVIEW;SOURCE=');blocked=lambda *a,**k:(_ for _ in ()).throw(AssertionError('review forbids process/backend invocation'))
with patch.object(subprocess,'run',blocked),patch.object(subprocess,'Popen',blocked),contextlib.redirect_stdout(io.StringIO())as out:
 exec(compile(adapted,str(A/'audit_guards.py'),'exec'),namespace);namespace['main']()
(D/'audit-summary.json').write_text(out.getvalue());check('nine guard results exact reproduction',load(D/'guard-closure.json')==load(A/'guard-closure.json'))
check('149/121 matcher report exact reproduction',load(D/'patched-source-manifests.json')==load(A/'patched-source-manifests.json'))
with patch.object(subprocess,'run',blocked),patch.object(subprocess,'Popen',blocked),contextlib.redirect_stdout(io.StringIO())as out:runpy.run_path(str(A/'verify.py'),run_name='__main__')
verification=json.loads(out.getvalue());check('author final verification exactly reproduced',verification==load(A/'verification.json'));(D/'verification-reproduced.json').write_text(out.getvalue())
check('all2628 source bytes unmodified after guards/verify',inv(NEW)==new)
(D/'checks.json').write_text(json.dumps({'decision':'accepted source-support closure only','compiled_calls':0,'spawned_processes':0,'checks':checks},indent=2)+'\n');print(len(checks),json.loads((D/'audit-summary.json').read_text()))
