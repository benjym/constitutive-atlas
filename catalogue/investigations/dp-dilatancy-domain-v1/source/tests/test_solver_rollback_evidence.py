"""Retained double solver transactions, not a constitutive benchmark."""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'catalogue/investigations/solver-rollback-v1'
REVIEW=ROOT/'docs/reviews/solver-rollback-design-v1'
spec=importlib.util.spec_from_file_location('rollback_assessor',STUDY/'assess.py')
ASSESSOR=importlib.util.module_from_spec(spec);spec.loader.exec_module(ASSESSOR)

class SolverRollbackEvidence(unittest.TestCase):
    def test_complete_frozen_inputs_and_original_design(self):
        for name,pin in json.loads((STUDY/'manifest.json').read_text()).items():
            self.assertEqual(hashlib.sha256((STUDY/name).read_bytes()).hexdigest(),pin,name)
        self.assertEqual((STUDY/'expected.json').read_bytes(),(REVIEW/'expected.json').read_bytes())
        expected=json.loads((STUDY/'expected.json').read_text())
        self.assertEqual(len(expected['rows']),11)
        self.assertEqual(len(expected['preparation']),3)
        for p in (STUDY/'models').glob('*.json'):
            model=json.loads(p.read_text())
            self.assertEqual(model['schema_version'],'0.3')
            self.assertNotIn('integration',model)
            self.assertIn('inputs',model['formulation'])

    def test_retained_backend_rows_bits_and_full_parity(self):
        saved=json.loads((STUDY/'assessment.json').read_text())
        for backend in ('native','wasm'):
            result=ASSESSOR.assess(STUDY/backend/'observe.stdout.txt')
            self.assertTrue(result['passed'])
            self.assertEqual(result,saved[backend])
            receipt=json.loads((STUDY/backend/'receipt.json').read_text())
            self.assertEqual([c['exit_code']for c in receipt['commands']],[0,0,0])
        self.assertEqual(ASSESSOR.load(STUDY/'native/observe.stdout.txt'),ASSESSOR.load(STUDY/'wasm/observe.stdout.txt'))
        self.assertTrue(saved['complete_raw_parity'])

    def test_missing_duplicate_wrong_state_clock_type_extra_reject(self):
        for mutation in ('missing','duplicate','state','clock','numeric-bool','extra'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory()as temp:
                raw=ASSESSOR.load(STUDY/'native/observe.stdout.txt')
                if mutation=='missing':raw['rows'].pop()
                elif mutation=='duplicate':raw['rows'].append(raw['rows'][0])
                elif mutation=='state':raw['rows'][0]['state_bits'][6]=ASSESSOR.bits(11)
                elif mutation=='clock':raw['rows'][5]['time_bits']=ASSESSOR.bits(3)
                elif mutation=='numeric-bool':raw['rows'][0]['ok']=0
                else:raw['preparation'][0]['extra']=True
                p=Path(temp)/'mutated.json';p.write_text(json.dumps(raw))
                self.assertFalse(ASSESSOR.assess(p)['passed'])

    def test_duplicate_wire_key_rejects(self):
        with tempfile.TemporaryDirectory()as temp:
            p=Path(temp)/'duplicate.json';p.write_text('{"version":"x","version":"y"}')
            with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
                ASSESSOR.assess(p)

    def test_frozen_python_regenerates_exact_header(self):
        # A fresh isolated interpreter imports only the retained generator/schema
        # tree. Current imports cannot reinterpret historical fixture bytes.
        code="""import sys, pathlib, hashlib
frozen=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(frozen))
import atlas.compiler
assert pathlib.Path(atlas.compiler.__file__).resolve().is_relative_to(frozen)
from atlas.compiler import generate
study=pathlib.Path(sys.argv[2]);output=pathlib.Path(sys.argv[3])
generate(output,sorted((study/'models').glob('*.json')))
print(hashlib.sha256((output/'models.hpp').read_bytes()).hexdigest())
"""
        with tempfile.TemporaryDirectory()as temp:
            env={k:v for k,v in os.environ.items()if not k.startswith(('PYTHON','ATLAS'))}
            result=subprocess.run([sys.executable,'-I','-S','-B','-c',code,str(STUDY/'frozen'),str(STUDY),temp],
                                  env=env,cwd=temp,text=True,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stderr,'')
            self.assertEqual(result.stdout.strip(),hashlib.sha256((STUDY/'generated/models.hpp').read_bytes()).hexdigest())
