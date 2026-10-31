"""State/transport boundary checks; native tests exercise the actual AD solve."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from atlas.dsl import ValidationError
from atlas.model import ROOT, MAX_STATE_COMPONENTS, load, validate
from atlas.schedule import validate_schedule
from atlas.compiler import generate

class CapacityTests(unittest.TestCase):
    def test_generated_catalogue_rejects_inadequate_ad_storage(self):
        compiler=shutil.which('c++')
        if not compiler:self.skipTest('C++ compiler unavailable')
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            generate(base/'generated',[ROOT/'tests/fixtures/time/capacity-32.json'])
            include=base/'include/atlas';include.mkdir(parents=True)
            for name in ('expm.hpp', 'checked_trace.hpp', 'checked_expression.hpp', 'trace_accuracy.hpp'):
                shutil.copyfile(ROOT/'cpp/include/atlas'/name, include/name)
            (base/'check.cpp').write_text('#include "models.hpp"\n')
            original=(ROOT/'cpp/include/atlas/tensor.hpp').read_text()
            for header in (original.replace('max_state = 32','max_state = 24'),
                           original.replace('max_state + 6','max_state')):
                (include/'tensor.hpp').write_text(header)
                result=subprocess.run([compiler,'-std=c++20','-fsyntax-only','-I'+str(base/'include'),
                                       '-I'+str(base/'generated'),str(base/'check.cpp')],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('Generated catalogue exceeds engine state/control derivative capacity',result.stderr)
    def test_definition_boundary_and_transport(self):
        model=load(ROOT/'tests/fixtures/time/capacity-32.json')
        initial=[v for f in model['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
        self.assertEqual(len(initial),MAX_STATE_COMPONENTS)
        bad=copy.deepcopy(model)
        bad['state'].append(dict(name='overflow',shape='scalar',unit='1',scale='1',initial=0))
        bad['equations']['overflow']='0 / tau'
        with self.assertRaisesRegex(ValidationError,'at most 32'):validate(bad)
        spec=dict(schema_version='0.2',units='SI',model=model['id'],start_time=0,initial=initial,
                  segments=[dict(id='hold',duration=2,samples=4,controls=[dict(quantity='stress',kind='hold') for _ in range(6)])],
                  solver=dict(method='backward-euler-step-doubling'))
        validate_schedule(spec)
        spec['initial'].append(0)
        with self.assertRaises(ValidationError):validate_schedule(spec)

    def test_legacy_26_component_multiplier_layout(self):
        model=load(ROOT/'models/linear-elastic.json')
        model.update(integration='residual',derived=[],domain=[])
        model['state']=model['state'][:1]
        for name in ('alpha','fabric','alpha_in'):
            model['state'].append(dict(name=name,unit='1',shape='sym',initial=[0]*6,scale='1'))
        model['state'].append(dict(name='e',unit='1',shape='scalar',initial=.7,scale='1'))
        model['state'].append(dict(name='gamma',unit='1',shape='scalar',initial=0,scale='1',transient=True,multiplier=True))
        model['equations']={'sigma':'sigma - sigma_n',**{n:f'{n} - {n}_n' for n in ('alpha','fabric','alpha_in','e')},'gamma':'gamma'}
        validate(model) # Capacity only: this is deliberately not SANISAND.
