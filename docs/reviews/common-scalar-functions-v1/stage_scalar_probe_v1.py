"""Stage a fresh bounded scalar qualification closure; no shared-source mutation."""
from pathlib import Path
import shutil,json,hashlib
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=Path('/private/tmp/atlas-common-scalar-functions-v1/scalar-probe-source-v1');assert not dst.exists();dst.mkdir(parents=True)
for f in sorted((r/'cpp/include').rglob('*.hpp')):
 d=dst/f.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
for sub in ['cpp','cmake']:
 for f in sorted((p/'proposed-v2'/sub).rglob('*')):
  if f.is_file():
   d=dst/f.relative_to(p/'proposed-v2');d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
q=dst/'qualification';shutil.copytree(p/'qualification-v2',q,ignore=shutil.ignore_patterns('assessor-controls','__pycache__'))
fs=[f for f in dst.rglob('*') if f.is_file()];(p/'scalar-probe-source-freeze-v1.json').write_text(json.dumps({'identity':'common-scalar-functions-prospective-probe-v1','source':str(dst),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'policies':[str(p/'REFERENCE_POLICY_V1.md'),str(p/'qualification-design-freeze-v2.json')],'status':'No compiled observations; isolated bounded391case probe only'},indent=2)+'\n');print(len(fs),'staged files')
