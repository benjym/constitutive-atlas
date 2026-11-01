"""SQLite approval provenance must satisfy the canonical independent-review gate."""
import copy
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from atlas import research
from atlas.agent_review import CHECKLIST, approval_entry
from atlas.dsl import ValidationError


class DatabaseApprovalIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.model = json.loads((research.ROOT / 'models/linear-elastic.json').read_text())
        self.model_path = 'models/linear-elastic.json'
        self.review_path = 'catalogue/agent-reviews/elastic-test.json'
        self.registry_path = 'catalogue/approved-models.json'
        self.write(self.model_path, self.model)
        self.write('evidence/reference.json', {'kind': 'synthetic fixture, no scientific claim'})
        self.record = {
            'schema_version': '0.1', 'kind': 'agent-model-review', 'id': 'elastic-test',
            'created_at': '2026-11-01', 'source_commit': 'a' * 40,
            'model': {'id': self.model['id'], 'path': self.model_path, 'sha256': self.sha(self.model_path)},
            'status': 'accepted',
            'reviewer': {'kind': 'agent', 'name': 'Synthetic reviewer', 'run_id': 'review-run',
                         'independence_basis': 'Separate synthetic run'},
            'author_run_ids': ['author-run'], 'scope': 'Synthetic bounded test scope only.',
            'limitations': ['No experimental validation.'], 'blocking_findings': [],
            'checklist': [{'id': key, 'outcome': 'pass', 'reason': 'Synthetic fixture assertion',
                           'evidence': ['evidence/reference.json#check']} for key in sorted(CHECKLIST)],
            'artifacts': [{'path': name, 'sha256': self.sha(name)}
                          for name in (self.model_path, 'evidence/reference.json')],
        }
        self.write(self.review_path, self.record)
        self.approval = approval_entry(self.root / self.review_path, root=self.root)
        self.write(self.registry_path, {'models': [self.approval]})
        self.write('catalogue/manifest.json', {'models': [
            {'id': self.model['id'], 'name': self.model['name'], 'family': self.model['family']} ]})
        for target, value in (
            ('ROOT', self.root), ('all_models', lambda: [self.model]),
            ('load_publications', lambda: {'publications': [], 'relations': []}),
            ('load_screening', lambda: []),
        ):
            context = patch.object(research, target, value)
            context.start()
            self.addCleanup(context.stop)

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + '\n')

    def sha(self, relative):
        return hashlib.sha256((self.root / relative).read_bytes()).hexdigest()

    def export(self, name='atlas.sqlite'):
        path = self.root / name
        research.export_database(path)
        return path

    def replace_review(self, record):
        self.write(self.review_path, record)
        approval = copy.deepcopy(self.approval)
        approval['review']['sha256'] = self.sha(self.review_path)
        self.write(self.registry_path, {'models': [approval]})

    @staticmethod
    def dump(path):
        with closing(sqlite3.connect(path)) as connection:
            return '\n'.join(connection.iterdump())

    def test_valid_export_preserves_exact_provenance_sources_and_membership(self):
        path = self.export()
        with closing(sqlite3.connect(path)) as connection:
            approval = json.loads(connection.execute('select record_json from model_approvals').fetchone()[0])
            review = json.loads(connection.execute('select record_json from agent_reviews').fetchone()[0])
            definition, executable = connection.execute('select definition_json,executable from models').fetchone()
            urls = {row[0] for row in connection.execute('select url from sources')}
        self.assertEqual(approval, self.approval)
        self.assertEqual(review, self.record)
        self.assertEqual(json.loads(definition), self.model)
        self.assertEqual(executable, 1)
        self.assertEqual(urls, {source['url'] for source in self.model['sources']})
        before = self.dump(path)
        self.export()
        self.assertEqual(self.dump(path), before)

    def test_registry_claims_must_match_generated_approval(self):
        for key, value in (
            ('scope', {'use': 'An unreviewed wider scope'}),
            ('limitations', []), ('experimental_validation', 'validated'),
            ('approval_authority', {'kind': 'invented authority'}),
            ('supporting_files', []),
        ):
            with self.subTest(field=key):
                altered = copy.deepcopy(self.approval)
                altered[key] = value
                self.write(self.registry_path, {'models': [altered]})
                with self.assertRaises(ValidationError):
                    self.export()

    def test_agent_authority_cannot_bypass_review_validation_by_changing_kind(self):
        for review in (None, {}, {**self.approval['review'], 'kind': 'different-kind'}):
            with self.subTest(review=review):
                altered = copy.deepcopy(self.approval)
                altered['scope'] = {'use': 'Forged wider scope'}
                if review is None:
                    altered.pop('review')
                else:
                    altered['review'] = review
                self.write(self.registry_path, {'models': [altered]})
                with self.assertRaises(ValidationError):
                    self.export()

    def test_accepted_label_and_matching_hash_cannot_bypass_review_semantics(self):
        mutations = {
            'self_review': lambda r: r['reviewer'].update(run_id='author-run'),
            'missing_item': lambda r: r['checklist'].pop(),
            'failed_item': lambda r: r['checklist'][0].update(outcome='fail'),
            'blocking_finding': lambda r: r['blocking_findings'].append('Unresolved source issue'),
            'unbound_evidence': lambda r: r['checklist'][0].update(evidence=['absent.json#check']),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                altered = copy.deepcopy(self.record)
                mutate(altered)
                self.replace_review(altered)
                with self.assertRaises((ValidationError, ValueError)):
                    self.export()

    def test_corrupt_evidence_and_stale_review_hash_reject(self):
        self.write('evidence/reference.json', {'tampered': True})
        with self.assertRaises(ValidationError):
            self.export()
        self.write('evidence/reference.json', {'kind': 'synthetic fixture, no scientific claim'})
        altered = copy.deepcopy(self.record)
        altered['scope'] += ' changed'
        self.write(self.review_path, altered)
        with self.assertRaisesRegex(ValidationError, 'hash mismatch'):
            self.export()

    def test_failed_reexport_preserves_existing_database(self):
        path = self.export()
        before = self.dump(path)
        altered = copy.deepcopy(self.approval)
        altered['scope'] = {'use': 'Unreviewed scope'}
        self.write(self.registry_path, {'models': [altered]})
        with self.assertRaises(ValidationError):
            self.export()
        self.assertEqual(self.dump(path), before)

    def test_project_metadata_can_extend_an_exact_approval(self):
        extended = {**self.approval, 'project_note': 'Non-authoritative integration metadata'}
        self.write(self.registry_path, {'models': [extended]})
        with closing(sqlite3.connect(self.export())) as connection:
            actual = json.loads(connection.execute('select record_json from model_approvals').fetchone()[0])
        self.assertEqual(actual, extended)


if __name__ == '__main__':
    unittest.main()
