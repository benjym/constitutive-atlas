import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from atlas.dsl import ValidationError
from atlas.evidence import sha256, validate_record
from atlas.model import ROOT


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'report.json').write_text('{}')
        (self.root/'models').mkdir()
        (self.root/'models/test.json').write_text('{}')
        self.path = self.root/'record.json'
        self.record = dict(schema_version='0.1',kind='numerical-evidence',id='test-evidence',created_at='2026-10-30T00:00:00Z',
            source_commit='a'*40,model=dict(id='test',definition_sha256=sha256(self.root/'models/test.json')),
            executor=dict(name='Automated test',automated=True,method='analytical-closed-form',independent_review=False),
            scope='Integrity fixture',limitations=['No scientific claim'],outcome='passed',
            artifacts=[dict(path='report.json',sha256=sha256(self.root/'report.json'))],
            source_files=[dict(path='models/test.json',sha256=sha256(self.root/'models/test.json'))],
            reproduction_command='fixture')

    def validate(self, current=False):
        self.path.write_text(json.dumps(self.record))
        return validate_record(self.path, self.root, current=current)

    def test_valid_integrity_record_and_current_definition(self):
        self.assertEqual(self.validate(True)['outcome'], 'passed')

    def test_modified_artifact_is_rejected(self):
        (self.root/'report.json').write_text('{"changed":true}')
        with self.assertRaises(ValidationError): self.validate()

    def test_historical_record_is_separate_from_current_compatibility(self):
        (self.root/'models/test.json').write_text('{"changed":true}')
        self.validate()
        with self.assertRaises(ValidationError): self.validate(True)

    def test_automated_record_cannot_claim_independent_review(self):
        self.record['executor']['independent_review'] = True
        with self.assertRaises(ValidationError): self.validate()

    def test_traversal_and_duplicate_artifacts_are_rejected(self):
        for item in [dict(path='../outside.json',sha256='a'*64),self.record['artifacts'][0]]:
            with self.subTest(item=item):
                original=copy.deepcopy(self.record['artifacts'])
                self.record['artifacts'].append(item)
                with self.assertRaises(ValidationError): self.validate()
                self.record['artifacts']=original

    def test_review_cannot_close_without_reviewer_or_with_open_questions(self):
        dossier=self.root/'docs/models/test.md';dossier.parent.mkdir(parents=True);dossier.write_text('Pending')
        self.record={k:v for k,v in self.record.items() if k in ('schema_version','kind','id','created_at','source_commit','model')}
        self.record.update(kind='source-review',status='pending',independent=False,dossier='docs/models/test.md',evidence_ids=['test-evidence'],unresolved=['Independent review pending'])
        self.validate(True)
        self.record['status']='accepted'
        with self.assertRaises(ValidationError): self.validate()
        self.record.update(independent=True,reviewer='Fixture reviewer',reviewed_at='2026-10-30')
        with self.assertRaises(ValidationError): self.validate()

    def test_oracle_detects_shear_factor_and_void_ratio_errors(self):
        spec=importlib.util.spec_from_file_location('elasticity_oracle',ROOT/'tools/verify_elasticity.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        initial=[0]*6+[.7]
        expected=module.expected_state(initial,[0,0,0,.001,0,0],3e7,.25)
        self.assertAlmostEqual(expected[3],24000)
        wrong=expected.copy();wrong[3]/=2
        self.assertFalse(module.compare(wrong,expected)[0])
        wrong=expected.copy();wrong[6]+=.00001
        self.assertFalse(module.compare(wrong,expected)[0])

    def test_native_elasticity_closed_forms(self):
        spec=importlib.util.spec_from_file_location('elasticity_oracle',ROOT/'tools/verify_elasticity.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        report=module.execute(Path(os.environ.get('ATLAS_SOLVER',ROOT/'build/atlas_solver')))
        self.assertEqual(len(report['cases']),29)
        self.assertTrue(report['passed'],[c['id'] for c in report['cases'] if not c['passed']])

    def test_committed_records_have_valid_integrity(self):
        for directory in ('evidence','reviews'):
            for path in (ROOT/'catalogue'/directory).glob('*.json'):
                # This named archive map is verified by test_evidence_archives;
                # every other JSON file must remain a typed evidence envelope.
                if path.name == 'source-archive-map.json':
                    continue
                with self.subTest(record=path.name): validate_record(path)
