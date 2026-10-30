import copy
import json
from pathlib import Path
import tempfile
import unittest

from atlas.baseline import CHECK_IDS, artifact, dump, verify
from atlas.model import ROOT


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'logs').mkdir()
        dump(self.root/'source-inventory.json',[dict(path='models/linear-elastic.json',sha256='b'*64)])
        dump(self.root/'elasticity-results.json',dict(passed=True,cases=[dict(id='fixture',passed=True)]))
        checks=[]
        for ident in CHECK_IDS:
            log=self.root/'logs'/(ident+'.txt');log.write_text('fixture result\n')
            checks.append(dict(id=ident,command=['fixture'],returncode=0,elapsed_seconds=0,log=artifact(self.root,log)))
        catalogue=dict(sha256='c'*64,models=[dict(id='linear-elastic',status='transcribed',path='models/linear-elastic.json',sha256='b'*64)])
        self.record=dict(schema_version='0.1',kind='software-baseline',id='baseline-fixture',created_at='2026-10-30T00:00:00Z',
            source_commit='a'*40,git_tree='d'*40,scope='Integrity fixture',outcome='passed',
            versions=dict(python_package='fixture',model_schema_versions=['0.1','0.2'],compiler='source-pinned',engine='source-pinned',expression_language='source-pinned'),
            toolchain={key:'fixture' for key in ('python','cmake','node','emscripten','platform','native_cxx')},
            configuration=dict(native={},wasm={}),
            inventory=artifact(self.root,self.root/'source-inventory.json'),checks=checks,
            catalogues={key:copy.deepcopy(catalogue) for key in ('public','temporal-fixtures','research')},
            build_products={key:'e'*64 for key in ('build/atlas_solver','build/atlas_time_solver','build/atlas_research_solver','build-wasm/atlas.js','build-wasm/atlas.wasm','build-wasm/time-fixtures.js','build-wasm/time-fixtures.wasm','build-wasm/research.js','build-wasm/research.wasm')},
            reports=[artifact(self.root,self.root/'elasticity-results.json')],limitations=['Not scientific review'],reproduction=['fixture'])

    def verify(self):
        dump(self.root/'manifest.json',self.record)
        return verify(self.root/'manifest.json')

    def test_complete_baseline_integrity(self):
        self.assertEqual(self.verify()['outcome'],'passed')

    def test_passing_claim_requires_all_checks_and_zero_return_codes(self):
        checks=copy.deepcopy(self.record['checks'])
        self.record['checks'].pop()
        with self.assertRaises(ValueError): self.verify()
        self.record['checks']=checks
        self.record['checks'][0]['returncode']=1
        with self.assertRaises(ValueError): self.verify()
        self.record['outcome']='failed'
        self.assertEqual(self.verify()['outcome'],'failed')

    def test_changed_log_and_failed_oracle_cannot_support_passing_claim(self):
        log=self.root/'logs/definitions.txt'
        log.write_text('altered\n')
        with self.assertRaises(ValueError): self.verify()
        self.record['checks'][0]['log']=artifact(self.root,log)
        dump(self.root/'elasticity-results.json',dict(passed=False,cases=[dict(id='fixture',passed=False)]))
        self.record['reports'][0]=artifact(self.root,self.root/'elasticity-results.json')
        with self.assertRaises(ValueError): self.verify()

    def test_model_hash_must_match_the_export_inventory(self):
        self.record['catalogues']['public']['models'][0]['sha256']='f'*64
        with self.assertRaises(ValueError): self.verify()

    def test_paths_cannot_escape_baseline_directory(self):
        self.record['checks'][0]['log']['path']='../outside.txt'
        with self.assertRaises(ValueError): self.verify()

    def test_committed_baseline_records(self):
        for path in (ROOT/'catalogue/baselines').glob('*/manifest.json'):
            with self.subTest(baseline=path.parent.name): verify(path)
