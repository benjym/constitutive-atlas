"""Pure packaging fixtures. No compiled module or Wasm is executed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('maxwell_packager', ROOT/'tools/build_maxwell_laboratory.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class MaxwellPackage(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='atlas-maxwell-package-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.build, self.dest = self.base/'build', self.base/'site'
        self.build.mkdir()
        package.generate(self.build/'generated', [ROOT/package.DEFINITION])
        (self.build/'maxwell.js').write_bytes(b'// SYNTHETIC TEST MODULE; never executed\n')
        (self.build/'maxwell.wasm').write_bytes(b'SYNTHETIC TEST WASM; never executed')
        self.binding = {'model_sha256': package.digest((ROOT/package.DEFINITION).read_bytes()),
                        'catalogue_file_sha256': package.digest((self.build/'generated/models.json').read_bytes()),
                        'module_sha256': package.digest((self.build/'maxwell.js').read_bytes()),
                        'wasm_sha256': package.digest((self.build/'maxwell.wasm').read_bytes()),
                        'source_manifest_sha256': package.source_manifest()['sha256'],
                        'reference_policy_sha256': package.digest((ROOT/package.REFERENCE).read_bytes())}
        self.review = {'status': 'accepted', 'reviewer_run': 'synthetic-test-reviewer', 'binding': self.binding,
                       'gates': dict.fromkeys(package.GATES, True)}
        self.qualification = {'schema_version': 'maxwell-qualified-build-1', 'model': package.MODEL, 'status': 'passed',
                              'binding': self.binding, 'gates': dict.fromkeys(package.GATES, True),
                              'implementation_run': 'synthetic-test-implementation'}
        self.save_receipts()

    def save_receipts(self):
        review = package.encoded(self.review)
        (self.build/'independent.json').write_bytes(review)
        self.qualification['independent_review'] = {'path': 'independent.json', 'sha256': package.digest(review)}
        (self.build/'maxwell-qualification.json').write_bytes(package.encoded(self.qualification))

    def reject(self):
        with self.assertRaises((ValueError, FileNotFoundError)):
            package.bundle(self.dest, self.build)
        self.assertFalse(self.dest.exists(), 'Failed preflight must not publish partial site')

    def test_exact_public_bundle_identity_and_assets(self):
        identity = package.bundle(self.dest, self.build)
        self.assertEqual(identity['model_sha256'], self.binding['model_sha256'])
        manifest = json.loads((self.dest/'engine-maxwell/package-manifest.json').read_text())
        self.assertEqual(manifest['kind'], 'maxwell-main-atlas-1')
        for name, expected in manifest['files'].items():
            self.assertEqual(package.digest((self.dest/name).read_bytes()), expected, name)
        self.assertEqual(set(identity['component_sha256']), set(package.COMPONENTS))
        self.assertEqual((self.dest/'engine-maxwell/maxwell.mjs').read_bytes(), (self.build/'maxwell.js').read_bytes())
        self.assertEqual(json.loads((self.dest/'engine-maxwell/qualification.json').read_bytes()), self.qualification)
        self.assertIn('index.html#laboratory?model='+package.MODEL, (self.dest/'engine-maxwell/review.html').read_text())
        self.assertIn('https://docs.itascacg.com/', (self.dest/'maxwell-laboratory.mjs').read_text())
        self.assertFalse((self.dest/'maxwell.html').exists())
        self.assertFalse(any('.pdf' in name or 'private-sources' in name for name in manifest['files']))

    def test_missing_qualification_rejects(self):
        (self.build/'maxwell-qualification.json').unlink()
        self.reject()

    def test_failed_or_incomplete_gate_rejects(self):
        for mutate in [lambda: self.qualification.update(status='failed'),
                       lambda: self.qualification['gates'].update(parity=False),
                       lambda: self.qualification['gates'].update(parity=1),
                       lambda: self.qualification['gates'].pop('presets')]:
            with self.subTest(mutate=mutate):
                original = json.loads(json.dumps(self.qualification))
                mutate(); self.save_receipts(); self.reject()
                self.qualification = original

    def test_stale_engine_or_catalogue_rejects(self):
        for path in ['maxwell.js', 'maxwell.wasm', 'generated/models.json']:
            with self.subTest(path=path):
                target = self.build/path; original = target.read_bytes()
                target.write_bytes(original+b'changed')
                self.reject(); target.write_bytes(original)

    def test_changed_source_or_reference_policy_identity_rejects(self):
        for key in ['source_manifest_sha256', 'reference_policy_sha256']:
            with self.subTest(key=key):
                original = self.binding[key]; self.binding[key] = '0'*64
                self.save_receipts(); self.reject(); self.binding[key] = original

    def test_separate_review_required_and_exact(self):
        for mutate in [lambda: self.review.update(status='pending'),
                       lambda: self.review.update(reviewer_run='synthetic-test-implementation'),
                       lambda: self.review['gates'].update(presets=False)]:
            with self.subTest(mutate=mutate):
                original = json.loads(json.dumps(self.review))
                mutate(); self.save_receipts(); self.reject(); self.review = original
        self.save_receipts()
        (self.build/'independent.json').write_text('{}')
        self.reject()

    def test_review_path_traversal_and_unregistered_approval_reject(self):
        self.qualification['independent_review']['path'] = '../elsewhere.json'
        (self.build/'maxwell-qualification.json').write_bytes(package.encoded(self.qualification))
        self.reject()
        self.save_receipts()
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            if path == ROOT/'catalogue/approved-models.json':
                registry = json.loads(data)
                registry['models'] = [x for x in registry['models'] if x['id'] != 'maxwell-itasca900-zero-spin-agent-review-v2-approval']
                return package.encoded(registry)
            return data
        with patch.object(Path, 'read_bytes', changed):
            self.reject()

    def test_widened_approval_and_matching_registry_cannot_override_canonical_review(self):
        original = Path.read_bytes
        altered = json.loads(original(ROOT/package.APPROVAL))
        altered['scope']['use'] = 'unrestricted experimental approval'
        altered['limitations'] = []
        altered['experimental_validation'] = 'validated'
        def changed(path):
            data = original(path)
            if path == ROOT/package.APPROVAL:
                return package.encoded(altered)
            if path == ROOT/'catalogue/approved-models.json':
                registry = json.loads(data)
                registry['models'] = [altered if row['id'] == altered['id'] else row for row in registry['models']]
                return package.encoded(registry)
            return data
        with patch.object(Path, 'read_bytes', changed):
            self.reject()

    def test_rejected_interface_review_cannot_be_used_as_a_file_list(self):
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            if path == ROOT/package.INTERFACE_REVIEW:
                review = json.loads(data)
                review.update(decision='rejected', unresolved_in_scope_blockers=['test blocker'])
                return package.encoded(review)
            return data
        with patch.object(Path, 'read_bytes', changed):
            self.reject()

    def test_module_symlink_outside_build_is_rejected(self):
        external = self.base/'external.mjs'
        external.write_bytes((self.build/'maxwell.js').read_bytes())
        (self.build/'maxwell.js').unlink()
        (self.build/'maxwell.js').symlink_to(external)
        self.reject()

    def test_changed_reviewed_interface_rejects(self):
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            return data+b'\n// changed interface' if path == ROOT/'web/maxwell-atlas-engine.mjs' else data
        with patch.object(Path, 'read_bytes', changed):
            self.reject()

    def test_mid_preflight_source_drift_preserves_destination_absence(self):
        before = package.source_manifest()
        with patch.object(package, 'source_manifest', side_effect=[before, {'files': {}, 'sha256': '0'*64}]):
            self.reject()


if __name__ == '__main__':
    unittest.main()

