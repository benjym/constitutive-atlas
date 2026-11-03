"""Fail-closed exact original emitter/model context; no compiled execution."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PACKET=Path('docs/ingestion/vibe-2026/full-python-contracts-v1')
CONTEXT_SHA256='1a43fc7d94b86e6d439ce93ab90900d9443f9e9e764f34f4c5b90c4152a27b74'
def digest(blob):return hashlib.sha256(blob).hexdigest()
def verified(item):
 original=Path(item['path']);canonical=Path('catalogue/source-snapshots')/item['sha256']/original
 if original.is_absolute() or '..' in original.parts or item['archived_path']!=canonical.as_posix():raise ValueError('Unbound historical input')
 path=(ROOT/canonical).resolve()
 if not path.is_relative_to(ROOT.resolve()):raise ValueError('Unsafe historical input')
 try:blob=path.read_bytes()
 except OSError as exc:raise ValueError('Missing historical input') from exc
 if digest(blob)!=item['sha256']:raise ValueError('Corrupt historical input')
 return path

def context():
 try:blob=(ROOT/PACKET/'historical-context-v1.json').read_bytes()
 except OSError as exc:raise ValueError('Missing historical context') from exc
 if digest(blob)!=CONTEXT_SHA256:raise ValueError('Unknown or changed historical context')
 data=json.loads(blob)
 if data['version']!='controlled-time-historical-ordinary-v1':raise ValueError('Unknown historical context')
 manifest=data['baseline_manifest'];raw=(ROOT/manifest['path']).read_bytes()
 if digest(raw)!=manifest['sha256'] or json.loads(raw)!=data['expected_outputs']:raise ValueError('Changed original baseline receipt')
 for row in data['expected_outputs']:
  if digest((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('Changed original expected artifact')
 metadata=next(row for row in data['expected_outputs'] if row['path'].endswith('/models.json'))
 raw=(ROOT/metadata['path']).read_bytes()
 if digest(raw)!=metadata['sha256']:raise ValueError('Changed original baseline metadata')
 expected={m['id']:m for m in json.loads(raw)['models']};actual={}
 if len(data['models'])!=15:raise ValueError('Incomplete original model glob')
 for row in data['models']:
  model=json.loads(verified(row).read_text())
  if model['id'] in actual:raise ValueError('Duplicate original model')
  actual[model['id']]=model
 if actual!=expected:raise ValueError('Historical models differ from original baseline')
 verified(data['emitter'])
 return data

def generate(destination):
 data=context();source=verified(data['emitter']);spec=importlib.util.spec_from_file_location('atlas._vibe_original_31125_compiler',source);emitter=importlib.util.module_from_spec(spec);spec.loader.exec_module(emitter)
 # Preserve original basename ordering: content-addressed archive prefixes
 # are not the original default-glob sorting keys.
 with tempfile.TemporaryDirectory(prefix='atlas-original-31125-inputs-') as directory:
  paths=[]
  for row in data['models']:
   path=Path(directory)/Path(row['path']).name;path.write_bytes(verified(row).read_bytes());paths.append(path)
  return emitter.generate(destination,paths)
