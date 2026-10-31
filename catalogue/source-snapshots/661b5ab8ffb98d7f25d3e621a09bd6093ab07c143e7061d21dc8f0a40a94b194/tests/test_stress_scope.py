"""Metadata scope is explicit without enabling new material profiles."""
import copy
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest
from atlas.compiler import generate
from atlas.dsl import ValidationError
from atlas.model import ROOT, all_models, load, migrate_formulation, validate
from atlas.stress import stress_binding, stress_scope


def scope_fixtures():
    elastic=load(ROOT/'models/linear-elastic.json')
    maxwell=load(ROOT/'tests/fixtures/time/maxwell.json')
    clock=load(ROOT/'tests/fixtures/time/clock.json')
    models={
        'scope-legacy-incremental':elastic,
        'scope-explicit-incremental':migrate_formulation(elastic),
        'scope-legacy-timed':maxwell,
        'scope-effective-timed':migrate_formulation(maxwell,stress_scope='effective'),
        'scope-total-timed':migrate_formulation(maxwell,stress_scope='total'),
        'scope-clock':migrate_formulation(clock),
        'scope-legacy-clock':clock,
    }
    for name,model in models.items():model['id']=name;validate(model)
    return models


def without_stress_scope_metadata(header):
    """Remove only the additive enum/member/initializer tokens for old-byte checks."""
    header=header.replace('enum class StressScope { unspecified, none, effective, total };\n','')
    header=header.replace(' StressScope stress_scope=StressScope::unspecified;','')
    return re.sub(r',StressScope::(?:unspecified|none|effective|total)(?=},$)','',header,flags=re.MULTILINE)


class StressScopeTests(unittest.TestCase):
    def test_explicit_and_legacy_scope_matrix(self):
        expected=json.loads((ROOT/'docs/reviews/stress-scope-metadata-v1/freeze.json').read_text())['expected']
        fixtures=scope_fixtures();self.assertEqual(set(fixtures),set(expected))
        for name,model in fixtures.items():
            self.assertEqual(stress_scope(model),expected[name][0],name)
        for model in all_models():self.assertEqual(stress_scope(model),'effective',model['id'])
        self.assertEqual(stress_binding(fixtures['scope-legacy-timed'])['measure'],'unspecified')

    def test_binding_returns_detached_metadata(self):
        model=scope_fixtures()['scope-total-timed'];before=copy.deepcopy(model)
        binding=stress_binding(model);binding['scope']='effective'
        self.assertEqual(model,before);self.assertEqual(stress_scope(model),'total')

    def test_missing_or_malformed_modern_binding_is_not_inferred(self):
        original=scope_fixtures()['scope-explicit-incremental']
        for binding in [None,{},dict(source='none',scope='total'),dict(source='state',name='sigma',measure='cauchy',scope='unknown'),dict(source='observable',name='stress',measure='kirchhoff',scope='total')]:
            bad=copy.deepcopy(original);bad['formulation']['stress']=binding
            with self.subTest(binding=binding),self.assertRaises(ValidationError):stress_binding(bad)
        for version in [None,'0.4']:
            bad=copy.deepcopy(original);bad['schema_version']=version
            with self.assertRaises(ValidationError):stress_scope(bad)

    def test_scope_metadata_does_not_enable_total_incremental_profile(self):
        model=scope_fixtures()['scope-explicit-incremental'];model['formulation']['stress']['scope']='total'
        self.assertEqual(stress_scope(model),'total')
        with self.assertRaisesRegex(ValidationError,'effective Cauchy'):validate(model)

    def test_catalogue_and_all_generated_numerical_functions_match_prior_generator(self):
        previous=json.loads((ROOT/'docs/reviews/stress-scope-metadata-v1/previous-sources.json').read_text())
        spec=importlib.util.spec_from_file_location('atlas._prior_scope_compiler',ROOT/previous['atlas/compiler.py']['archived_path'])
        prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fixtures=root/'fixtures';fixtures.mkdir()
            for name,model in scope_fixtures().items():(fixtures/(name+'.json')).write_text(json.dumps(model))
            for name,paths in [('public',None),('scope',list(fixtures.glob('*.json')))]:
                old=root/(name+'-old');new=root/(name+'-new');prior.generate(old,paths);generate(new,paths)
                self.assertEqual((new/'models.json').read_bytes(),(old/'models.json').read_bytes(),name)
                old_header=(old/'models.hpp').read_text();new_header=(new/'models.hpp').read_text()
                self.assertEqual(without_stress_scope_metadata(new_header),old_header,name)
                # Includes residuals/rates, all guards, observable/scaling/AD code: compare complete suffix.
                marker='template<class T> bool evaluate_model('
                self.assertEqual(new_header[new_header.index(marker):],old_header[old_header.index(marker):],name)
                self.assertIn('enum class StressScope { unspecified, none, effective, total };',new_header)
                if name=='public':self.assertEqual(new_header.count(',StressScope::effective},'),9)


if __name__=='__main__':unittest.main()
