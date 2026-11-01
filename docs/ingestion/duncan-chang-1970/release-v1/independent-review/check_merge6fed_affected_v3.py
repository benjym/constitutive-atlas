"""Check exact remote affected receipt pairs in merged tree; saved-source only."""
from pathlib import Path
import subprocess,json,sys,hashlib
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
pre=Path('docs/ingestion/duncan-chang-1970/release-v2/merge-6fed-v1');a=json.loads((root/pre/'proposal.json').read_text());targets={r['path']:{r['own_sha256'],r['remote_sha256']} for r in a['operations']};g=lambda *args:subprocess.check_output(['git',*args],cwd=root);paths=g('diff','--name-only','9cefd1a6','6fed3e1e').decode().splitlines();pairs=set()
def walk(n,d):
 if isinstance(n,dict):
  for k,v in n.items():
   if k in targets and isinstance(v,str) and v in targets[k]:pairs.add((d,k,v))
  p=n.get('path',n.get('original_path'));h=n.get('sha256',n.get('hash'))
  if isinstance(p,str) and p in targets and h in targets[p]:pairs.add((d,p,h))
  for v in n.values():walk(v,d)
 elif isinstance(n,list):
  for v in n:walk(v,d)
for p in paths:
 if not p.endswith('.json') or p.startswith('catalogue/source-snapshots/'):continue
 try:walk(json.loads(g('show','6fed3e1e:'+p)),p)
 except json.JSONDecodeError:pass
errors=[];passed=[]
for d,p,h in sorted(pairs):
 try:checked_receipt(root,d,p,h);passed.append({'document':d,'path':p,'sha256':h})
 except Exception as e:errors.append({'document':d,'path':p,'sha256':h,'error':str(e)})
print(json.dumps({'status':'FAIL' if errors else 'PASS','remote':'6fed3e1e368337f02bbc67c2eef263d03b7c8c4a','affected_pairs':len(pairs),'passed':len(passed),'failures':errors,'passed_predicates':passed},indent=2))
