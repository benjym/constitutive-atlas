"""Pure negative witnesses for live-checker identity and binary64 fidelity."""
import importlib.util,math,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('live_check',Path(__file__).with_name('check_live_v2.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class StrictFidelity(unittest.TestCase):
 def test_boolean_number_rejected(self):
  for a,b in [(True,1),(False,0),(1,True),(0,False)]:self.assertFalse(c.equal(a,b))
 def test_binary64_zero_sign_preserved(self):
  self.assertFalse(c.equal(0.,-0.));self.assertTrue(c.equal(-0.,-0.))
 def test_js_numeric_type_matches(self):self.assertTrue(c.equal(1,1.0))
 def test_nonfinite_rejected(self):
  for x in [math.nan,math.inf,-math.inf]:self.assertFalse(c.equal(x,x))
 def test_nested_unknown_and_missing_fields_rejected(self):
  self.assertFalse(c.equal({'a':[0.,True]},{'a':[-0.,True]}));self.assertFalse(c.equal({'a':1},{'a':1,'b':0}));self.assertFalse(c.equal([1],[1,2]))
 def test_nonfinite_json_rejected(self):
  for s in ['NaN','Infinity','-Infinity','{"a":NaN}']:
   with self.subTest(s=s),self.assertRaises(ValueError):c.parse(s)
 def test_duplicate_json_rejected(self):
  with self.assertRaises(ValueError):c.parse('{"a":1,"a":2}')
 def test_root_directory_allowed(self):
  for name in ['.','./']:self.assertIsNone(c.member_name(name,True))
 def test_root_file_rejected(self):
  for name in ['.','./']:
   with self.subTest(name=name),self.assertRaises(AssertionError):c.member_name(name,False)
 def test_unsafe_archive_members_rejected(self):
  for name in ['', '../a','/a','a/../b','a\\b']:
   with self.subTest(name=name),self.assertRaises(AssertionError):c.member_name(name,False)
 def test_normalized_aliases_collide(self):self.assertEqual(c.member_name('a',False),c.member_name('./a',False))
 def test_strict_complete_payload_equal(self):
  self.assertTrue(c.equal({'p':[-0.,1.5,None,'-0',True]},{'p':[-0.,1.5,None,'-0',True]}))
if __name__=='__main__':unittest.main()
