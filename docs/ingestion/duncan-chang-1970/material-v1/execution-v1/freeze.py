"""One-shot exact closure freeze; run only before any compiled observations."""
from pathlib import Path
import json,hashlib,shutil,sys,subprocess,struct
B=Path(__file__).resolve().parent;R=B.parents[4];F=B/'frozen';assert not F.exists(),'Never overwrite a frozen study'
def bitify(x):
 if isinstance(x,float):return struct.pack('>d',x).hex()
 if isinstance(x,list):return [bitify(y) for y in x]
 if isinstance(x,dict):return {k:bitify(v) for k,v in x.items()}
 return x
assert bitify(json.loads((B/'requests.json').read_text()))==json.loads((B/'requests-binary64.json').read_text())
sys.path.insert(0,str(R))
from atlas.model import load
from atlas.compiler import generate
load(B/'candidate.json');generate(F/'generated',[B/'candidate.json'])
sources=[R/'cpp/main.cpp',*sorted((R/'cpp/include').rglob('*.hpp')),*sorted((R/'atlas').rglob('*.py')),*sorted((R/'schemas').glob('*.json'))]
bindings={}
for p in sources:
 rel=p.relative_to(R);dst=F/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);bindings[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
refs=[*B.glob('*.py'),*B.glob('*.mjs'),B/'CMakeLists.txt',B/'inspector.cpp',B/'POLICY.md',B/'candidate.json',B/'requests.json',B/'requests-binary64.json',B.parent/'reference.py',B.parent/'references.json',B.parent/'refinement.py',B.parent/'refinement-references.json',B.parent/'smooth_v2.py',B.parent/'smooth-v2.json']
for p in refs:bindings[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in (F/'generated').glob('*'):bindings[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
versions={}
for cmd in [['cmake','--version'],['clang++','--version'],['emcc','--version'],['node','--version'],['python3','--version']]:
 a=subprocess.run(cmd,capture_output=True,text=True);versions[' '.join(cmd)]=dict(exit=a.returncode,stdout=a.stdout,stderr=a.stderr)
(B/'freeze.json').write_text(json.dumps(dict(identity='duncan-complete-material-api-v1',files=bindings,toolchain=versions),indent=2)+'\n');print('Frozen',len(bindings),'files')
