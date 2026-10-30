"""Research parent-direction reset; retained native evidence, no compilation."""
import copy
import gzip
import json
import math
import unittest

from atlas.model import all_models, load, prepare_increment
from tools.verify_sanisand_parent_reset import MODEL, FIXED, RAW, ROOT, verify, unpack


def rows():return json.loads(gzip.decompress((ROOT/RAW).read_bytes()))


class SANISANDParentResetTests(unittest.TestCase):
    def test_variant_identity_and_unchanged_continuous_definition(self):
        model=load(ROOT/MODEL);fixed=load(ROOT/FIXED)
        for key in ('parameters','state','derived','equations','domain','initial_checks'):
            self.assertEqual(model[key],fixed[key])
        self.assertNotIn(model['id'],[m['id'] for m in all_models()])
        self.assertEqual(model['increment_reset']['scope'],'parent_increment')
        self.assertEqual(model['increment_reset']['updates'],[
            dict(target='alpha_in',guard='dot(alpha-alpha_in, dev(de))',value='alpha')])

    def test_strict_guard_and_immutable_parent(self):
        model=load(ROOT/MODEL)
        peak=next(r for r in rows() if (r['path'],r['steps'],r['leg'],r['step'])==(0,16,0,15))
        parent=unpack(model,peak['state']);saved=copy.deepcopy(parent)
        reverse=[-x for x in peak['increment']]
        prepared=prepare_increment(model,parent,reverse)
        self.assertEqual(prepared['alpha_in'],parent['alpha'])
        self.assertNotEqual(prepared['alpha_in'],parent['alpha_in'])
        for increment in ([0]*6,peak['increment'],[0,0,0,1e-5,0,0]):
            other=prepare_increment(model,parent,increment)
            self.assertEqual(other['alpha_in'],parent['alpha_in'])
        self.assertEqual(parent,saved)
        prepared['alpha_in'][0]+=1
        self.assertEqual(parent,saved)

    def test_source_cone_guard_is_not_parent_trial_guard(self):
        model=load(ROOT/MODEL)
        peak=next(r for r in rows() if (r['path'],r['steps'],r['leg'],r['step'])==(0,16,0,15))
        state=unpack(model,peak['state']);p=sum(state['sigma'][:3])/3
        delta=[state['sigma'][i]/p-(1 if i<3 else 0)-state['alpha'][i] for i in range(6)]
        length=math.sqrt(sum(v*v for v in delta));normal=[v/length for v in delta]
        memory=[a-b for a,b in zip(state['alpha'],state['alpha_in'])]
        source_guard=sum(a*b for a,b in zip(memory,normal))
        parent_guard=-sum(a*b for a,b in zip(memory,peak['increment']))
        self.assertGreater(source_guard,0)
        self.assertLess(parent_guard,0)
        # This establishes different local decisions, not a replacement for
        # the source's complete loading-process/event rules.

    def test_retained_native_cycles_resets_and_refinement(self):
        report=verify(rows())
        self.assertEqual(report['cyclic_increments'],896)
        self.assertEqual(report['cyclic_memory_resets'],18)
        self.assertEqual(report['rollback_after_reset'],6)
        self.assertEqual(report['monotonic_parity_checks'],224)

    def test_corrupt_preparation_rollback_and_partition_are_rejected(self):
        original=rows()
        altered=copy.deepcopy(original);altered[0]['prepared'][19]+=.01
        with self.assertRaises(ValueError):verify(altered)
        altered=copy.deepcopy(original);i=next(i for i,r in enumerate(altered) if r['leg']==4)
        altered[i]['state']=altered[i]['prepared'][:]
        with self.assertRaises(ValueError):verify(altered)
        altered=copy.deepcopy(original);altered[0]['fractions']=[.5,.5]
        with self.assertRaises(ValueError):verify(altered)
        with self.assertRaises(ValueError):verify(original[:-1])


if __name__=='__main__':unittest.main()
