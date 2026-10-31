from pathlib import Path
import json,hashlib,datetime,shutil,sys
root=Path('/Users/bmar5496/code/constitutive-atlas');stage=Path(__file__).parent
if (stage/'prospective-freeze.json').exists():raise RuntimeError('freeze already exists')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files={name:sha(root/name) for name in ['CMakeLists.txt','tests/test_laboratory_controls.py']}
for directory,patterns in [('cpp',['*.cpp','*.hpp']),('atlas',['*.py']),('schemas',['*.json']),('models',['*.json']),('tools',['test_wasm.mjs'])]:
 for pattern in patterns:
  for p in sorted((root/directory).rglob(pattern)):
   if p.is_file():files[str(p.relative_to(root))]=sha(p)
# Keep actual source bytes for reproducibility and future generic extensions.
for name in files:
 p=stage/'frozen'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,p)
local={}
for name in ['check.mjs','CONTRACT.md','POLICY.md','source_check.py','prior/main.cpp','prior/solver.hpp','source-check.json','freeze.py','build.py','test_laboratory_controls.py']:
 local[name]=sha(stage/name)
for p in sorted((stage/'source-review').rglob('*')):
 if p.is_file():local[str(p.relative_to(stage))]=sha(p)
old={}
for role in ['native','wasm']:
 receipt=json.loads((root/f'docs/reviews/nine-model-lab-integration/{role}-build.json').read_text())
 for name,entry in receipt['artifacts'].items():
  if sha(Path(entry['path']))!=entry['sha256']:raise RuntimeError('old artifact identity changed '+name)
  old[role+'/'+name]=entry
freeze={'identity':'explicit-laboratory-controls-v1','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'source_files':files,'local_files':local,'baseline_artifacts':old,'candidate_executions_at_freeze':0,'builds_at_freeze':0}
(stage/'prospective-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n');print('Frozen',len(files),'source files and',len(local),'study files.')
