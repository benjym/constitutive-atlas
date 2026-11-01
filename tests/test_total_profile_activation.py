"""Total profile admission is semantic only; no compiled or material execution."""
from tests.historical_generation import public_paths
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas.compiler import generate
from atlas.dsl import ValidationError
from atlas.model import ROOT,load,migrate_formulation,validate
from tests.laboratory_scope_support import synthetic_total,generate_transport_fixture
P=ROOT/'docs/reviews/total-profile-activation-v1'
def prior_validator():
    old=json.loads((P/'previous-sources.json').read_text())['atlas/model.py']
    path=ROOT/old['archived_path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==old['sha256']
    spec=importlib.util.spec_from_file_location('atlas._before_total_activation',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # The archived module lives under a hash directory; use unchanged current schema resources.
    module.ROOT=ROOT
    return module
class TotalProfileActivationTests(unittest.TestCase):
    def test_effective_and_total_residual_and_rate(self):
        for path in ('linear-elastic','hypoplastic-sand-vw96'):
            base=migrate_formulation(load(ROOT/'models'/(path+'.json')))
            for scope in ('effective','total'):
                model=copy.deepcopy(base);model['formulation']['stress']['scope']=scope
                with self.subTest(path=path,scope=scope):self.assertIs(validate(model),model)
        with self.assertRaises(ValidationError):migrate_formulation(load(ROOT/'models/linear-elastic.json'),stress_scope='total')
    def test_scope_does_not_relax_other_restrictions(self):
        base=synthetic_total();mutations=[]
        for key,value in [('scope','unknown'),('scope',None),('scope',True),('name','e'),('source','observable'),('source','none'),('measure','kirchhoff')]:
            m=copy.deepcopy(base);m['formulation']['stress'][key]=value;mutations.append((key+str(value),m))
        for descriptor in ({'source':'none'},{'source':'state','name':'sigma','measure':'cauchy'},dict(base['formulation']['stress'],pore_pressure=True)):
            m=copy.deepcopy(base);m['formulation']['stress']=descriptor;mutations.append(('descriptor'+str(descriptor),m))
        for key,value in [('frame','corotated'),('kinematics','finite_strain'),('tensor_representation','voigt'),('stress_sign','tension_positive'),('strain_sign','tension_positive')]:
            m=copy.deepcopy(base);m['formulation'][key]=value;mutations.append((key,m))
        for key,value in [('role','transient'),('quantity','unspecified'),('transformation','fixed_components')]:
            m=copy.deepcopy(base);m['state'][0]['semantics'][key]=value;mutations.append(('semantics-'+key,m))
        for key,value in [('shape','scalar'),('unit','1'),('name','tau')]:
            m=copy.deepcopy(base);m['state'][0][key]=value;mutations.append(('state-'+key,m))
        m=copy.deepcopy(base);m['initialization']['required_state']=[];mutations.append(('missing-initialization',m))
        for name,m in mutations:
            with self.subTest(name=name),self.assertRaises(ValidationError):validate(m)
        self.assertEqual(len(mutations),22)
    def test_pinned_tresca_normal_validation_and_generation(self):
        path=ROOT/'docs/reviews/tresca-declarative-v1/model.json'
        original=path.read_bytes();m=load(path)
        self.assertEqual(m['formulation']['stress']['scope'],'total')
        self.assertEqual(m['initialization']['required_state'],['sigma','ep'])
        self.assertEqual(sum(6 if f['shape']=='sym' else 1 for f in m['state']),12)
        self.assertEqual(m['domain'],['p_ref>0*p_ref','lame_lambda>0*p_ref','mu>0*p_ref','k>0*p_ref'])
        with self.assertRaisesRegex(ValidationError,'requires effective Cauchy'):prior_validator().validate(m)
        with tempfile.TemporaryDirectory() as d:
            generate(d,[path]);catalogue=json.loads((Path(d)/'models.json').read_text());header=(Path(d)/'models.hpp').read_text()
            self.assertEqual(catalogue['models'],[m]);self.assertIn('StressScope::total',header)
            self.assertIn('projector_min',header);self.assertIn('projector_max',header)
        self.assertEqual(path.read_bytes(),original)
    def test_public_generation_is_byte_identical_to_frozen_validator(self):
        paths=public_paths();self.assertEqual(len(paths),9)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);generate(p/'new',paths)
            with patch('atlas.compiler.load',side_effect=prior_validator().load):generate(p/'old',paths)
            for name in ('models.json','models.hpp'):
                self.assertEqual((p/'new'/name).read_bytes(),(p/'old'/name).read_bytes(),name)
    def test_total_fixture_uses_normal_production_loader(self):
        with tempfile.TemporaryDirectory() as d:
            generate_transport_fixture(d)
            total=load(Path(d)/'fixtures/scope-synthetic-total-elastic.json')
            self.assertEqual(total,synthetic_total())
            generated=json.loads((Path(d)/'generated/models.json').read_text())
            from atlas.model import all_models
            self.assertEqual({m['id'] for m in generated['models']}, {m['id'] for m in all_models()} | {total['id']})
            self.assertEqual(len(generated['models']),len(all_models())+1)
            for model in all_models():self.assertIn(model,generated['models'])
            self.assertIn(total,generated['models'])
