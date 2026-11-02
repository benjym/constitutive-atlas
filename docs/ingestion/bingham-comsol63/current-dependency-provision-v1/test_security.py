"""Synthetic fixtures/mocked review and guards only; no actual assets provisioned."""
from contextlib import contextmanager
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import warnings
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('dependency_provision', ROOT / 'tools/provision_bingham_dependency_assets.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def archive_fixture(change=None, duplicate=False):
    files = {name: bytes([i + 1]) * size for i, (name, size) in enumerate(module.MEMBERS.items())}
    entries = [(name, data, stat.S_IFREG | 0o644, 3) for name, data in files.items()]
    if change:
        change(entries)
    if duplicate:
        entries.append(entries[0])
    raw = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(raw, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data, mode, system in entries:
                info = zipfile.ZipInfo(name)
                info.create_system = system
                info.external_attr = mode << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
    index = {'identity': 'bingham-current-dependency-assets-v1', 'archive': module.ARCHIVE,
             'archive_sha256': module.digest(raw.getvalue()),
             'files': {name: module.digest(data) for name, data in files.items()}}
    return index, raw.getvalue(), files


class SecurityTests(unittest.TestCase):
    def setUp(self):
        scratch = HERE / 'scratch'
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.index, self.raw, self.files = archive_fixture()
        self.binding = {'synthetic': 'review-binding'}
        self.sha_patch = patch.object(module, 'ARCHIVE_SHA256', module.digest(self.raw))
        self.sha_patch.start()
        self.addCleanup(self.sha_patch.stop)

    def selected(self, index, raw):
        with patch.object(module, 'ARCHIVE_SHA256', module.digest(raw)):
            return module._selected_files(index, raw)

    def test_exact_twelve_fixture_and_changed_bytes(self):
        self.assertEqual(self.selected(self.index, self.raw), self.files)
        changed = dict(self.index, files=dict(self.index['files']))
        changed['files']['maxwell/maxwell.js'] = '0' * 64
        with self.assertRaises(ValueError):
            self.selected(changed, self.raw)
        with self.assertRaises(ValueError):
            module._selected_files(self.index, self.raw + b'changed')

    def test_duplicate_missing_extra_and_escape_names(self):
        mutations = [lambda e: e.pop(), lambda e: e.append(('unexpected', b'x', stat.S_IFREG | 0o644, 3)),
                     lambda e: e.__setitem__(0, ('../maxwell.js', *e[0][1:])),
                     lambda e: e.__setitem__(0, ('/maxwell.js', *e[0][1:])),
                     lambda e: e.__setitem__(0, ('maxwell\\maxwell.js', *e[0][1:]))]
        for mutation in mutations:
            index, raw, _ = archive_fixture(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.selected(index, raw)
        index, raw, _ = archive_fixture(duplicate=True)
        with self.assertRaises(ValueError):
            self.selected(index, raw)

    def test_symlink_fifo_dos_and_wrong_sizes(self):
        mutations = [lambda e: e.__setitem__(0, (e[0][0], e[0][1], stat.S_IFLNK | 0o777, 3)),
                     lambda e: e.__setitem__(0, (e[0][0], e[0][1], stat.S_IFIFO | 0o644, 3)),
                     lambda e: e.__setitem__(0, (e[0][0], e[0][1], stat.S_IFREG | 0o4644, 3)),
                     lambda e: e.__setitem__(0, (e[0][0], e[0][1], stat.S_IFREG | 0o644, 0)),
                     lambda e: e.__setitem__(0, (e[0][0], e[0][1][:-1], e[0][2], 3))]
        for mutation in mutations:
            index, raw, _ = archive_fixture(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.selected(index, raw)

    def test_archive_limit_and_ambiguous_json(self):
        with patch.object(module, 'ARCHIVE_LIMIT', len(self.raw) - 1), self.assertRaises(ValueError):
            self.selected(self.index, self.raw)
        with self.assertRaises(ValueError):
            module._json('{"files":{},"files":{}}')

    def test_existing_symlink_parent_and_nested_destinations(self):
        existing = self.directory / 'existing'
        existing.mkdir()
        dangling = self.directory / 'dangling'
        dangling.symlink_to(self.directory / 'absent')
        parent = self.directory / 'linked'
        parent.symlink_to(existing, target_is_directory=True)
        for destination in [existing, dangling, parent / 'new']:
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                module._destination(destination)
        with self.assertRaises(ValueError):
            module.provision(self.directory / 'same', self.directory / 'same')
        with self.assertRaises(ValueError):
            module.provision(self.directory / 'outer', self.directory / 'outer/inner')

    @contextmanager
    def mock_assets(self, guard=None, assets=None, rename=None):
        with patch.object(module, '_reviewed_assets', side_effect=assets or (lambda: (self.index, self.raw, self.binding))) as source, \
             patch.object(module, '_guard', side_effect=guard or (lambda stages, outputs: None)) as guarded:
            if rename is None:
                yield source, guarded
            else:
                with patch.object(module, '_rename_no_replace', side_effect=rename):
                    yield source, guarded

    def test_both_stages_validated_before_synthetic_install(self):
        outputs = [self.directory / 'maxwell', self.directory / 'norsand']
        def guard(stages, verification):
            self.assertEqual(set(stages), {'maxwell', 'norsand'})
            self.assertEqual(set(verification), {'maxwell', 'norsand'})
            self.assertTrue(all(not p.exists() for p in outputs))
            module._verify_staged(stages, self.files)
        with self.mock_assets(guard) as (source, guarded):
            result = module.provision(*outputs)
        self.assertEqual(source.call_count, 2)
        self.assertEqual(guarded.call_count, 1)
        self.assertEqual(result['status'], 'passed')
        for name, data in self.files.items():
            group, relative = name.split('/', 1)
            self.assertEqual((outputs[0 if group == 'maxwell' else 1] / relative).read_bytes(), data)

    def test_guard_rejection_staged_tamper_and_binding_change_leave_no_output(self):
        for case in ['guard', 'tamper', 'binding']:
            outputs = [self.directory / (case + '-m'), self.directory / (case + '-n')]
            def guard(stages, verification):
                if case == 'guard':
                    raise ValueError('synthetic guard rejects')
                if case == 'tamper':
                    (stages['maxwell'] / 'maxwell.js').write_bytes(b'changed')
            calls = 0
            def assets():
                nonlocal calls
                calls += 1
                return self.index, self.raw, self.binding if calls == 1 or case != 'binding' else {'changed': True}
            with self.subTest(case=case), self.mock_assets(guard, assets), self.assertRaises(ValueError):
                module.provision(*outputs)
            self.assertTrue(all(not p.exists() for p in outputs))

    def test_second_destination_check_blocks_race_before_any_rename(self):
        outputs = [self.directory / 'race-m', self.directory / 'race-n']
        def guard(stages, verification):
            outputs[1].mkdir()
        with self.mock_assets(guard), patch.object(module, '_rename_no_replace') as rename, self.assertRaises(ValueError):
            module.provision(*outputs)
        rename.assert_not_called()
        self.assertFalse(outputs[0].exists())
        self.assertTrue(outputs[1].is_dir())

    def test_atomic_no_replace_refuses_concurrent_empty_directory(self):
        source = self.directory / 'source'
        source.mkdir()
        (source / 'marker').write_bytes(b'staged')
        destination = self.directory / 'concurrent'
        destination.mkdir()
        with self.assertRaises(OSError):
            module._rename_no_replace(source, destination)
        self.assertEqual((source / 'marker').read_bytes(), b'staged')
        self.assertEqual(list(destination.iterdir()), [])

    def test_directory_fd_rejects_link_in_any_ancestor(self):
        real = self.directory / 'real-parent'
        (real / 'inner').mkdir(parents=True)
        link = self.directory / 'parent-link'
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaises(OSError):
            module._directory_fd(link / 'inner')

    def test_partial_second_install_failure_is_explicit_and_preserves_verified_first(self):
        outputs = [self.directory / 'partial-m', self.directory / 'partial-n']
        actual = module._rename_no_replace
        calls = 0
        def rename(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                destination.mkdir()
            actual(source, destination)
        with self.mock_assets(rename=rename), self.assertRaisesRegex(RuntimeError, 'already installed verified directories retained'):
            module.provision(*outputs)
        self.assertTrue((outputs[0] / 'maxwell.js').is_file())
        self.assertEqual(list(outputs[1].iterdir()), [])

    def test_real_guard_wrapper_calls_unchanged_both_bundle_entrypoints_only(self):
        called = []
        maxwell = types.ModuleType('tools.build_maxwell_laboratory')
        maxwell.bundle = lambda output, build: called.append(('maxwell', output, build))
        norsand = types.ModuleType('tools.build_controlled_path_web')
        norsand.bundle = lambda output, build: called.append(('norsand', output, build))
        stages = {'maxwell': 'mock-m', 'norsand': 'mock-n'}
        outputs = {'maxwell': 'mock-mo', 'norsand': 'mock-no'}
        with patch.dict(sys.modules, {'tools.build_maxwell_laboratory': maxwell, 'tools.build_controlled_path_web': norsand}):
            module._guard(stages, outputs)
        self.assertEqual(called, [('maxwell', 'mock-mo', 'mock-m'), ('norsand', 'mock-no', 'mock-n')])

    def test_e5_approval_and_index_archive_binding_fail_closed_with_mock_reviewer(self):
        mockroot = self.directory / 'repo'
        def put(name, data):
            path = mockroot / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        review_name = 'catalogue/agent-reviews/synthetic-e5.json'
        approval = {'model_id': module.MODEL, 'review': {'path': review_name}}
        review = {'model': {'id': module.MODEL, 'sha256': module.MODEL_SHA256},
                  'artifacts': [{'path': module.INDEX, 'sha256': ''}, {'path': module.ARCHIVE, 'sha256': module.digest(self.raw)}]}
        raw_index = json.dumps(self.index).encode()
        review['artifacts'][0]['sha256'] = module.digest(raw_index)
        put('catalogue/approved-models.json', json.dumps({'models': [approval]}).encode())
        put(review_name, b'{}')
        put(module.INDEX, raw_index)
        put(module.ARCHIVE, self.raw)
        mock_review = types.ModuleType('atlas.agent_review')
        calls = []
        def validate(path, **kwargs):
            calls.append(kwargs)
            return review
        mock_review.validate_review = validate
        mock_review.approval_entry = lambda *args, **kwargs: approval
        with patch.object(module, 'ROOT', mockroot), patch.object(module, 'INDEX_SHA256', module.digest(raw_index)), patch.dict(sys.modules, {'atlas.agent_review': mock_review}):
            self.assertEqual(module._reviewed_assets()[0], self.index)
            self.assertTrue(calls[-1]['for_approval'])
            self.assertEqual(calls[-1]['root'], mockroot)
            review['artifacts'].pop()
            with self.assertRaises(ValueError):
                module._reviewed_assets()
            put('catalogue/approved-models.json', b'{"models":[]}')
            with self.assertRaises(ValueError):
                module._reviewed_assets()


if __name__ == '__main__':
    unittest.main(verbosity=2)
