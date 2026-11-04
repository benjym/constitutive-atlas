"""Existing-native callback identities, malformed echoes and serial full steps."""
import copy
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from atlas.dsl import ValidationError
from atlas.history_legacy import advance_legacy, make_legacy_snapshot
from atlas.history_native import native_integrator
from atlas.initialization import canonical_hash
from atlas.model import ROOT,defaults,load
from atlas.recorded import MATERIAL_DEFAULTS
from tests.test_history_legacy import fixture,named


class NativeCallbackTests(unittest.TestCase):
    def fake(self, directory, *, changed_order=False):
        model,state,parent=fixture()
        data={'schema_version':'0.1','models':[copy.deepcopy(model)]}
        data['sha256']=canonical_hash(data['models'])
        binary=Path(directory)/'solver';binary.write_bytes(b'fake fixture binary; never executed')
        catalogue=Path(directory)/'models.json';catalogue.write_text(json.dumps(data))
        flat=[v for f in model['state'] for v in (state[f['name']] if f['shape']=='sym' else [state[f['name']]])]
        response={'ok':True,'model':model['id'],'catalogue_hash':data['sha256'],
                  'parameters':list(defaults(model).values()),'initial':flat,'strain':[0.]*6,
                  'integration_settings':{'version':'incremental-settings-0.1','norm':'scaled_component_max',**MATERIAL_DEFAULTS},'state':flat,
                  'diagnostics':{'iterations':0,'substeps':0,'rejected':0,'increment_fractions':[]},'message':'ok'}
        described=copy.deepcopy(data)
        if changed_order:described['models'][0]['parameters']=dict(reversed(list(model['parameters'].items())))
        return model,state,parent,binary,catalogue,described,response

    def test_describe_and_complete_numeric_echo(self):
        with tempfile.TemporaryDirectory() as tmp:
            model,state,parent,binary,cat,description,response=self.fake(tmp)
            with patch('atlas.history_native.subprocess.run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps(description)),SimpleNamespace(returncode=0,stdout=json.dumps(response))]) as run:
                callback=native_integrator(binary,cat,dict(MATERIAL_DEFAULTS))
                result=advance_legacy(model,parent,[0.]*6,callback)
                self.assertTrue(result['ok']);self.assertEqual(named(result['snapshot']),state)
                self.assertEqual(run.call_count,2)
                self.assertEqual(run.call_args_list[0].args[0],[str(binary.resolve()),'--describe'])
                self.assertEqual(result['diagnostics']['native_runtime']['catalogue_sha256'],description['sha256'])

    def test_numeric_boolean_impostors_reject_and_roll_back(self):
        for key,mutate in [('strain',lambda r:r['strain'].__setitem__(0,False)),
                           ('initial',lambda r:r['initial'].__setitem__(-1,False)),
                           ('parameters',lambda r:r['parameters'].__setitem__(0,True)),
                           ('settings',lambda r:r['integration_settings'].update(max_depth=True)),
                           ('state',lambda r:r['state'].__setitem__(0,True)),
                           ('diagnostics',lambda r:r['diagnostics'].update(substeps=True))]:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as tmp:
                model,state,parent,binary,cat,description,response=self.fake(tmp);mutate(response)
                with patch('atlas.history_native.subprocess.run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps(description)),SimpleNamespace(returncode=0,stdout=json.dumps(response))]):
                    callback=native_integrator(binary,cat,dict(MATERIAL_DEFAULTS))
                    result=advance_legacy(model,parent,[0.]*6,callback)
                    self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent)

    def test_runtime_parameter_order_not_just_canonical_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            _,_,_,binary,cat,description,_=self.fake(tmp,changed_order=True)
            # Dict sorting makes these hashes equal; runtime order is separately checked.
            self.assertEqual(description['sha256'],canonical_hash(description['models']))
            with patch('atlas.history_native.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps(description))):
                with self.assertRaisesRegex(ValidationError,'parameter order'):
                    native_integrator(binary,cat,dict(MATERIAL_DEFAULTS))

    def test_binary_change_after_binding_rolls_back_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            model,_,parent,binary,cat,description,_=self.fake(tmp)
            with patch('atlas.history_native.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps(description))) as run:
                callback=native_integrator(binary,cat,dict(MATERIAL_DEFAULTS));binary.write_bytes(b'changed')
                result=advance_legacy(model,parent,[0.]*6,callback)
                self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent)
                self.assertEqual(run.call_count,1)

    def test_explicit_settings_are_closed_and_bounded(self):
        for settings in ({},dict(MATERIAL_DEFAULTS,extra=1),dict(MATERIAL_DEFAULTS,max_iterations=True),
                         dict(MATERIAL_DEFAULTS,rate_tolerance=math.inf),dict(MATERIAL_DEFAULTS,max_depth=21)):
            with self.assertRaises(ValidationError):native_integrator('/missing','/missing',settings)
        with self.assertRaises(ValidationError):native_integrator('/missing','/missing',dict(MATERIAL_DEFAULTS),timeout=10**1000)

    def test_existing_native_full_steps_serial(self):
        solver=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))
        catalogue=Path(os.environ.get('ATLAS_TIME_CATALOGUE',solver.parent/'time-generated/models.json'))
        if not solver.is_file() or not catalogue.is_file():self.skipTest('existing time-fixture solver/catalogue required; no build')
        callback=native_integrator(solver,catalogue,dict(MATERIAL_DEFAULTS))
        for suffix in ('reset','residual','reset-cutback'):
            model,state,parent=fixture(suffix)
            inc=[-1.,0,0,0,0,0] if suffix=='reset-cutback' else [-.5,0,0,0,0,0]
            result=advance_legacy(model,parent,inc,callback)
            self.assertTrue(result['ok'],result.get('message'))
            self.assertEqual(named(result['snapshot'])['anchor'],1.)
            expected=math.exp(-1) if suffix=='reset-cutback' else .5
            self.assertAlmostEqual(named(result['snapshot'])['coordinate'],expected,delta=2e-5)
            if suffix=='reset-cutback':self.assertGreater(result['diagnostics']['rejected'],0)
        model,state,_=fixture();parameters=dict(defaults(model),limit=1.1)
        parent=make_legacy_snapshot(model,state,parameters,[0.]*6)
        failure=advance_legacy(model,parent,[-3.,0,0,0,0,0],callback)
        self.assertFalse(failure['ok']);self.assertIs(failure['snapshot'],parent)
        self.assertGreater(failure['diagnostics']['substeps'],0)


if __name__=='__main__':unittest.main()
