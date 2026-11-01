"""Archived review evidence must remain exact without accepting stale models."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from atlas.agent_review import CHECKLIST, validate_review
from atlas.dsl import ValidationError

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class AgentReviewArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'models').mkdir()
        self.model=self.root/'models/test.json';self.model.write_text('{"id":"test"}')
        self.report=self.root/'report.md';self.report.write_text('Original reviewed policy bytes')
        self.path=self.root/'reviews/review.json';self.path.parent.mkdir()
        self.record=dict(schema_version='0.1',kind='agent-model-review',id='test-review',
            created_at='2026-11-01',source_commit='a'*40,
            model=dict(id='test',path='models/test.json',sha256=sha(self.model)),status='accepted',
            reviewer=dict(kind='agent',name='reviewer',run_id='independent',independence_basis='Separate fixture run'),
            author_run_ids=['author'],scope='Fixture',limitations=['No physical claim'],blocking_findings=[],
            artifacts=[dict(path='report.md',sha256=sha(self.report))],
            checklist=[dict(id=k,outcome='pass',reason='Fixture',evidence=['report.md']) for k in sorted(CHECKLIST)])
        self.path.write_text(json.dumps(self.record))
        h=sha(self.report);self.archive=self.root/'catalogue/source-snapshots'/h/'report.md'
        self.archive.parent.mkdir(parents=True);self.archive.write_bytes(self.report.read_bytes())
        self.sidecar=self.path.parent/'source-archive-map.json'
        self.mapping=dict(version='immutable-source-archive-map-0.1',
            documents={'reviews/review.json':sha(self.path)},
            entries=[dict(original_path='report.md',sha256=h,archived_path=str(self.archive.relative_to(self.root)))])
        self.sidecar.write_text(json.dumps(self.mapping));self.report.write_text('New policy text')

    def validate(self):return validate_review(self.path,self.root,for_approval=True)

    def test_archived_policy_validates_without_rewriting_original_review(self):
        original=self.path.read_bytes();self.validate();self.assertEqual(self.path.read_bytes(),original)
        self.report.unlink();self.validate()

    def test_corrupt_or_missing_archive_never_falls_back_to_original_live_bytes(self):
        original=self.archive.read_bytes();self.report.write_bytes(original)
        self.archive.write_text('corrupt')
        with self.assertRaises(ValidationError):self.validate()
        self.archive.unlink()
        with self.assertRaises(ValidationError):self.validate()

    def test_changed_review_and_ambiguous_or_escaping_maps_rejected(self):
        for kind in ('document','duplicate','escape','version'):
            mapping=json.loads(json.dumps(self.mapping))
            if kind=='document':mapping['documents']['reviews/review.json']='0'*64
            elif kind=='duplicate':mapping['entries'].append(mapping['entries'][0])
            elif kind=='escape':mapping['entries'][0]['archived_path']='../outside'
            else:mapping['version']='invalid'
            self.sidecar.write_text(json.dumps(mapping))
            with self.subTest(kind=kind),self.assertRaises(ValidationError):self.validate()

    def test_current_model_is_still_required_even_if_its_old_bytes_are_archived(self):
        self.model.write_text('{"id":"changed"}')
        with self.assertRaises(ValidationError):self.validate()

    def test_unmapped_other_review_requires_exact_live_artifacts(self):
        other=self.path.parent/'other.json';other.write_text(json.dumps(self.record))
        with self.assertRaises(ValidationError):validate_review(other,self.root,for_approval=True)
        self.report.write_bytes(self.archive.read_bytes());validate_review(other,self.root,for_approval=True)

if __name__=='__main__':unittest.main()
