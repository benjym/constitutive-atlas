"""One-shot source/qualification closure; no material execution or compilation."""
from pathlib import Path
import hashlib,json,shutil,subprocess
B=Path(__file__).resolve().parent;R=B.parents[2];Q=B/'qualification';assert not (B/'qualification-freeze.json').exists()
for root in [Q/'frozen',Q/'catalogue-source']:
 for p in sorted((R/'cpp/include').rglob('*.hpp')):
  dst=root/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
files={}
for p in sorted(Q.rglob('*')):
 if p.is_file():files[p.relative_to(R).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in [B/'CONTRACT.md',B/'freeze_qualification.py',B/'preservation.json',B/'preservation-recorded.json',R/'docs/INCREMENTAL_SETTINGS.md',R/'cpp/main.cpp']:
 files[p.relative_to(R).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
for rel in ['docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz','docs/reviews/tresca-rounded-reference-v1/generate.py','docs/reviews/tresca-rounded-reference-v1/spectral_source.py','docs/reviews/certified-spectral-range-v1/exact.py']:
 p=R/rel;files[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
versions={}
for cmd in [['cmake','--version'],['clang++','--version'],['emcc','--version'],['node','--version']]:
 a=subprocess.run(cmd,capture_output=True,text=True);versions[' '.join(cmd)]=dict(exit=a.returncode,stdout=a.stdout,stderr=a.stderr)
(B/'qualification-freeze.json').write_text(json.dumps(dict(identity='bounded-partition-retry-qualification-v1',files=files,toolchains=versions),indent=2)+'\n');print('Frozen',len(files),'files')
