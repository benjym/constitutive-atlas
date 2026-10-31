"""Portable regression entry point for authored ingestion packets; no author binaries."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKETS=('hca-sand-2005','pm4silt','hypoplastic-isa')
class IngestionPackets(unittest.TestCase):
 def run_python(self,*args):
  return subprocess.run([sys.executable,'-B',*args],cwd=ROOT,capture_output=True,text=True,timeout=60,check=True)
 def test_local_packet_receipts(self):
  for model in PACKETS:
   with self.subTest(model=model):
    folder=ROOT/'docs/ingestion'/model;manifest=json.loads((folder/'manifest.json').read_text());files=manifest['files']
    self.assertIn('README.md',files)
    for name,pin in files.items():
     path=Path(name);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
     self.assertEqual(hashlib.sha256((folder/path).read_bytes()).hexdigest(),pin)
    self.assertFalse(any(p.suffix.lower() in ('.pdf','.dll','.zip','.png','.so','.dylib') for p in folder.rglob('*')))
 def test_hca_source_distinguishing_fixtures(self):
  self.run_python('-m','unittest','discover','-s','docs/ingestion/hca-sand-2005','-p','test_fixtures.py','-v')
 def test_pm4silt_source_distinguishing_fixtures(self):
  self.run_python('docs/ingestion/pm4silt/checks.py')
  result=self.run_python('docs/ingestion/pm4silt/checks.py','--json')
  self.assertEqual(json.loads(result.stdout),json.loads((ROOT/'docs/ingestion/pm4silt/check-results.json').read_text()))
 def test_isa_supplied_host_contract_and_checks(self):
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'checks.json'
   self.run_python('docs/ingestion/hypoplastic-isa/check_packet.py','--repo',str(ROOT),'--output',str(output))
   actual=json.loads(output.read_text());stored=json.loads((ROOT/'docs/ingestion/hypoplastic-isa/checks.json').read_text())
   # Private source availability is provenance; portable algebra must still run without PDFs.
   self.assertTrue(actual['passed']);self.assertFalse(actual['constitutive_evaluator']);self.assertEqual(actual['compiled_calls'],0)
   public=lambda d:[x for x in d['checks'] if not x['name'].startswith('private-source:')]
   self.assertEqual(public(actual),public(stored))
if __name__=='__main__':unittest.main()
