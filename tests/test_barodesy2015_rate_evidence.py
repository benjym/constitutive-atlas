"""Retained negative instantaneous-rate study; no compiled execution in tests."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools import research_rate_observations as rates
from tools import research_rate_parity as compare

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'catalogue/investigations/barodesy2015-rates-v1'
spec=importlib.util.spec_from_file_location('barodesy_actual_layout',STUDY/'check_layout.py')
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)

class SandRateEvidence(unittest.TestCase):
 def test_retained_file_manifest_and_frozen_design(self):
  manifest=json.loads((STUDY/'results-manifest.json').read_text())
  for name,pin in manifest['files'].items():
   path=Path(name);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
   blob=(STUDY/path).read_bytes();self.assertEqual(hashlib.sha256(blob).hexdigest(),pin)
  freeze=json.loads((STUDY/'prospective-freeze.json').read_text())
  self.assertFalse(freeze['compiled_observations_at_freeze'])
  for name,pin in freeze['files'].items():self.assertEqual(rates.sha(STUDY/name),pin)
  protocol,_,_=rates.checked_protocol(STUDY/'protocol.json');self.assertEqual(len(protocol['cases']),70)
 def test_fresh_reaudit_retains_exact_same_failure_and_comparison(self):
  actual=compare.assess(STUDY/'protocol.json',tuple(STUDY/('native-'+name+'.json') for name in ('build','observation','observation.transport')),tuple(STUDY/('wasm-'+name+'.json') for name in ('build','observation','observation.transport')))
  self.assertEqual(actual,json.loads((STUDY/'comparison.json').read_text()))
  self.assertEqual(actual['outcome'],'failed');self.assertTrue(actual['parity']['passed']);self.assertFalse(actual['parity']['both_independent_assessments_passed'])
  for backend in ('native','wasm'):
   self.assertEqual(actual[backend],json.loads((STUDY/(backend+'-assessment.json')).read_text()))
   self.assertEqual(len(actual[backend]['failures']),1);self.assertEqual(actual[backend]['failures'][0]['case'],'valid:audit-trace-cancellation');self.assertEqual(actual[backend]['failures'][0]['component'],6)
 def test_lost_void_rate_is_an_exact_actual_input_witness(self):
  protocol=json.loads((STUDY/'protocol.json').read_text());case=next(c for c in protocol['cases']if c['id']=='valid:audit-trace-cancellation')
  strain=[float(x)for x in case['args'][3].split(',')];e=float(case['args'][2].split(',')[-1])
  exact=-(1+Fraction(e))*sum(map(Fraction,strain[:3]),Fraction())
  expected=float(exact);self.assertNotEqual(expected,0.);self.assertEqual(case['expectation']['values'][6],expected)
  self.assertEqual(case['expectation']['absolute_budgets'][6],4*__import__('math').ulp(expected))
  for backend in ('native','wasm'):
   assessment=json.loads((STUDY/(backend+'-assessment.json')).read_text());row=next(c for c in assessment['cases']if c['id']==case['id'])
   self.assertEqual(row['response']['values'][6],0.);self.assertGreater(abs(expected),case['expectation']['absolute_budgets'][6])
 def test_serial_build_commands_and_exact_generated_source_parity(self):
  for backend in ('native','wasm'):
   receipt=json.loads((STUDY/(backend+'-build.json')).read_text());self.assertTrue(receipt['all_commands_succeeded'])
   for entry in receipt['commands']:
    path=ROOT/entry['path'];self.assertEqual(rates.sha(path),entry['sha256']);command=json.loads(path.read_text());self.assertEqual(command['returncode'],0)
    if '--build'in command['argv']:self.assertEqual(command['argv'][-4:],['--target','atlas_isolated','--parallel','1'])
  for name in ('models.hpp','models.json'):self.assertEqual((STUDY/('native-generated-'+name)).read_bytes(),(STUDY/('wasm-generated-'+name)).read_bytes())
  failure=json.loads((STUDY/'native-build-attempt-0.json').read_text());self.assertEqual(failure['compiled_rate_calls'],0);self.assertTrue(failure['build_commands_succeeded'])
 def test_actual_layout_supplement_replays(self):self.assertEqual(layout.verify(),json.loads((STUDY/'layout-check.json').read_text()))
 def test_layout_supplement_rejects_reordered_or_duplicate_descriptors(self):
  for kind in ('order','duplicate'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as tmp:
    folder=Path(tmp)
    for name in ('protocol.json','native-observation.json','native-observation.transport.json','native-generated-models.json','wasm-observation.json','wasm-observation.transport.json','wasm-generated-models.json'):shutil.copyfile(STUDY/name,folder/name)
    raw=json.loads((folder/'native-observation.transport.json').read_text());lines=raw['stdout'].splitlines()
    if kind=='order':
     desc=json.loads(lines[0]);desc['models'][0]['parameters']=dict(reversed(list(desc['models'][0]['parameters'].items())));lines[0]=json.dumps(desc)
    else:lines[1]=lines[1].replace('"ok":true','"ok":false,"ok":true',1)
    raw['stdout']='\n'.join(lines)+'\n';(folder/'native-observation.transport.json').write_text(json.dumps(raw))
    obs=json.loads((folder/'native-observation.json').read_text());obs['transport_sha256']=rates.sha(folder/'native-observation.transport.json');(folder/'native-observation.json').write_text(json.dumps(obs))
    with patch.object(layout,'HERE',folder):
     with self.assertRaises(ValueError):layout.verify()

if __name__=='__main__':unittest.main()
