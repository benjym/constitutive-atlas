"""Read-only source/plan integrity check; never executes compilers or solvers."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((HERE/'plan.json').read_text())
receipt=ROOT/plan['source_receipt']
assert digest(receipt)==plan['source_receipt_sha256']
source=Path(plan['source_directory']);files=json.loads(receipt.read_text())['source_files']
assert len(files)==578
for path,h in files.items():assert digest(source/path)==h,path
assert len(plan['profiles'])==8
assert len({p['profile'] for p in plan['profiles']})==8
for profile in plan['profiles']:
    cmake=(source/profile['cmake_directory']/'CMakeLists.txt').read_text()
    assert profile['target'] in cmake,profile['profile']
    assert profile['execution_status']=='not executed by plan author'
manifest=HERE/'manifest.json'
if manifest.exists():
    for path,h in json.loads(manifest.read_text())['files'].items():assert digest(HERE/path)==h,path
print(json.dumps({'status':'passed','source_files':len(files),'profiles':8,'compiled_calls':0}))
