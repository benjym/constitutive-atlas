"""Restore the exact interpreter-v3 source context into its explicitly owned stage."""
from pathlib import Path
import shutil,json,hashlib
HERE=Path(__file__).resolve().parent;DEST=Path('/private/tmp/atlas-norsand-path-v1')
for folder in ['atlas','schemas','cpp/include']:
 shutil.copytree(HERE/'backend-proposal-v5'/folder,DEST/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for file in (HERE/'proposed-v3').rglob('*'):
 if file.is_file():
  target=DEST/file.relative_to(HERE/'proposed-v3');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
for rel,expected in json.loads((HERE/'executed-stage-bindings-v3.json').read_text())['files'].items():assert hashlib.sha256((DEST/rel).read_bytes()).hexdigest()==expected,rel
print('Restored exact interpreter-v3 proposal and retained common source context')
