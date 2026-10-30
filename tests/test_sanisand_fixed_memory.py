"""Fixed-memory residual research checks; no compilation or native execution."""
import copy
import gzip
import json
import math
import unittest

from atlas.dsl import Sym
from atlas.model import all_models, interpret, load
from tools.inspect_sanisand_limit import load_fragment, evaluate_fragment
from tools.verify_sanisand_fixed_memory import MODEL, ROOT, verify


class FixedMemoryResearchTests(unittest.TestCase):
    def test_research_scope_and_capacity(self):
        model=load(ROOT/MODEL)
        self.assertEqual(sum(6 if f['shape']=='sym' else 1 for f in model['state']),26)
        self.assertNotIn(model['id'],[m['id'] for m in all_models()])
        self.assertEqual(model['status'],'draft')
        self.assertNotIn('increment_reset',model)
        self.assertEqual(model['equations']['alpha_in'],'alpha_in-alpha_in_n')

    def test_residual_matches_original_rates_to_first_order(self):
        model=load(ROOT/MODEL);fragment=load_fragment()
        for direction in ([2,-1,-1,0,0,0],[-2,1,1,0,0,0],[.4,-.1,-.3,.7,-.2,.1]):
            length=math.sqrt(sum(v*v for v in direction));n=[v/length for v in direction]
            radius=math.sqrt(2/3)*.01
            sigma=Sym(tuple(1e5*(.3*n[i]+radius*n[i]+(1 if i<3 else 0)) for i in range(6)))
            alpha=Sym(tuple(.3*v for v in n));fabric=Sym(tuple(-.2*v for v in n));zero=Sym((0.,)*6)
            previous=dict(sigma=list(sigma.v),e=.7,alpha=list(alpha.v),fabric=list(fabric.v),alpha_in=list(zero.v),gamma=0)
            errors=[]
            for h in (1e-5,5e-6,2.5e-6):
                de=Sym(tuple(h*v for v in n))
                rate=evaluate_fragment(fragment,sigma=sigma,e=.7,alpha=alpha,z=fabric,alpha_in=zero,d_epsilon=de)
                self.assertGreater(rate['plastic_multiplier'],0)
                current=dict(sigma=list((sigma+rate['stress_increment']).v),e=.7+rate['void_ratio_increment'],
                             alpha=list((alpha+rate['backstress_increment']).v),fabric=list((fabric+rate['fabric_increment']).v),
                             alpha_in=list(zero.v),gamma=rate['multiplier_times_h'])
                residual=interpret(model,current,previous,de.v)
                errors.append(max(abs(x)/(1e5 if name=='sigma' else 1) for name,value in residual.items()
                                  for x in (value.v if isinstance(value,Sym) else [value])))
            for a,b in zip(errors,errors[1:]):self.assertLess(b,a*.27)

    def test_zero_increment_elastic_interior(self):
        model=load(ROOT/MODEL)
        state={f['name']:f['initial'] for f in model['state']}
        result=interpret(model,state,state,[0]*6)
        for value in result.values():
            for component in (value.v if isinstance(value,Sym) else [value]):
                self.assertAlmostEqual(component,0,delta=1e-14)

    def test_retained_native_matrix_and_invalid_evidence(self):
        raw=ROOT/'catalogue/investigations/sanisand-fixed-memory-be-v1/trajectories.json.gz'
        rows=json.loads(gzip.decompress(raw.read_bytes()))
        result=verify(rows)
        self.assertEqual(result['increments'],336)
        with self.assertRaises(ValueError):verify(rows[:-1])
        changed=copy.deepcopy(rows);changed[0]['substeps']=2
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(rows);changed[0]['state'][19]=.01
        with self.assertRaises(ValueError):verify(changed)


if __name__=='__main__':unittest.main()
