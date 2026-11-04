"""Generate a distinct native test catalogue from exactly five pinned v0.1 records."""
from pathlib import Path
import json,shutil,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas.compiler import generate
from tests.recorded_native_fixtures import LEGACY_HASH,legacy_paths

def generate_legacy(output):
 with tempfile.TemporaryDirectory(prefix='atlas-recorded-legacy-models-')as directory:
  inputs=Path(directory)
  for source in legacy_paths():
   model=json.loads(source.read_text())
   if model['schema_version']!='0.1':raise ValueError('legacy recorded fixture must remain v0.1')
   shutil.copyfile(source,inputs/(model['id']+'.json'))
  generate(output,sorted(inputs.glob('*.json')))
 result=json.loads((Path(output)/'models.json').read_text())
 if result['sha256']!=LEGACY_HASH or len(result['models'])!=5:raise ValueError('generated legacy recorded catalogue identity changed')
 return result
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('one explicit output directory required')
 generate_legacy(Path(sys.argv[1]))
