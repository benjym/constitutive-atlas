"""Exact proposal binding and rejection of unsupported changes or signatures."""
import copy
import importlib.util
import json
import unittest
from unittest.mock import patch
from atlas.model import ROOT
P=ROOT/'docs/reviews/tresca-v5-source-integration-v1'
spec=importlib.util.spec_from_file_location('tresca_source_review',P/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class TrescaSourceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.q=v.read(ROOT/'catalogue/investigations/tresca-certified-corners-v5/frozen/model.json')
        self.p=v.read(P/'public-model.json');self.r=v.read(P/'pending-review.json');self.d=v.read(P/'decision.json')
    def test_source_and_generated_identity_without_execution(self):
        with patch('subprocess.run',side_effect=AssertionError('no material execution')):
            self.assertTrue(v.verify()['overall_pass'])
    def test_constitutive_change_rejected(self):
        p=copy.deepcopy(self.p);p['equations']['sigma']='2*(sigma-returned)'
        with self.assertRaises((ValueError,KeyError)): v.check_contract(self.q,p,self.r,self.d)
    def test_false_signoff_and_definition_rebinding_rejected(self):
        for change in [{'status':'accepted','independent':True},{'reviewer':'unassigned'},{'model':{'id':self.p['id'],'definition_sha256':'0'*64}}]:
            with self.subTest(change=change):
                r=copy.deepcopy(self.r);r.update(change)
                with self.assertRaises(ValueError): v.check_contract(self.q,self.p,r,self.d)
    def test_unsupported_scientific_and_deployment_decisions_rejected(self):
        for key in ('scientific_admission','experimental_validation','deployment_authorized'):
            d=copy.deepcopy(self.d);d[key]=True
            with self.subTest(key=key), self.assertRaises(ValueError): v.check_contract(self.q,self.p,self.r,d)
