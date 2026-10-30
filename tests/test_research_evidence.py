"""Bind retained numerical results to source/code and independent references."""
import hashlib,json,unittest
from atlas.model import ROOT,load
from atlas.initialization import canonical_hash
from tools.verify_research_matrix_wasm import verify

class ResearchEvidence(unittest.TestCase):
 def test_investigation_receipts_and_no_public_admission(self):
  for name in ('gis2024-hp-host-v1','gis2024-coupled-rates-v1','clay-nonisotropic-v1','pm4-order-reconciliation-v1'):
   m=json.loads((ROOT/'catalogue/investigations'/name/'manifest.json').read_text())
   self.assertFalse(m['public_admission']);self.assertFalse(m['complete_model'])
   for path,expected in (m.get('dependencies',{})|m['files']).items():
    self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)
 def test_retained_gis_native_and_wasm_against_cartesian_rates(self):
  from tools.gis2024_rate_study import MODEL_PATH,REFERENCE_PATH,assess
  model=load(MODEL_PATH);cases=json.loads(REFERENCE_PATH.read_text())['cases'];folder=ROOT/'catalogue/investigations/gis2024-coupled-rates-v1'
  native=json.loads((folder/'native.json').read_text());wasm=json.loads((folder/'wasm.json').read_text())
  self.assertEqual(native['catalogue_hash'],canonical_hash([model]));self.assertEqual(native['model_sha256'],canonical_hash(model));assess(native['records'],model,cases);verify(wasm)
  self.assertEqual(wasm['native_report_sha256'],hashlib.sha256((folder/'native.json').read_bytes()).hexdigest())
 def test_retained_clay_chained_native_and_wasm_against_cartesian_paths(self):
  from tools.clay2013_nonisotropic_study import MODEL_PATH,assess,digest
  from tools.clay2013_path_reference import study
  model=load(MODEL_PATH);reference=study();folder=ROOT/'catalogue/investigations/clay-nonisotropic-v1'
  native=json.loads((folder/'native.json').read_text());wasm=json.loads((folder/'wasm.json').read_text())
  receipt=json.loads((folder/'evidence.json').read_text())
  self.assertEqual(native['reference_sha256'],digest(receipt));self.assertEqual(native['model_sha256'],canonical_hash(model));assess(native['records'],model,reference);verify(wasm,reference_receipt=receipt)
  self.assertEqual(wasm['native_report_sha256'],hashlib.sha256((folder/'native.json').read_bytes()).hexdigest())
 def test_parallel_queue_exact_candidate_coverage(self):
  catalogue=json.loads((ROOT/'catalogue/manifest.json').read_text())['models'];queue=json.loads((ROOT/'catalogue/research-queues/parallel-source-queue-2026-10-31.json').read_text())
  expected={m['id']for m in catalogue if m['status']=='candidate'};actual=[m['formulation_id']for m in queue['formulations']]
  self.assertEqual(len(actual),len(set(actual)));self.assertEqual(set(actual),expected)
  self.assertEqual(queue['snapshot_counts']['candidates'],len(expected));self.assertEqual(queue['snapshot_counts']['public_executable'],sum(m['executable']for m in catalogue))

if __name__=='__main__':unittest.main()
