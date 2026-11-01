"""Public download package is source-linked and matches the website catalogue."""
from contextlib import closing
import copy
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import json
from pathlib import Path
import sqlite3
import shutil
import threading
import urllib.request
import tempfile
import unittest
from unittest.mock import patch

from atlas.model import all_models
from tools import build_database as package


class DatabasePackage(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.site = Path(self.temporary.name)
        self.models = all_models()
        self.write('models.json', {'models': self.models})
        self.catalogue = json.loads((package.ROOT / 'catalogue/manifest.json').read_text())
        self.write('catalogue.json', self.catalogue)

    def write(self, name, value):
        (self.site / name).write_text(json.dumps(value, indent=2) + '\n')

    def artifacts(self):
        return {name: (self.site / name).read_bytes() for name in (package.DATABASE, package.MANIFEST)}

    def test_public_download_preserves_definitions_sources_and_exact_approval_records(self):
        manifest = package.bundle(self.site)
        raw = (self.site / package.DATABASE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['database']['sha256'])
        self.assertEqual(len(raw), manifest['database']['bytes'])
        self.assertEqual(json.loads((self.site / package.MANIFEST).read_text()), manifest)
        self.assertFalse(manifest['measurements_included'])
        self.assertFalse(manifest['source_documents_included'])
        self.assertFalse(manifest['compiled_engines_included'])
        self.assertEqual(set(manifest['ordinary_engine_model_ids']), {m['id'] for m in self.models})
        with closing(sqlite3.connect(self.site / package.DATABASE)) as connection:
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchall(), [('ok',)])
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            for model in self.models:
                definition, executable = connection.execute(
                    'SELECT definition_json,executable FROM models WHERE id=?', (model['id'],)).fetchone()
                self.assertEqual(json.loads(definition), model)
                self.assertEqual(executable, 1)
                rows = set(connection.execute('SELECT url,locator,role FROM sources WHERE model_id=?', (model['id'],)))
                for source in model['sources']:
                    self.assertIn((source['url'], source['locator'], source['role']), rows)
            actual = {mid: json.loads(raw) for mid, raw in connection.execute('SELECT id,record_json FROM model_approvals')}
        registry = json.loads((package.ROOT / 'catalogue/approved-models.json').read_text())
        self.assertEqual(actual, {a['id']: a for a in registry['models'] if a['status'] == 'approved'})
        self.assertEqual({p.name for p in self.site.iterdir()},
                         {'models.json', 'catalogue.json', package.DATABASE, package.MANIFEST})
        repeated = package.bundle(self.site)
        self.assertEqual(manifest['counts'], repeated['counts'])
        self.assertEqual(manifest['source_inputs'], repeated['source_inputs'])

    def test_stale_missing_duplicate_or_changed_models_leave_prior_downloads(self):
        package.bundle(self.site)
        before = self.artifacts()
        changed = copy.deepcopy(self.models)
        changed[0]['name'] += ' altered'
        for values in (self.models[:-1], self.models + self.models[:1], changed, None):
            with self.subTest(case=type(values).__name__):
                self.write('models.json', {'models': values})
                with self.assertRaises(ValueError):
                    package.bundle(self.site)
                self.assertEqual(self.artifacts(), before)
        (self.site / 'models.json').unlink()
        with self.assertRaises(FileNotFoundError):
            package.bundle(self.site)
        self.assertEqual(self.artifacts(), before)

    def test_changed_discovery_catalogue_rejects(self):
        altered = copy.deepcopy(self.catalogue)
        altered['models'].pop()
        self.write('catalogue.json', altered)
        with self.assertRaisesRegex(ValueError, 'discovery catalogue differ'):
            package.bundle(self.site)
        self.assertFalse((self.site / package.DATABASE).exists())

    def test_input_drift_during_export_retains_old_downloads(self):
        package.bundle(self.site)
        before = self.artifacts()
        original = package.export_database
        def drift(path):
            result = original(path)
            (self.site / 'models.json').write_text('{}')
            return result
        with patch.object(package, 'export_database', drift), self.assertRaisesRegex(ValueError, 'inputs changed'):
            package.bundle(self.site)
        self.assertEqual(self.artifacts(), before)

    def test_catalogue_drift_before_initial_source_hash_capture_rejects(self):
        package.bundle(self.site)
        before = self.artifacts()
        original = package._source_inputs
        calls = 0
        def drift(ordinary, approvals):
            nonlocal calls
            calls += 1
            if calls == 1:
                altered = copy.deepcopy(self.catalogue)
                altered['models'].pop()
                self.write('catalogue.json', altered)
            return original(ordinary, approvals)
        with patch.object(package, '_source_inputs', drift), self.assertRaisesRegex(ValueError, 'inputs changed'):
            package.bundle(self.site)
        self.assertEqual(self.artifacts(), before)

    def test_source_catalogue_capture_must_match_compared_bytes(self):
        original = package._source_inputs
        def changed_hash(ordinary, approvals):
            hashes = original(ordinary, approvals)
            hashes['catalogue/manifest.json'] = '0' * 64
            return hashes
        with patch.object(package, '_source_inputs', changed_hash), self.assertRaisesRegex(ValueError, 'source catalogue changed'):
            package.bundle(self.site)
        self.assertFalse((self.site / package.DATABASE).exists())

    def test_second_publish_failure_restores_previous_pair_or_absence(self):
        original = Path.replace
        def failure(path, target):
            if path.name == package.MANIFEST and path.parent != self.site:
                raise OSError('injected manifest publication failure')
            return original(path, target)
        with patch.object(Path, 'replace', failure), self.assertRaisesRegex(OSError, 'injected'):
            package.bundle(self.site)
        self.assertFalse((self.site / package.DATABASE).exists())
        self.assertFalse((self.site / package.MANIFEST).exists())
        package.bundle(self.site)
        # A distinct but legal prior SQLite file makes rollback observable.
        database = self.site / package.DATABASE
        database.write_bytes(database.read_bytes() + b'\n')
        manifest = json.loads((self.site / package.MANIFEST).read_text())
        manifest['database']['sha256'] = hashlib.sha256(database.read_bytes()).hexdigest()
        manifest['database']['bytes'] = database.stat().st_size
        self.write(package.MANIFEST, manifest)
        before = self.artifacts()
        with patch.object(Path, 'replace', failure), self.assertRaisesRegex(OSError, 'injected'):
            package.bundle(self.site)
        self.assertEqual(self.artifacts(), before)

    def test_added_ordinary_membership_during_export_rejects(self):
        calls = 0
        def models():
            nonlocal calls
            calls += 1
            return self.models if calls == 1 else self.models[:-1]
        with patch.object(package, 'all_models', models), self.assertRaisesRegex(ValueError, 'membership changed'):
            package.bundle(self.site)
        self.assertFalse((self.site / package.DATABASE).exists())

    def test_unexpected_table_or_altered_review_cannot_be_published(self):
        package.bundle(self.site)
        before = self.artifacts()
        original = package.export_database
        for alteration, message in (
            ('CREATE TABLE raw_measurements(sample REAL)', 'unsupported public table set'),
            ("UPDATE agent_reviews SET record_json='{}'", 'agent review records'),
            ('DELETE FROM sources', 'source provenance'),
        ):
            def altered(path):
                result = original(path)
                with closing(sqlite3.connect(path)) as connection:
                    connection.execute(alteration)
                    connection.commit()
                return result
            with self.subTest(alteration=alteration), patch.object(package, 'export_database', altered):
                with self.assertRaisesRegex(ValueError, message):
                    package.bundle(self.site)
                self.assertEqual(self.artifacts(), before)

    def test_download_links_resolve_under_a_project_path_with_matching_bytes(self):
        package.bundle(self.site)
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = {}
            def handle_starttag(self, tag, attrs):
                values = dict(attrs)
                if tag == 'a' and values.get('href') in (package.DATABASE, package.MANIFEST):
                    self.links[values['href']] = values
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / 'constitutive-atlas'
            project.mkdir()
            for name in (package.DATABASE, package.MANIFEST):
                shutil.copyfile(self.site / name, project / name)
            shutil.copyfile(package.ROOT / 'web/index.html', project / 'index.html')
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=root))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f'http://127.0.0.1:{server.server_port}/constitutive-atlas/'
                with urllib.request.urlopen(base) as response:
                    parser = Links()
                    parser.feed(response.read().decode())
                self.assertEqual(set(parser.links), {package.DATABASE, package.MANIFEST})
                self.assertEqual(parser.links[package.DATABASE]['download'], 'constitutive-atlas.sqlite')
                with urllib.request.urlopen(base + package.DATABASE) as response:
                    database = response.read()
                with urllib.request.urlopen(base + package.MANIFEST) as response:
                    manifest = json.load(response)
                self.assertTrue(database.startswith(b'SQLite format 3\x00'))
                self.assertEqual(hashlib.sha256(database).hexdigest(), manifest['database']['sha256'])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == '__main__':
    unittest.main()
