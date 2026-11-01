"""Agent-review export must preserve exact scope/history and never infer approval."""
import copy
import json
import unittest
from atlas.agent_review import CHECKLIST, approval_entry
from tests import test_build_evidence as fixture


class AgentReviewExport(unittest.TestCase):
    setUp = fixture.Export.setUp
    write = fixture.Export.write
    sha = fixture.Export.sha
    export = fixture.Export.export

    def review(self, mid='elastic'):
        path = 'catalogue/agent-reviews/elastic-agent-v1.json'
        self.write('artifacts/review.json', {'checked': 'synthetic fixture only'})
        model = 'models/elastic.json'
        record = {
            'schema_version': '0.1', 'kind': 'agent-model-review', 'id': 'elastic-agent-v1',
            'created_at': '2026-11-01', 'source_commit': 'a' * 40,
            'model': {'id': mid, 'path': model, 'sha256': self.sha(model)},
            'status': 'accepted', 'reviewer': {'kind': 'agent', 'name': 'Synthetic fixture',
                'run_id': 'reviewer-fixture', 'independence_basis': 'Separate synthetic fixture'},
            'author_run_ids': ['author-fixture'], 'scope': 'Bounded synthetic law only.',
            'limitations': ['No experimental or current release claim.'], 'blocking_findings': [],
            'checklist': [{'id': key, 'outcome': 'pass', 'reason': 'Synthetic test decision',
                'evidence': ['artifacts/review.json#fixture']} for key in sorted(CHECKLIST)],
            'artifacts': [{'path': p, 'sha256': self.sha(p)} for p in (model, 'artifacts/review.json')],
        }
        self.write(path, record)
        return path, record

    def register(self, path):
        entry = approval_entry(self.root / path, root=self.root)
        self.write('catalogue/approved-models.json', {'models': [entry]})
        return entry

    def archive(self, document, names):
        entries = []
        for name in names:
            expected = self.sha(name)
            archive = 'catalogue/source-snapshots/' + expected + '/' + name
            target = self.root / archive
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((self.root / name).read_bytes())
            entries.append({'original_path': name, 'sha256': expected, 'archived_path': archive})
        self.write('catalogue/agent-reviews/source-archive-map.json', {
            'version': 'immutable-source-archive-map-0.1',
            'documents': {document: self.sha(document)}, 'entries': entries})
        return entries

    def test_actual_record_and_definition_retained_without_implicit_registry_approval(self):
        path, record = self.review()
        index = self.export(); row = index['agent_reviews'][0]
        self.assertTrue(row['definition_current']); self.assertEqual(row['status'], 'accepted')
        self.assertIsNone(row['registered_approval_id'])
        self.assertEqual(row['scope'], record['scope'])
        self.assertEqual((self.dest/'evidence-records'/path).read_bytes(), (self.root/path).read_bytes())
        self.assertEqual((self.dest/'evidence-records'/row['definition_record_path']).read_bytes(), (self.root/'models/elastic.json').read_bytes())
        self.assertFalse((self.dest/'evidence-records/artifacts').exists())
        self.assertEqual(index['records'][0]['outcome'], 'failed')

    def test_exact_explicit_registry_approval_is_visible_and_downloadable(self):
        path, _ = self.review(); entry = self.register(path)
        index = self.export()
        self.assertEqual(index['agent_reviews'][0]['registered_approval_id'], entry['id'])
        self.assertEqual((self.dest/'evidence-records/catalogue/approved-models.json').read_bytes(), (self.root/'catalogue/approved-models.json').read_bytes())

    def test_forged_scope_or_duplicated_approval_rejects_before_writes(self):
        path, _ = self.review(); entry = self.register(path)
        bad = copy.deepcopy(entry); bad['scope']['use'] = 'Unreviewed broader scope'
        self.write('catalogue/approved-models.json', {'models': [bad]})
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())
        self.write('catalogue/approved-models.json', {'models': [entry, entry]})
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())

    def test_historical_approval_keeps_old_definition_without_approving_current(self):
        path, _ = self.review(); self.register(path)
        old = (self.root/'models/elastic.json').read_bytes()
        self.archive(path, ['models/elastic.json'])
        self.write('models/elastic.json', {'id': 'elastic', 'changed': True})
        with self.assertRaises(ValueError): approval_entry(self.root/path, root=self.root)
        row = self.export()['agent_reviews'][0]
        self.assertFalse(row['definition_current']); self.assertIsNotNone(row['registered_approval_id'])
        self.assertEqual((self.dest/'evidence-records'/row['definition_record_path']).read_bytes(), old)
        self.assertFalse((self.dest/'models/elastic.json').exists())

    def test_corrupt_archive_never_falls_back_to_matching_live_bytes(self):
        path, _ = self.review(); entries = self.archive(path, ['models/elastic.json'])
        (self.root/entries[0]['archived_path']).write_bytes(b'corrupt')
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())

    def test_changed_model_without_explicit_archive_fails(self):
        self.review(); self.write('models/elastic.json', {'id': 'elastic', 'changed': True})
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())

    def test_historical_artifact_resolves_only_through_bound_receipt(self):
        path, _ = self.review(); self.archive(path, ['artifacts/review.json'])
        self.write('artifacts/review.json', {'changed': True})
        self.assertTrue(self.export()['agent_reviews'][0]['definition_current'])
        self.write(path, {'tampered': True})
        with self.assertRaises(ValueError): self.export()

    def test_unbound_variant_is_explicitly_omitted_without_guessing_catalogue_family(self):
        path, _ = self.review('unknown-variant')
        index = self.export()
        self.assertEqual(index['agent_reviews'], [])
        self.assertEqual(index['coverage']['omitted_agent_reviews_without_catalogue_binding'], [path])
        self.assertFalse((self.dest/'evidence-records'/path).exists())

    def test_self_review_and_incomplete_checklist_fail_before_export(self):
        path, record = self.review(); record['reviewer']['run_id'] = 'author-fixture'; self.write(path, record)
        with self.assertRaises(ValueError): self.export()
        record['reviewer']['run_id'] = 'reviewer-fixture'; record['checklist'][0] = record['checklist'][1]; self.write(path, record)
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())

    def test_external_record_symlink_rejects(self):
        path, _ = self.review(); outside = self.root.parent/'outside.json'
        outside.write_bytes((self.root/path).read_bytes()); (self.root/path).unlink(); (self.root/path).symlink_to(outside)
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.dest.exists())
