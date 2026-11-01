"""Freeze ordinary root build inputs before compiled observations."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OUT=HERE/'frozen/source'
assert not OUT.exists(), 'Preserve existing freeze'
paths={ROOT/'CMakeLists.txt',ROOT/'.github/workflows/verify.yml'}
for directory,patterns in [('atlas',['*.py']),('schemas',['*.json']),('cpp',['*.cpp','*.hpp']),('tests',['*.cpp','*.hpp','*.json']),('models',['*.json']),('cmake',['CMakeLists.txt']),('web',['*.mjs']),('tools',['*.mjs','*.py'])]:
    for pattern in patterns:
        paths.update((ROOT/directory).rglob(pattern))
paths.update(ROOT/p for p in ['catalogue/laboratory-package-policy.json','catalogue/laboratory-profile-policy.json','catalogue/approved-models.json','catalogue/manifest.json','catalogue/laboratory-examples.json','catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json','docs/models/duncan-chang-1970-endpoint-average.md'])
paths.update([HERE/'POLICY.md',HERE/'scoped-cases.json',HERE/'preset-inputs.json'])
files={}
for p in sorted(paths):
    rel=p.relative_to(ROOT); data=p.read_bytes(); dest=OUT/rel
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    files[str(rel)]=hashlib.sha256(data).hexdigest()
result=subprocess.run(['python3','-B','-m','atlas.compiler',str(HERE/'frozen/generated')],cwd=OUT,capture_output=True,text=True)
(HERE/'freeze-generation.log').write_text(result.stdout+result.stderr)
assert result.returncode==0
generated={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'frozen/generated').iterdir() if p.is_file()}
catalogue=json.loads((HERE/'frozen/generated/models.json').read_text())
assert len(catalogue['models'])==14
tools={}
for command in [['cmake','--version'],['c++','--version'],['emcc','--version'],['node','--version'],['python3','--version']]:
    p=subprocess.run(command,capture_output=True,text=True); assert p.returncode==0
    tools[' '.join(command)]=p.stdout+p.stderr
freeze=dict(identity='duncan-ordinary-atlas-integration-v1',source_root=str(OUT.relative_to(ROOT)),files=files,generated=generated,catalogue_hash=catalogue['sha256'],tools=tools)
(HERE/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
print(f'Frozen {len(files)} inputs,14models, catalogue {catalogue["sha256"]}')
