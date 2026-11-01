"""Independent exact merge preservation; no build or compiled calls."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
BASE='217ef5e3c9e4604a7ac120dda81e9b7fbdb86714'
REMOTE='8e060a425015d65ffe087243204d17b8dba62ab8'
MERGE='7b17cdfb120e056647a9622168dc84e9efd6cd5a'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(rev,name):return json.loads(git('show',rev+':'+name))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=git('diff','--name-only',BASE+'..'+MERGE).decode().splitlines()
unequal=[n for n in paths if (ROOT/n).read_bytes()!=git('show',REMOTE+':'+n)]
assert unequal==['.github/workflows/verify.yml','IMPLEMENTATION_PLAN.md','catalogue/approved-models.json','catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json']
assert git('diff','--name-only',BASE+'..'+MERGE,'--','atlas','cpp','schemas','models','web/app.js','tools/build_web.py')==b''
registry='catalogue/approved-models.json'
a,b=read(BASE,registry),read(REMOTE,registry)
c=json.loads((ROOT/registry).read_text())
own=[x for x in a['models'] if x not in b['models']]
assert len(own)==1 and own[0]['model_id']=='original-cam-clay-sw-electronic-log-recovery-v1'
assert c=={**b,'models':b['models']+own}
maps={}
for name in ['catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json','docs/ingestion/burgers-itasca900/integration-v1/source-archive-map.json']:
 a,b=read(BASE,name),read(REMOTE,name);c=json.loads((ROOT/name).read_text())
 docs=dict(a['documents']);entries={}
 for k,v in b['documents'].items():
  assert k not in docs or docs[k]==v;docs[k]=v
 for x in a['entries']+b['entries']:
  k=(x['original_path'],x['sha256'])
  assert k not in entries or entries[k]==x;entries[k]=x
  assert sha(ROOT/x['archived_path'])==x['sha256']
 assert c['version']==a['version']==b['version']
 assert c['documents']==docs and len(c['entries'])==len(entries) and all(x in c['entries'] for x in entries.values())
 maps[name]=dict(documents=len(docs),entries=len(entries))
for x in ['web/app.js','tools/build_web.py','models/original-cam-clay-sw-electronic-log-recovery-v1.json','catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json']:
 assert (ROOT/x).read_bytes()==git('show',BASE+':'+x);paths.append(x)
print(json.dumps(dict(verdict='accepted_exact_merge_preservation',baseline=BASE,remote=REMOTE,merge=MERGE,incoming_files=158,remote_byte_equal=154,resolved_overlap=unequal,registry_entries=len(json.loads((ROOT/registry).read_text())['models']),archive_maps=maps,sha256={n:sha(ROOT/n) for n in sorted(set(paths))}),indent=2))
