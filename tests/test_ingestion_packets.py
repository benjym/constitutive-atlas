"""Portable regression entry point for authored ingestion packets; no author binaries."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKETS=('hca-sand-2005','pm4silt','hypoplastic-isa','original-cam-clay','s-clay1','duncan-chang-1970')
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
 def test_original_cam_clay_analytical_packet(self):
  self.run_python('docs/ingestion/original-cam-clay/test_packet.py')
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'checks.json'
   self.run_python('docs/ingestion/original-cam-clay/check_packet.py','--output',str(output))
   actual=json.loads(output.read_text());stored=json.loads((ROOT/'docs/ingestion/original-cam-clay/checks.json').read_text())
   self.assertTrue(actual['passed']);self.assertFalse(actual['general_constitutive_evaluator'])
   # The private PDF byte check is deliberately optional in a public checkout.
   public=lambda d:[x for x in d['source_checks'] if x['name']!='source-hash']
   self.assertEqual(public(actual),public(stored))
 def test_s_clay1_reports_missing_equations_without_fabricated_closure(self):
  result=json.loads(self.run_python('docs/ingestion/s-clay1/check_packet.py').stdout)
  self.assertEqual(result['constitutive_checks_run'],0);self.assertFalse(result['original_equations_verified'])
 def test_duncan_chang_original_and_correction_remain_unverified(self):
  folder=ROOT/'docs/ingestion/duncan-chang-1970';manifest=json.loads((folder/'manifest.json').read_text());audit=json.loads((folder/'source-audit.json').read_text())
  self.assertFalse(manifest['constitutive_equations_verified']);self.assertFalse(manifest['full_source_ingestion_complete'])
  self.assertEqual(audit['original']['doi'],'10.1061/JSFEAQ.0001458');self.assertEqual(audit['correction']['doi'],'10.1061/JSFEAQ.0001706')
  self.assertIsNone(audit['original']['pdf_sha256']);self.assertIsNone(audit['correction']['pdf_sha256']);self.assertFalse(audit['correction']['correction_content_verified'])
if __name__=='__main__':unittest.main()
