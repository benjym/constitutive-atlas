"""Scientific annotation controls that do not assume stored 3D stress."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'paper'))
from atlas.model import load, interpret, observe
from atlas.dsl import Sym
from analysis.terracotta_normalization import invariant_coefficients, rescale
from analysis.annotations import validate_model_annotations
from analysis.common import read_json


class NormalizationAudit(unittest.TestCase):
    def test_changed_original_source_evidence_requires_annotation_review(self):
        annotations=read_json(ROOT/'paper/study/model_annotations.json')
        model=next(m for m in annotations['models'] if m['model_id']=='hypoplastic-sand-igs97')
        pins=model['source_reconciliation']['inputs_sha256']
        pins[next(iter(pins))]='0'*64
        with self.assertRaisesRegex(ValueError,'source reconciliation input changed'):
            validate_model_annotations(annotations)

    def test_scope_counts_do_not_invent_a_stored_stress_or_full_3d_state(self):
        annotations=read_json(ROOT/'paper/study/model_annotations.json')
        records=validate_model_annotations(annotations)
        model=next(m for m in records if m['model_id']=='terracotta-2024-fig1')
        self.assertEqual(model['component_count_scope']['stored_stress_components'],0)
        self.assertEqual(model['component_count_scope']['persistent_internal_components'],4)
        self.assertIsNone(model['counts']['stress_components_3d'])
        self.assertIsNone(model['independent_material_dimension']['value'])
        model['counts']['stress_components_3d']=0
        with self.assertRaisesRegex(ValueError,'unsupported 3D'):
            validate_model_annotations(annotations)

    def test_supported_count_must_match_actual_state_roles(self):
        annotations=read_json(ROOT/'paper/study/model_annotations.json')
        model=next(m for m in annotations['models'] if m['model_id']=='terracotta-2024-fig1')
        model['component_count_scope']['persistent_internal_components']=6
        with self.assertRaisesRegex(ValueError,'supported-scope'):
            validate_model_annotations(annotations)

    def test_positive_temperature_reparameterization_preserves_rhs_and_stress(self):
        model=load(ROOT/'models/research/terracotta-2024-fig1.json')
        parameters={name:value['default'] for name,value in model['parameters'].items()}
        for state in [dict(ev_e=.05,es_e=.005,Tm=.002,phi=.423),
                      dict(ev_e=.06,es_e=-.003,Tm=.001,phi=.45)]:
            for rate in [[2e-5,-1e-5,-1e-5,0,0,0],[-1e-5]*3+[0,0,0],[0]*6]:
                original_rhs=interpret(model,state,None,rate,parameters,time=3.)
                original_outputs=observe(model,state,rate,parameters,time=3.)
                for factor in [.1,2.,10.]:
                    p,z=rescale(parameters,state,factor)
                    rhs=interpret(model,z,None,rate,p,time=3.)
                    output=observe(model,z,rate,p,time=3.)
                    for name,value in original_rhs.items():
                        expected=value*factor if name=='Tm' else value
                        self.assertAlmostEqual(rhs[name],expected,delta=max(1e-15,abs(expected)*1e-12))
                    for name,value in original_outputs.items():
                        a,b=(value.v,output[name].v) if isinstance(value,Sym) else ([value],[output[name]])
                        for x,y in zip(a,b):
                            self.assertAlmostEqual(x,y,delta=max(1e-8,abs(x)*1e-12))
                    for name,value in invariant_coefficients(parameters).items():
                        self.assertAlmostEqual(invariant_coefficients(p)[name],value,delta=abs(value)*1e-12)

    def test_varying_gamma_alone_is_not_a_normalization_change(self):
        model=load(ROOT/'models/research/terracotta-2024-fig1.json')
        p={name:value['default'] for name,value in model['parameters'].items()}
        state=dict(ev_e=.05,es_e=.005,Tm=.002,phi=.423)
        before=observe(model,state,[2e-5,0,0,0,0,0],p,time=0)['pressure']
        p['Gamma']*=4
        after=observe(model,state,[2e-5,0,0,0,0,0],p,time=0)['pressure']
        self.assertNotEqual(before,after)
        with self.assertRaisesRegex(ValueError,'positive finite'):
            rescale(p,state,0.)


if __name__=='__main__':
    unittest.main()
