"""Retained source bindings and fresh independent numerical reassessment."""
import json,unittest
from pathlib import Path
from atlas.evidence import checked_receipt
from tools.log1p_study import assess,read,verify_parity
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'catalogue/investigations/checked-log1p-v1'
class Log1pEvidence(unittest.TestCase):
 def test_retained_sources(self):
  manifest=read(PACKET/'manifest.json')
  for row in manifest['files']:
   with self.subTest(path=row['path']):checked_receipt(ROOT,str((PACKET/'manifest.json').relative_to(ROOT)),row['path'],row['sha256'])
 def test_fresh_numerics_and_parity(self):
  native=read(PACKET/'native.json');wasm=read(PACKET/'wasm-raw.json')
  assess(native);assess(wasm);verify_parity(wasm,native,PACKET/'native.json')
if __name__=='__main__':unittest.main()
