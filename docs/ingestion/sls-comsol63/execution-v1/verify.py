"""Read-only verification of retained SLS qualification and exact archives."""
import hashlib,json,subprocess,sys,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tarfile.open(B/'runtime-source.tar.gz')as t:
    pinned=json.loads((B/'freeze-v2.json').read_text())['pins']
    for name,value in pinned.items():
        actual=hashlib.sha256(t.extractfile(name).read()).hexdigest()
        if name=='atlas/agent_review.py':
            context=json.loads((B/'runtime-archive-context.json').read_text());assert actual==context['context_only_differences'][name]['archived_sha256'];assert name not in json.loads((B/'build-source-context.json').read_text())['actual_compiler_modules']
        else:assert actual==value,name
assert sha(B/'runtime-source.tar.gz')==json.loads((B/'build-input-receipt.json').read_text())['archive_sha256']
assert sha(B/'authoring-v1/study.py')==json.loads((B/'freeze.json').read_text())['pins']['docs/ingestion/sls-comsol63/execution-v1/study.py']
for file in ['observation-repair-freeze.json','wasm-assessor-freeze.json']:
    record=json.loads((B/file).read_text())
    for name,value in record['pins'].items():assert sha(B/name)==value,name
before=json.loads((B/'native-raw.json').read_text());after=json.loads((B/'native-observe-v2-raw.json').read_text())
assert len(before)==len(after)and all(a['calls']==b['calls']for a,b in zip(before,after))
assert sha(ROOT/'models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json')==sha(B.parent/'candidate.json')
subprocess.run([sys.executable,str(B.parent/'verify_packet.py')],cwd=ROOT,check=True)
result=subprocess.run([sys.executable,str(B/'check_saved.py')],cwd=ROOT,capture_output=True,text=True,check=True)
assert json.loads(result.stdout)==json.loads((B/'parity-report.json').read_text())
manifest=B/'manifest.json'
if manifest.exists():
    for name,value in json.loads(manifest.read_text())['files'].items():assert sha(B/name)==value,name
print('PASS: exact archived runtime/cases/active freeze, retained failures, unchanged material responses, model bytes, source packet and native/Wasm analytical/parity evidence.')
