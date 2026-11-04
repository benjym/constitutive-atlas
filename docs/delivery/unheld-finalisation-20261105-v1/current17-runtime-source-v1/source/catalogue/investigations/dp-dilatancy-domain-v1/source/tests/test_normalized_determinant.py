"""Independent frozen references and corruption detection for the determinant core."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import unittest
from atlas.numerics.normalized_determinant import normalized_determinant
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'catalogue/investigations/normalized-determinant-v1'
spec=importlib.util.spec_from_file_location('normalized_determinant_assessor',HERE/'assess.py')
assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
CASES=json.loads((HERE/'protocol.json').read_text())['cases']
def bits(x):return struct.pack('>d',x).hex()
def response(c):
 e=c['primal_expectation']
 return {'id':c['id'],'version':assessor.VERSION,'inputs_unchanged':True,'double_ok':e['ok'],
 'double_bits':assessor.hex_bits(e['hex'])if e['ok']else bits(-123.5),
 'double_unchanged':not e['ok'],'jet_ok':c['expectation']['ok'],
 'jet_unchanged':not c['expectation']['ok'],'jet_bits':assessor.expected_jet(c)}
class DeterminantReferences(unittest.TestCase):
 def test_all_frozen_primal_references(self):
  for c in CASES:
   with self.subTest(case=c['id']):
    e=c['primal_expectation'];values=[float(v)for v in c['values']]
    if e['ok']:self.assertEqual(bits(normalized_determinant(values)),assessor.hex_bits(e['hex']))
    else:
     with self.assertRaises(ValueError):normalized_determinant(values)
 def test_invalid_type_and_shape(self):
  for values in ([1]*5,[1]*7,[True,1,1,0,0,0],['1',1,1,0,0,0],[10**10000,1,1,0,0,0]):
   with self.subTest(kind=type(values[0]).__name__,length=len(values)):
    with self.assertRaises(ValueError):normalized_determinant(values)
 def test_assessor_accepts_reference_frames(self):
  for c in CASES:assessor.check_row(response(c),c)
 def test_assessor_rejects_corrupted_components(self):
  c=next(c for c in CASES if c['expectation']['ok'])
  for component in range(39):
   row=response(c);row['jet_bits'][component]=format(int(row['jet_bits'][component],16)^1,'016x')
   with self.subTest(component=component):
    with self.assertRaises(AssertionError):assessor.check_row(row,c)
 def test_assessor_rejects_failure_output_mutation(self):
  c=next(c for c in CASES if not c['expectation']['ok'])
  for field in ('jet_unchanged','jet_ok','double_ok','inputs_unchanged'):
   row=response(c);row[field]=not row[field]
   with self.subTest(field=field):
    with self.assertRaises(AssertionError):assessor.check_row(row,c)
  row=response(c);row['jet_bits'][38]=bits(0.)
  with self.assertRaises(AssertionError):assessor.check_row(row,c)
 def test_assessor_rejects_negative_zero(self):
  c=next(c for c in CASES if c['expectation']['ok'] and '0000000000000000'in assessor.expected_jet(c))
  row=response(c);column=row['jet_bits'].index('0000000000000000');row['jet_bits'][column]='8000000000000000'
  with self.assertRaises(AssertionError):assessor.check_row(row,c)
 def test_assessor_rejects_extra_fields_and_status_types(self):
  c=CASES[0]
  for mutate in (lambda r:r.update(exception='hidden'),lambda r:r.update(jet_ok=1),lambda r:r.update(double_ok=1)):
   row=response(c);mutate(row)
   with self.assertRaises(AssertionError):assessor.check_row(row,c)
class FrozenSelection(unittest.TestCase):
 def test_caches_are_excluded(self):
  spec=importlib.util.spec_from_file_location('ratio_freeze',HERE/'freeze.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  import tempfile
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)
   for name in ('script.py','reference.json','source.hpp','__pycache__/script.pyc','__pycache__/source.py','.cache/source.py','script.pyc','.git/config.json'):
    path=p/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('fixture')
   self.assertEqual({str(x.relative_to(p))for x in module.selected(p)},{'script.py','reference.json','source.hpp'})
 def test_literal_protocol_and_recovery_assembly(self):
  spec=importlib.util.spec_from_file_location('ratio_freeze',HERE/'freeze.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  protocol=json.loads((HERE/'protocol.json').read_text());self.assertEqual(protocol,module.protocol());self.assertEqual((HERE/'requests.tsv').read_text(),module.request_text(protocol))
  self.assertFalse(any('__pycache__'in p or p.endswith('.pyc')for p in json.loads((HERE/'prospective-freeze.json').read_text())['files']))
if __name__=='__main__':unittest.main()
