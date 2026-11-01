"""Agent approval gates require actual distinct-run, exact-byte checklist records."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from atlas.agent_review import CHECKLIST, approval_entry, validate_review
from atlas.dsl import ValidationError
from atlas.evidence import sha256


class AgentReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        model = self.root/'models/test.json'; model.parent.mkdir(); model.write_text('{"id":"test"}')
        report = self.root/'report.md'; report.write_text('Independent fixture review; no scientific model approval.')
        self.path = self.root/'review.json'
        self.record = dict(schema_version='0.1', kind='agent-model-review', id='test-agent-v1',
            created_at='2026-11-01', source_commit='a'*40,
            model=dict(id='test', path='models/test.json', sha256=sha256(model)), status='accepted',
            reviewer=dict(kind='agent', name='Fixture reviewing agent', run_id='review-run', independence_basis='Separate run; independently inspected fixture'),
            author_run_ids=['author-run'], scope='Synthetic unit-test fixture only', limitations=['No scientific or experimental claim'],
            blocking_findings=[], artifacts=[dict(path='report.md', sha256=sha256(report))],
            checklist=[dict(id=item, outcome='pass', reason='Synthetic fixture assessment', evidence=['report.md#'+item]) for item in sorted(CHECKLIST)])

    def validate(self, approval=True):
        self.path.write_text(json.dumps(self.record))
        return validate_review(self.path, self.root, for_approval=approval)

    def test_agent_alone_can_approve_exact_scope_without_human_fields(self):
        self.validate(); entry=approval_entry(self.path,self.root)
        self.assertEqual(entry['status'],'approved')
        self.assertEqual(entry['approval_authority']['kind'],'independent-agent-review')
        self.assertEqual(entry['scope']['use'],self.record['scope'])
        self.assertEqual(entry['experimental_validation'],'not_assessed')
        self.assertFalse(entry['deployment_authorized'])

    def test_author_cannot_review_own_transcription(self):
        self.record['reviewer']['run_id']='author-run'
        with self.assertRaises(ValidationError):self.validate()

    def test_incomplete_duplicate_failed_or_core_na_checklist_blocks_approval(self):
        original=copy.deepcopy(self.record)
        for kind in ('missing','duplicate','pending','fail','core-na'):
            self.record=copy.deepcopy(original)
            if kind=='missing':self.record['checklist'].pop()
            elif kind=='duplicate':self.record['checklist'][0]=self.record['checklist'][1]
            else:
                row=next(row for row in self.record['checklist'] if row['id']=='equation_fidelity')
                row['outcome']={'pending':'pending','fail':'fail','core-na':'not-applicable'}[kind]
            with self.subTest(kind=kind),self.assertRaises(ValidationError):self.validate()

    def test_pending_and_changes_requested_are_not_approvals(self):
        for status in ('pending','changes-requested'):
            self.record['status']=status; self.validate(False)
            with self.assertRaises(ValidationError):self.validate()

    def test_blocking_findings_cannot_be_hidden_by_passing_items(self):
        self.record['blocking_findings']=['Sign conversion unresolved']
        with self.assertRaises(ValidationError):self.validate()

    def test_unsupported_compiled_backend_can_be_excluded_with_evidence(self):
        row=next(row for row in self.record['checklist'] if row['id']=='backend_delivery')
        row['outcome']='not-applicable';row['reason']='No compiled interface in fixture scope'
        self.validate()
        row['reason']=''
        with self.assertRaises(ValidationError):self.validate()

    def test_stale_model_id_or_artifacts_and_unbound_references_are_rejected(self):
        original=copy.deepcopy(self.record)
        for kind in ('hash','id','artifact','unbound','escape','duplicate-artifact','human'):
            self.record=copy.deepcopy(original)
            if kind=='hash':self.record['model']['sha256']='0'*64
            elif kind=='id':self.record['model']['id']='other'
            elif kind=='artifact':self.record['artifacts'][0]['sha256']='0'*64
            elif kind=='unbound':self.record['checklist'][0]['evidence']=['unhashed.md']
            elif kind=='escape':self.record['model']['path']='models/../report.md'
            elif kind=='duplicate-artifact':self.record['artifacts'].append(self.record['artifacts'][0])
            else:self.record['reviewer']['kind']='human'
            with self.subTest(kind=kind),self.assertRaises(ValidationError):self.validate()


if __name__=='__main__':unittest.main()
