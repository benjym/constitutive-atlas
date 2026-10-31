"""Portable regression entry point for authored ingestion packets; no author binaries."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKETS=('wu-bauer-1994','terracotta-2024','hca-sand-2005','pm4silt','hypoplastic-isa','original-cam-clay','s-clay1','duncan-chang-1970','manzari-dafalias-1997','hypoplastic-clay-2005','pm4sand','barodesy-sand','extended-mohr-coulomb-2013','barodesy-sand/rate-study-v1','hypoplastic-clay-2005/rate-study-v1','barodesy-sand/rate-review-v1','hypoplastic-clay-2005/rate-review-v1','barodesy-sand/rate-study-v2','hypoplastic-clay-2005/rate-study-v2','hypoplastic-thermal-ma-2017','hypoplastic-interface-2016','barodesy-sand/compiled-plan-review-v1','hypoplastic-clay-2005/guard-review-v2')
class IngestionPackets(unittest.TestCase):
 def assert_source_review_replay(self,family,count):
  from atlas.source_replay import registered
  result=registered(ROOT,'catalogue/source-replays/source-reviews-v1/registry.json','source-reviews')
  report=json.loads(result['stdout'])
  self.assertEqual(report['original_groups'],11)
  row=next(x for x in report['families']if x['family']==family)
  self.assertEqual(row['original_groups'],count);self.assertTrue(row['original_result_exact'])
 def run_python(self,*args):
  return subprocess.run([sys.executable,'-B',*args],cwd=ROOT,capture_output=True,text=True,timeout=60,check=True)
 def test_local_packet_receipts(self):
  for model in PACKETS:
   with self.subTest(model=model):
    folder=ROOT/'docs/ingestion'/model;manifest=json.loads((folder/'manifest.json').read_text());files=manifest['files']
    if type(files)is list:
     count=len(files);files={x['path']:x for x in files};self.assertEqual(len(files),count)
    self.assertIn('README.md',files)
    for name,pin in files.items():
     path=Path(name);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
     blob=(folder/path).read_bytes();self.assertEqual(hashlib.sha256(blob).hexdigest(),pin['sha256'] if type(pin)is dict else pin)
     if type(pin)is dict and 'bytes'in pin:self.assertEqual(len(blob),pin['bytes'])
    self.assertFalse(any(p.suffix.lower() in ('.pdf','.dll','.zip','.png','.so','.dylib','.pyc','.pyo','.o','.a') for p in folder.rglob('*')))
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
 def test_md1997_does_not_substitute_later_formulations(self):
  folder=ROOT/'docs/ingestion/manzari-dafalias-1997';manifest=json.loads((folder/'manifest.json').read_text());audit=json.loads((folder/'source-audit.json').read_text())
  for key in ('original_received','source_complete','equations_verified','executable_added','scientific_admission'):self.assertIs(manifest[key],False)
  self.assertEqual(audit['target']['doi'],'10.1680/geot.1997.47.2.255');self.assertIsNone(audit['target']['sha256']);self.assertEqual(audit['target']['equation_locators'],[])
 def test_clay2005_available_source_algebra_without_full_kernel_claim(self):
  folder=ROOT/'docs/ingestion/hypoplastic-clay-2005'
  self.run_python('-m','unittest','discover','-s',str(folder),'-p','test_packet.py','-v')
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'checks.json';self.run_python(str(folder/'check_packet.py'),'--output',str(output))
   actual=json.loads(output.read_text());stored=json.loads((folder/'checks.json').read_text())
   self.assertEqual(actual,stored);self.assertTrue(actual['passed']);self.assertEqual(actual['count'],40)
 def test_pm4sand_preserves_partial_source_gate_and_algebra_witnesses(self):
  folder=ROOT/'docs/ingestion/pm4sand';manifest=json.loads((folder/'manifest.json').read_text())
  self.run_python(str(folder/'check_packet.py'));self.assertIs(manifest['status']['source_complete'],False)
  self.assertEqual(len(manifest['unresolved_ids']),9)
 def test_barodesy2015_interior_algebra_and_fixture_replay(self):
  folder=ROOT/'docs/ingestion/barodesy-sand'
  self.run_python('-m','unittest','discover','-s',str(folder),'-p','test_algebra.py','-v')
  self.run_python(str(folder/'algebra.py'),'--check',str(folder/'fixtures.json'))
  self.assertIs(json.loads((folder/'manifest.json').read_text())['compiled_execution'],False)
 def test_emc2013_retains_source_reconciliation_gates(self):
  folder=ROOT/'docs/ingestion/extended-mohr-coulomb-2013'
  result=self.run_python(str(folder/'check_packet.py'))
  self.assertIn('9 bounded diagnostic groups pass',result.stdout)
  manifest=json.loads((folder/'manifest.json').read_text())
  self.assertIs(manifest['status']['primary_pdf_obtained'],True)
  self.assertIs(manifest['status']['source_complete'],False)
  self.assertIs(manifest['status']['executable_model_added'],False)
  self.assertIs(manifest['status']['scientifically_admitted'],False)
  self.assertEqual(manifest['unresolved_ids'],['EMC-01','EMC-02','EMC-03','EMC-04','EMC-05','EMC-06'])
 def test_clay2005_additive_source_correction_and_spd_defects(self):
  self.assert_source_review_replay('clay-v1',4)
 def test_barodesy2015_oracle_limits_remain_reproducible(self):
  self.assert_source_review_replay('sand-v1',3)
 def test_generic_rate_review_current_behavior_remains_fixed(self):
  folder=ROOT/'docs/reviews/generic-rate-transport-v1'
  manifest=json.loads((folder/'manifest.json').read_text())
  for name,pin in manifest['files'].items():
   path=Path(name);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
   blob=(folder/path).read_bytes();self.assertEqual(hashlib.sha256(blob).hexdigest(),pin['sha256']);self.assertEqual(len(blob),pin['bytes'])
  result=self.run_python(str(folder/'witnesses.py'),'--repo',str(ROOT),'--source',str(ROOT/'tools/research_rate_observations.py'),'--require-fixed')
  actual=json.loads(result.stdout);original=json.loads((folder/'final-witness-results.json').read_text())
  self.assertEqual(actual['input_sha256'],hashlib.sha256((ROOT/'tools/research_rate_observations.py').read_bytes()).hexdigest())
  self.assertEqual(actual['witnesses'],original['witnesses'])
  # Exact historical source/output reproduction is separately registered in test_source_replay.
 def test_revised_source_studies_preserve_historical_execution(self):
  from atlas.source_replay import registered
  registry='catalogue/source-replays/source-rates-v1/registry.json'
  for name in ('sand','clay'):
   with self.subTest(model=name):self.assertTrue(registered(ROOT,registry,name)['historical_output_reproduced'])
 def test_thermal_packet_diagnostics_and_six_open_gates(self):
  folder=ROOT/'docs/ingestion/hypoplastic-thermal-ma-2017'
  actual=json.loads(self.run_python(str(folder/'check_packet.py')).stdout)
  self.assertEqual(actual,json.loads((folder/'check-results.json').read_text()))
  manifest=json.loads((folder/'manifest.json').read_text())
  self.assertEqual(len(manifest['unresolved_ids']),6)
  self.assertFalse(manifest['status']['executable_model_added']);self.assertFalse(manifest['status']['complete_coupled_source'])
 def test_interface_partial_source_and_exact_representation(self):
  folder=ROOT/'docs/ingestion/hypoplastic-interface-2016'
  self.run_python(str(folder/'checks.py'),'--check',str(folder/'check-results.json'))
  self.run_python('-m','unittest','discover','-s',str(folder),'-p','test_checks.py','-v')
 def test_clay2005_v2_independent_guard_review(self):
  self.assert_source_review_replay('clay-guard-v2',4)
 def test_sand_prospective_mapping_review(self):
  from atlas.source_replay import registered
  result=registered(ROOT,'catalogue/source-replays/sand-prospective-v1/registry.json','sand-prospective')
  self.assertEqual(json.loads(result['stdout'])['original_mutation_groups'],8)
 def test_collection_identity_gap_remains_documented(self):
  folder=ROOT/'docs/reviews/generic-rate-collection-v1'
  manifest=json.loads((folder/'manifest.json').read_text())
  for name,pin in manifest['files'].items():
   path=Path(name);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
   blob=(folder/path).read_bytes();self.assertEqual(hashlib.sha256(blob).hexdigest(),pin['sha256']);self.assertEqual(len(blob),pin['bytes'])
  actual=json.loads(self.run_python(str(folder/'witnesses.py'),'--repo',str(ROOT)).stdout)
  self.assertEqual(actual,json.loads((folder/'witness-results.json').read_text()))

 def test_terracotta_temporal_packet_independent_algebra(self):
  folder=ROOT/'docs/ingestion/terracotta-2024'
  result=json.loads(self.run_python(str(folder/'checks.py')).stdout)
  self.assertEqual(result,json.loads((folder/'checks.json').read_text()))
  self.assertEqual(result['checks'],17);self.assertEqual(result['failures'],0)
 def test_wu_bauer_appendix_conflicts_and_exact_algebra(self):
  folder=ROOT/'docs/ingestion/wu-bauer-1994'
  result=json.loads(self.run_python(str(folder/'check_appendix.py')).stdout)
  self.assertEqual(result,json.loads((folder/'check-results.json').read_text()))
  self.assertEqual(result['upper_agreement_for_generic_witness'],19)
  self.assertEqual(set(result['retained_entry_conflicts']),{'L15','L55'})
  self.assertFalse(result['scientific_admission'])

if __name__=='__main__':unittest.main()
