"""Authenticate current paired CI evidence and assess saved JSON only."""
import hashlib,json,subprocess,sys,zipfile,shutil
from pathlib import Path
RUN=41388826742
HEAD="43ea5c45f0e6112661fe996b685a3adcdac12ce6"
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
platform=sys.argv[1];assert platform in ("Linux","macOS")
label={"Linux":"LINUX","macOS":"MACOS"}[platform]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
raw=subprocess.check_output(['gh','api',f'repos/benjym/constitutive-atlas/actions/runs/{RUN}/artifacts'])
items=[x for x in json.loads(raw)['artifacts'] if x['name']=='bingham-paired-'+platform]
assert len(items)==1
a=items[0];assert a['workflow_run']['head_sha']==HEAD and a['workflow_run']['id']==RUN and not a['expired']
private=ROOT/'.local'/f'bingham-ci-paired-{label.lower()}-{RUN}'
assert not private.exists();private.mkdir(parents=True)
z=private/'artifact.zip'
with z.open('xb') as f:subprocess.run(['gh','api',f"repos/benjym/constitutive-atlas/actions/artifacts/{a['id']}/zip"],stdout=f,check=True)
assert a['digest']=='sha256:'+sha(z)
files=private/'files';files.mkdir()
with zipfile.ZipFile(z) as f:
 for n in f.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
 f.extractall(files)
checks={}
for kind in ('native','wasm','parity'):
 if kind=='parity':cmd=[sys.executable,'-B',str(ROOT/'docs/ingestion/bingham-comsol63/execution-v5/parity.py'),str(files/'bingham-native.json'),str(files/'bingham-wasm.json')]
 else:cmd=[sys.executable,'-B',str(ROOT/'docs/ingestion/bingham-comsol63/execution-v5/study.py'),'assess','--raw',str(files/f'bingham-{kind}.json')]
 r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (HERE/f'{label}-PAIRED-{kind.upper()}-ASSESSMENT.log').write_bytes(r.stdout)
 checks[kind]=r.returncode==0
posts=[]
for p in sorted(files.rglob('post.json')):
 d=json.loads(p.read_text());assert d['all_records_unchanged'] is True
 posts.append({'path':str(p.relative_to(files)),'kind':d['kind'],'sha256':sha(p),'all_records_unchanged':True})
assert len(posts)==5
durable=Path('/Users/bmar5496/code/constitutive-atlas/.local/private-evidence/bingham-release-ci-v3')/f'{private.name}-artifact.zip'
durable.parent.mkdir(parents=True,exist_ok=True);assert not durable.exists();shutil.copyfile(z,durable);assert sha(z)==sha(durable)
out={'source_revision':HEAD,'run_id':RUN,'artifact':a,'private_zip':str(z),'durable_private_zip':str(durable),'zip_sha256':sha(z),'files':{str(p.relative_to(files)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files.rglob('*')) if p.is_file()},'checks':checks,'unchanged_post_receipts':posts,'saved_assessment_only_no_material_execution':True}
(HERE/f'{label}-PAIRED-ARTIFACT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'platform':platform,'checks':checks,'files':len(out['files']),'post_receipts':len(posts)}));assert all(checks.values())
