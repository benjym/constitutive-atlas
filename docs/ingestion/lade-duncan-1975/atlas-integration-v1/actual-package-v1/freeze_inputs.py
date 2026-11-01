"""Freeze exact current package inputs immediately before standard builder execution."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((HERE/'PLAN.json').read_text());files={}
for name in ['atlas','web','tools','catalogue','models','schemas','docs/models','cpp/profiles','cmake/implicit-path-v1']:
 for p in sorted((ROOT/name).rglob('*')):
  if p.is_file() and p.suffix in ('.py','.mjs','.js','.json','.hpp','.cpp','.txt','.yml','.html','.css') and not any(x in p.parts for x in ('__pycache__','dist','preview')):
   files[p.relative_to(ROOT).as_posix()]=sha(p)
for name,folder in plan['inputs'].items():
 folder=Path(folder);folder=folder if folder.is_absolute() else ROOT/folder
 assert folder.is_dir(),folder
 for p in sorted(folder.rglob('*')):
  if p.is_file() and p.suffix in ('.wasm','.js','.mjs','.json') and 'CMakeFiles' not in p.parts:
   files[str(p)]=sha(p)
for name in ['PLAN.json','BROWSER_FAILURE_CASE.json','RETAINED_INPUTS.json','run_command.py','freeze_inputs.py','seal_package.py']:
 p=HERE/name;files[p.relative_to(ROOT).as_posix()]=sha(p)
out=HERE/'EXECUTION_SOURCE_FREEZE.json'
with out.open('x') as f:json.dump({'scope':'Current reviewed standard packaging and retained compiled inputs; prospective before actual package execution','files':files},f,indent=2);f.write('\n')
print(json.dumps({'files':len(files),'sha256':sha(out)}))
