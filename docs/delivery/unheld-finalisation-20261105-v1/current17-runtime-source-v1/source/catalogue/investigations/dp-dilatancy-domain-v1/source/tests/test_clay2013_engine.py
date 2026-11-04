"""Isolated clay research engine: source rates, transactional failures and evidence."""
import hashlib
import copy
import json
import math
import os
from pathlib import Path
import random
import unittest

from atlas.evidence import checked_receipt
from atlas.dsl import Sym
from atlas.model import ROOT, load
from tools.clay2013_integration_study import MODEL_PATH, native_call, request, assess
from tools.reference_clay2013_cartesian import rate

SOLVER=Path(os.environ.get('ATLAS_CLAY2013_SOLVER',ROOT/'build/atlas_clay2013_solver'))

class ResearchDefinition(unittest.TestCase):
    def test_catalogue_isolation_and_source_links(self):
        m=load(MODEL_PATH)
        self.assertEqual(m['status'],'draft')
        self.assertEqual(sum(6 if x['shape']=='sym' else 1 for x in m['state']),7)
        self.assertEqual(m['parameters']['p_ref']['min'],1000)
        self.assertEqual(m['parameters']['p_ref']['max'],1000)
        self.assertTrue(any('doi.org/10.1007/s11440-012-0199-y' in x['url'] for x in m['sources']))
        for folder in (ROOT/'models',ROOT/'models/research'):
            self.assertNotIn(m['id'],[load(p)['id'] for p in folder.glob('*.json')])

@unittest.skipUnless(SOLVER.is_file(),'isolated clay native solver not built')
class NativeEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=load(MODEL_PATH)
    def call(self,z,d,tol=1e-8,budget=20000,mode='integrate'):
        return native_call(SOLVER,request(self.model,z,d,tol,budget),mode)
    def test_noncoaxial_rates_against_independent_cartesian(self):
        rng=random.Random(2013);r2=math.sqrt(2)
        params={k:self.model['parameters'][k]['default'] for k in ('phi_c','lambda_star','kappa_star','N','nu')}
        for _ in range(8):
            b=[[rng.uniform(-.4,.4) for _ in range(3)] for _ in range(3)]
            s=[[1e4*(sum(b[i][k]*b[j][k] for k in range(3))+(i==j)) for j in range(3)] for i in range(3)]
            z=[s[0][0],s[1][1],s[2][2],r2*s[0][1],r2*s[1][2],r2*s[0][2],.8]
            d=[rng.uniform(-.002,.002) for _ in range(6)]
            cart=[[d[0],d[3]/r2,d[5]/r2],[d[3]/r2,d[1],d[4]/r2],[d[5]/r2,d[4]/r2,d[2]]]
            ref=rate(s,cart,.8,**params);q=ref['stress_rate']
            target=[q[0][0],q[1][1],q[2][2],r2*q[0][1],r2*q[1][2],r2*q[0][2],ref['e_rate']]
            actual=self.call(z,d,mode='evaluate');self.assertTrue(actual['ok'],actual)
            for x,y in zip(actual['values'],target,strict=True):self.assertAlmostEqual(x,y,delta=2e-10*max(1,abs(y)))
    def test_zero_increment_and_domain_rejections(self):
        z=[10000.]*3+[0.]*3+[.8];original=copy.deepcopy(z)
        self.assertEqual(self.call(z,[0.]*6)['state'],z)
        invalid=[[0.]*6+[.8],[10000.]*3+[0.]*3+[-.1],[10000.,-100.,-100.,0.,0.,0.,.8],[1.,1.,1.,1e-300,0.,0.,.8]]
        for state in invalid:
            a=self.call(state,[0.]*6);self.assertFalse(a['ok']);self.assertEqual(a['state'],state)
        self.assertEqual(z,original)
    def test_domain_and_budget_rollback(self):
        z=[10000.]*3+[0.]*3+[.1]
        a=self.call(z,[.2/3]*3+[0.]*3,budget=256)
        self.assertFalse(a['ok']);self.assertEqual(a['state'],z)
        self.assertGreater(a['diagnostics']['substeps'],0)
        self.assertIn('rolled back',a['message'])
        z=[10000.]*3+[0.]*3+[.8];d=[.01]*3+[0.]*3
        good=self.call(z,d);bad=self.call(z,d,budget=3)
        self.assertTrue(good['ok']);self.assertFalse(bad['ok']);self.assertEqual(bad['state'],z)
        self.assertGreater(bad['diagnostics']['substeps'],0)
        self.assertEqual(self.call(z,[.0001]*3+[0.]*3),self.call(list(z),[.0001]*3+[0.]*3))

class RetainedEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=ROOT/'catalogue/investigations/clay2013-integration-v1'
        cls.model=load(MODEL_PATH)
        cls.native=json.loads((cls.folder/'native.json').read_text())
        cls.wasm=json.loads((cls.folder/'wasm.json').read_text())
    def test_exact_reference_native_and_wasm_matrices(self):
        for report in (self.native,self.wasm):
            summary=assess(report['records'],self.model)
            self.assertEqual(len(summary),33)
            self.assertEqual(sum(x['calls'] for x in summary),115)
        self.assertLessEqual(self.wasm['maximum_scaled_native_parity'],2e-10)
        self.assertEqual(self.wasm['native_report_sha256'],hashlib.sha256((self.folder/'native.json').read_bytes()).hexdigest())
    def test_assessment_rejects_missing_duplicate_corrupt_or_misidentified_runs(self):
        for change in ('missing','duplicate','strain','state','settings','catalogue'):
            records=copy.deepcopy(self.native['records'])
            if change=='missing':records.pop()
            elif change=='duplicate':records.append(copy.deepcopy(records[0]))
            elif change=='strain':records[0]['calls'][0]['request']['strain'][0]+=.001
            elif change=='state':records[0]['calls'][-1]['response']['state'][0]*=2
            elif change=='settings':records[0]['calls'][0]['response']['integration_settings']['rate_tolerance']=.1
            elif change=='catalogue':records[0]['calls'][0]['response']['catalogue_hash']='0'*64
            with self.subTest(change=change),self.assertRaises(ValueError):assess(records,self.model)
    def test_manifest_and_analytic_fixture_integrity(self):
        from tools.clay2013_isotropic_reference import generate,encode
        generated=json.loads(json.dumps(generate(),default=encode))
        self.assertEqual(generated,json.loads((self.folder/'isotropic-reference.json').read_text()))
        for folder in (self.folder,ROOT/'catalogue/investigations/clay2013-initialization-v1'):
            manifest=json.loads((folder/'manifest.json').read_text())
            for name,digest in (manifest.get('dependencies',{})|manifest['files']).items():
                checked_receipt(ROOT, (folder/'manifest.json').relative_to(ROOT).as_posix(), name, digest)
        self.assertFalse(json.loads((self.folder/'manifest.json').read_text())['complete_model'])

if __name__=='__main__':unittest.main()

