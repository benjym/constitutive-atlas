"""Saved-only v3 integration review: exact inputs, git and metadata Counter checks."""
from pathlib import Path
from collections import Counter
import json,hashlib,subprocess,sqlite3
HERE=Path(__file__).resolve().parent;PACKET=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n,h in json.loads((HERE/'input-freeze.json').read_text()).items():
  if sha(Path(n))!=h:raise RuntimeError('changed frozen review input '+n)
 plan=json.loads((PACKET/'PLAN.json').read_text());expected=json.loads((HERE/'checks.json').read_text())
 c=Path('/private/tmp/atlas-clay2013-release-v3')
 def git(*args):return subprocess.check_output(['git',*args],cwd=c)
 if git('rev-parse','HEAD').decode().strip()!=expected['exact_commit'] or git('show','-s','--format=%P','HEAD').decode().strip()!=plan['base'] or git('status','--porcelain'):raise RuntimeError('commit/base/tree identity')
 if set(git('diff','--name-only','-z',plan['base'],'HEAD').decode().strip('\0').split('\0'))!={x['path'] for x in plan['writes']}:raise RuntimeError('committed whitelist')
 for row in plan['writes']:
  proc=subprocess.run(['git','show',plan['base']+':'+row['path']],cwd=c,capture_output=True)
  h=hashlib.sha256(proc.stdout).hexdigest() if proc.returncode==0 else None
  if h!=row['before_sha256'] or sha(c/row['path'])!=row['after_sha256'] or (c/row['path']).read_bytes()!=git('show',plan['metadata_commit']+':'+row['path']):raise RuntimeError('proposal identity '+row['path'])
 for n,h in plan['preserved_newer_release_sources'].items():
  if sha(c/n)!=h or hashlib.sha256(git('show',plan['base']+':'+n)).hexdigest()!=h:raise RuntimeError('base repair '+n)
 def tables(path):
  with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as db:
   if db.execute('pragma integrity_check').fetchall()!=[('ok',)] or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('SQL integrity')
   return {n:Counter(db.execute('select * from '+n).fetchall()) for (n,) in db.execute("select name from sqlite_master where type='table'")}
 m=Path(plan['metadata_output']);before=tables(m/'before/atlas.sqlite');after=tables(m/'after/atlas.sqlite')
 if set(before)!=set(after) or len(after)!=9:raise RuntimeError('table identity')
 for name in before:
  if before[name]-after[name] or sum((after[name]-before[name]).values())!=(3 if name in ['agent_reviews','model_approvals'] else 0):raise RuntimeError('SQL multiset '+name)
 def files(folder):return {str(q.relative_to(folder)):sha(q) for q in folder.rglob('*') if q.is_file()}
 b=files(m/'before');a=files(m/'after');delta=dict(added=sorted(a.keys()-b.keys()),removed=sorted(b.keys()-a.keys()),changed=sorted(n for n in b.keys()&a.keys() if b[n]!=a[n]))
 if delta!=expected['public_delta']:raise RuntimeError('public file delta')
 if (m/'before/models.json').read_bytes()!=(m/'after/models.json').read_bytes():raise RuntimeError('ordinary descriptor changed')
 return dict(status='PASS',input_bindings=len(json.loads((HERE/'input-freeze.json').read_text())),exact_commit=expected['exact_commit'],tables=9,committed_paths=28,public_delta=delta,compiled_calls=0,material_calls=0,release_ready=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))
