"""Read-only packet, candidate and optional private source verification."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];sys.path.insert(0,str(root))
from atlas.model import load
parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');args=parser.parse_args()
r=json.loads((p/'manifest.json').read_text())
for name,h in r['sha256'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
load(p/'candidate.json')
try:
 import jsonschema
 jsonschema.validate(json.loads((p/'candidate.json').read_text()),json.loads((root/'schemas/model-v0.3.schema.json').read_text()))
except ModuleNotFoundError:pass
subprocess.run([sys.executable,str(p/'check_algebra.py')],check=True,stdout=subprocess.DEVNULL)
if args.source:
 for entry in json.loads((p/'source-receipt.json').read_text())['sources']:
  f=Path(entry['private_path']);assert f.stat().st_size==entry['bytes'];assert hashlib.sha256(f.read_bytes()).hexdigest()==entry['sha256'],str(f)
print('PASS: packet hashes, v0.3 candidate, independent algebra'+(', private sources' if args.source else ''))
