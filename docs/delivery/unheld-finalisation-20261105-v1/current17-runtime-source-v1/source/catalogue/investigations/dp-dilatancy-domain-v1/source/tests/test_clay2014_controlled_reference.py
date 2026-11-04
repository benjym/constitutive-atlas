import ast
import copy
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path
import unittest

from tools import clay2014_controlled_reference as ref


class ControlledReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = ref.read(ref.ROOT/'catalogue/investigations/clay2014-controlled-resolution-v1/protocol-reference.json')
        cls.data = ref.inputs()

    def test_frozen_replay(self):
        ref.verify(self.document)
        self.assertEqual(self.document['actual_calls_per_backend'], 315)
        for field in self.document['policy']['claims'].values():
            self.assertIs(field, False)

    def test_exact_loading_and_endpoint_identity(self):
        base = ref.schedule(self.data, 1)
        for factor in ref.FACTORS:
            points = ref.schedule(self.data, factor)
            for i, original in enumerate(base):
                subset = points[i*factor:(i+1)*factor]
                for j in range(6):
                    self.assertEqual(sum((Fraction(p['increment'][j]) for p in subset), Fraction()), Fraction(original['increment'][j]))
                self.assertEqual(subset[-1]['cumulative_loading_exact'], original['cumulative_loading_exact'])
            endpoints = [p['target'] for p in next(g for g in self.document['groups'] if g['factor']==factor)['points'] if p['physical_endpoint']]
            baseline = [p['target'] for p in self.document['groups'][0]['points'] if p['physical_endpoint']]
            self.assertEqual(endpoints, baseline)

    def test_precision_refinement_and_exact_volume(self):
        for g in self.document['groups']:
            self.assertEqual(g['call_count'], 21*g['factor'])
            with localcontext() as ctx:
                ctx.prec = 140
                for p in g['points']:
                    num,den = p['cumulative_loading_exact'][0]
                    v = 3*Decimal(num)/Decimal(den)
                    expected = (1+Decimal.from_float(.65))*(-v).exp()-1
                    self.assertLessEqual(abs(expected-Decimal(p['decimal140'][1])), Decimal('1e-135'))
                    self.assertLess(p['reference_uncertainty']['stress'], 1e-7)
                    self.assertLess(p['reference_uncertainty']['e'], 1e-15)

    def test_matches_prior_independent_full_tensor_rk4(self):
        old = ref.read(ref.ROOT/'catalogue/investigations/clay2014-path-reference-v1/reference.json')
        row = next(c for c in old['cases'] if c['id']=='isotropic-ratios-hydro-reversal-n7')
        for a,b in zip(self.document['groups'][0]['points'], row['grids'][-1]['trajectory']):
            self.assertLess(abs(a['target'][0]-b['state'][0]), 1e-6)
            self.assertLess(abs(a['target'][6]-b['state'][6]), 1e-13)

    def test_scalar_solution_differential_identity(self):
        # Independently differentiate one tiny hydro increment in Decimal and
        # compare the explicit scalar source RHS, including compression/unload.
        import math
        data = copy.deepcopy(self.data)
        p=data['parameters']; pressure=data['initial'][0];e=data['initial'][6]
        af=math.sqrt(3)*(3-math.sin(p[2]))/(2*math.sqrt(2)*math.sin(p[2]))
        alpha=math.log((p[3]-p[4])/(p[3]+p[4])*(3+af*af)/(af*math.sqrt(3)))/math.log(2)
        pe=p[0]*math.exp((p[5]-math.log1p(e))/p[3])
        for sign in (-1,1):
            h=sign*1e-15
            data['base_increments']=[[h]*3+[0.]*3]
            result=ref.trajectory(data,1,140)[0]
            with localcontext() as ctx:
                ctx.prec=140
                derivative=float((result[0]-Decimal.from_float(pressure))/(3*Decimal.from_float(h)))
                void_derivative=float((result[1]-Decimal.from_float(e))/(3*Decimal.from_float(h)))
            expected=pressure/2*((1/p[3]+1/p[4])+(1/p[3]-1/p[4])*(pressure/pe)**alpha*sign)
            self.assertAlmostEqual(derivative/expected,1,places=11)
            self.assertAlmostEqual(void_derivative,-(1+e),places=12)

    def test_forged_policy_target_and_loading_rejected(self):
        for field in ('target','policy','loading','claim'):
            d=copy.deepcopy(self.document)
            if field=='target':d['groups'][0]['points'][0]['target'][0]+=1
            if field=='policy':d['policy']['endpoint_successor_error_factor']=.99
            if field=='loading':d['groups'][0]['points'][0]['increment'][0]*=2
            if field=='claim':d['policy']['claims']['scientific_admission']=True
            with self.assertRaises(ValueError):ref.verify(d)
        for factor in (True,0,3,16):
            with self.assertRaises(ValueError):ref.schedule(self.data,factor)

    def test_no_production_or_oracle_imports(self):
        tree=ast.parse(Path(ref.__file__).read_text())
        imported=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imported.extend(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom):imported.append(node.module)
        self.assertFalse(any(x.startswith(('atlas','tools','subprocess','ctypes')) for x in imported))


if __name__=='__main__':unittest.main()
