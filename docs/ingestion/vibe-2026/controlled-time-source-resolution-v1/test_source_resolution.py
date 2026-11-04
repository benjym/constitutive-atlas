"""Pure isolated source checks; never creates an accepted new-review decision."""
import importlib.util,json,hashlib,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
SPEC=importlib.util.spec_from_file_location('controlled_ci',ROOT/'tools/check_controlled_time_ci.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
class SourceResolutionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
  self.addCleanup(patch.stopall);patch.object(m,'ROOT',self.root).start()
  self.current={s:m.sha(ROOT/s) for s in ['tests/test_controlled_time.py','tools/check_controlled_time_ci.py']}
  self.triples=sorted(m.HISTORICAL_EXCEPTIONS)
  for doc,name,old in self.triples:
   for path in [doc,str(Path(doc).with_name('source-archive-map.json')),f'catalogue/source-snapshots/{old}/{name}',name]:self.copy(path)
  for key in ['manifest','decision']:self.copy(m.TEST_ACCEPTANCE[key])
  self.data={'identity':'controlled-time-current-source-amendment-v1','historical_exceptions':[list(x) for x in self.triples],'current_sources':self.current,'files':[{'path':n,'sha256':s} for n,s in self.current.items()]}
  self.write(m.AMENDMENT,self.data)
 def copy(self,name):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
 def write(self,name,data):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data))
 def pin(self,triple=None):
  d,n,s=triple or self.triples[0];return d,{'path':n,'sha256':s}
 def test_exact_two_historical_source_checks(self):
  for t in self.triples:m.verify_pin(*self.pin(t),self.current)
  self.assertEqual(m.amendment_sources()['current_sources'],self.current)
 def test_missing_old_archive(self):
  d,n,s=self.triples[0];(self.root/f'catalogue/source-snapshots/{s}/{n}').unlink()
  with self.assertRaises(ValueError):m.verify_pin(*self.pin(),self.current)
 def test_corrupt_old_archive(self):
  d,n,s=self.triples[0];(self.root/f'catalogue/source-snapshots/{s}/{n}').write_bytes(b'corrupt')
  with self.assertRaises(ValueError):m.verify_pin(*self.pin(),self.current)
 def test_unbound_old_archive(self):
  d,n,s=self.triples[0];p=self.root/Path(d).with_name('source-archive-map.json');data=json.loads(p.read_text());data['entries']=[e for e in data['entries'] if not(e['original_path']==n and e['sha256']==s)];p.write_text(json.dumps(data))
  with self.assertRaises(ValueError):m.verify_pin(*self.pin(),self.current)
 def test_current_test_changed(self):
  (self.root/'tests/test_controlled_time.py').write_bytes(b'changed')
  with self.assertRaises(AssertionError):m.amendment_sources()
 def test_current_collector_changed(self):
  (self.root/'tools/check_controlled_time_ci.py').write_bytes(b'changed')
  with self.assertRaises(AssertionError):m.amendment_sources()
 def test_unknown_exception_rejected(self):
  self.data['historical_exceptions'].append(['x','atlas/compiler.py','0'*64]);self.write(m.AMENDMENT,self.data)
  with self.assertRaises(AssertionError):m.amendment_sources()
 def test_unknown_current_source_rejected(self):
  self.data['current_sources']['atlas/compiler.py']='0'*64;self.write(m.AMENDMENT,self.data)
  with self.assertRaises(AssertionError):m.amendment_sources()
 def test_runtime_archive_does_not_permit_stale_current(self):
  name='atlas/controlled_time.py';self.copy(name);expected=m.sha(self.root/name)
  p=self.root/f'catalogue/source-snapshots/{expected}/{name}';p.parent.mkdir(parents=True);p.write_bytes((self.root/name).read_bytes())
  (self.root/name).write_bytes(b'changed runtime')
  self.assertEqual(m.sha(p),expected)
  with self.assertRaises(AssertionError):m.verify_pin('runtime-receipt.json',{'path':name,'sha256':expected},self.current)
 def test_same_path_wrong_original_document_not_exempt(self):
  with self.assertRaises(AssertionError):m.verify_pin('unbound.json',self.pin()[1],self.current)
 def test_missing_new_independent_decision_rejects(self):
  with self.assertRaises(FileNotFoundError):m.accepted_decision(m.AMENDMENT_REVIEW,m.AMENDMENT,m.sha(self.root/m.AMENDMENT))
 def test_real_prior_decision_cannot_accept_new_manifest(self):
  # Copy an actual accepted prior decision, never fabricate an author acceptance.
  self.copy(m.TEST_ACCEPTANCE['decision']);p=self.root/m.AMENDMENT_REVIEW;p.parent.mkdir(parents=True);p.write_bytes((ROOT/m.TEST_ACCEPTANCE['decision']).read_bytes())
  with self.assertRaises(AssertionError):m.accepted_decision(m.AMENDMENT_REVIEW,m.AMENDMENT,m.sha(self.root/m.AMENDMENT))
 def test_prior_accepted_test_decision_tamper_rejects(self):
  (self.root/m.TEST_ACCEPTANCE['decision']).write_bytes(b'changed')
  with self.assertRaises(AssertionError):m.amendment_sources()
 def test_portable_plan_stays_direct(self):
  name='docs/ingestion/vibe-2026/controlled-time-ci-v1/plan-v3.json';self.copy(name);expected=m.sha(self.root/name);(self.root/name).write_bytes(b'changed')
  with self.assertRaises(AssertionError):m.verify_pin('original-source-freeze',{'path':name,'sha256':expected},self.current)
if __name__=='__main__':unittest.main(verbosity=2)
