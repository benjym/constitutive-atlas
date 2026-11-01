"""Pure Python investigation, exact equality and strict mutation sensitivity."""
import copy
import decimal
import hashlib
import json
import unittest
from portable_generation import ROOT,make_with_arithmetic

REQUESTS=ROOT/'docs/ingestion/ramberg-osgood-ansys242/execution-v1/requests.json'
FROZEN_SHA='859518b4f1896f2c431992a8cbd98b5f79d1ff9ca7de1f7971b9858960d61aa3'

def decimal_power(base,exponent):
    with decimal.localcontext() as context:
        context.prec=100
        return float(decimal.Decimal(base)**decimal.Decimal(exponent))

class ProposedArithmeticTests(unittest.TestCase):
    def setUp(self):self.frozen=json.loads(REQUESTS.read_text())
    def test_original_review_bound_freeze_exact(self):
        self.assertEqual(hashlib.sha256(REQUESTS.read_bytes()).hexdigest(),FROZEN_SHA)
    def test_complete_exact_regeneration(self):
        self.assertEqual(self.frozen,make_with_arithmetic())
    def test_complete_exact_regeneration_with_independent_other_powers(self):
        # Remaining powers evaluated by100digit decimal; no libm pow dependency.
        self.assertEqual(self.frozen,make_with_arithmetic(other_power=decimal_power))
    def test_correctly_rounded_pow_probe_reproduces_ci_first_difference(self):
        probe=make_with_arithmetic(half_integer=False,other_power=decimal_power)
        self.assertNotEqual(self.frozen,probe)
        self.assertEqual(probe['cases'][22]['id'],'n2.5-uniaxial')
        self.assertEqual(probe['cases'][22]['increments'][0][:3],[0.004999999999999999,-0.0016666666666666666,-0.0016666666666666666])
    def test_input_control_and_oracle_mutations_reject(self):
        for field in ['parameters','increments','expected_states','settings']:
            actual=make_with_arithmetic();case=actual['cases'][2]
            if field=='parameters':case[field]['E']+=1
            elif field=='settings':case[field][0]*=2
            else:case[field][0][0]+=1e-6
            with self.subTest(field=field):self.assertNotEqual(self.frozen,actual)
    def test_fixed_primitive_is_exact_at_ci_argument(self):
        import math
        x=float.fromhex('0x1.fffffffffffffp-1')
        self.assertEqual((x*math.sqrt(x)).hex(),'0x1.ffffffffffffep-1')
        self.assertEqual(decimal_power(x,1.5).hex(),'0x1.fffffffffffffp-1')

if __name__=='__main__':unittest.main(verbosity=2)
