import hashlib
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from atlas.model import ROOT, all_models
from atlas.evidence import checked_receipt
from atlas.research import approved_definitions, export_database


class CatalogueTests(unittest.TestCase):
    def test_directory_coverage_has_resolvable_provenance(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        entries = {e['id']: e for e in manifest['models']}
        self.assertEqual(len(entries), len(manifest['models']))
        coverage = json.loads((ROOT / 'catalogue/discovery/soilmodels-2026-10-30.json').read_text())
        # Frozen directory observation, including family and extension overviews.
        self.assertEqual(len(coverage['entries']), 13)
        self.assertEqual(len({e['url'] for e in coverage['entries']}), 13)
        for record in coverage['entries']:
            self.assertTrue(record['model_ids'])
            for ident in record['model_ids']:
                with self.subTest(directory=record['url'], model=ident):
                    self.assertIn(ident, entries)
                    self.assertIn(record['url'], [s['url'] for s in entries[ident]['catalogue_sources']])
        # Discovery must not advertise candidates as executable definitions.
        definitions = {m['id'] for m in all_models()}
        for entry in entries.values():
            if 'controlled_time_laboratory' in entry:
                self.assert_controlled_time_provenance(entry)
                self.assertNotIn(entry['id'], definitions)
                self.assertTrue(entry['executable'])
                continue
            self.assertEqual(entry['executable'], entry['id'] in definitions)
            if not entry['executable']:
                if any(entry.get(k) for k in ('timed_laboratory', 'material_laboratory', 'path_laboratory', 'implicit_path_laboratory')):
                    self.assert_timed_provenance(entry)
                else:
                    self.assertEqual(entry['status'], 'candidate')
                    if entry['id'] in ('duncan-chang-1970', 'lade-duncan-1975'):
                        realized = {'duncan-chang-1970': 'duncan-chang-1970-endpoint-average', 'lade-duncan-1975': 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'}[entry['id']]
                        self.assertIn(realized, entries)
                        approvals = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
                        records = [a for a in approvals if a['model_id'] == realized and a['status'] == 'approved']
                        self.assertTrue(records)
                        for record in records:
                            path = ROOT / record['definition']['path']
                            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['definition']['sha256'])
                            self.assertEqual(json.loads(path.read_text())['id'], realized)
                        self.assertIn(entry['discovery_url'].lower(), [s['url'].lower() for s in entries[realized].get('catalogue_sources', [])] + [entries[realized]['discovery_url'].lower()])
                    else:
                        self.assertTrue(entry['capability_gap'])

    def assert_controlled_time_provenance(self, entry, approvals=None):
        from atlas.agent_review import approval_entry, validate_review
        from atlas.model import load
        self.assertEqual(entry.get('controlled_time_laboratory'), 'index.html')
        self.assertIs(entry.get('executable'), True)
        self.assertTrue((ROOT / 'web/index.html').is_file())
        self.assertFalse(any(entry.get(key) for key in ('timed_laboratory', 'material_laboratory', 'path_laboratory', 'implicit_path_laboratory')))
        self.assertNotIn(entry['id'], {m['id'] for m in all_models()})
        if approvals is None:
            approvals = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
        records = [record for record in approvals if record['model_id'] == entry['id'] and record['status'] == 'approved']
        self.assertEqual(len(records), 1)
        record = records[0]
        path = ROOT / record['definition']['path']
        self.assertTrue(path.resolve().is_relative_to(ROOT / 'models'))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['definition']['sha256'])
        model = load(path)
        self.assertEqual(model['id'], entry['id'])
        self.assertEqual(model['schema_version'], '0.3')
        self.assertEqual(model['formulation']['equation_form'], 'controlled_ode')
        self.assertEqual(model['formulation']['time_dependence'], 'physical_time')
        self.assertEqual(record['review']['kind'], 'agent-model-review')
        validate_review(ROOT / record['review']['path'], for_approval=True)
        self.assertEqual(record, approval_entry(ROOT / record['review']['path']))
        definitions, _ = approved_definitions()
        self.assertEqual(model, definitions[entry['id']])
        self.assertTrue(record['supporting_files'])
        for pin in record['supporting_files']:
            resolved = checked_receipt(ROOT, record['review']['path'], pin['path'], pin['sha256'])
            self.assertEqual(hashlib.sha256(resolved.read_bytes()).hexdigest(), pin['sha256'])

    def assert_timed_provenance(self, entry, approvals=None):
        self.assertIn(entry['status'], ('numerically-tested', 'reviewed'))
        page = Path(entry.get('material_laboratory') or entry.get('path_laboratory') or entry.get('implicit_path_laboratory') or entry['timed_laboratory'])
        self.assertFalse(page.is_absolute())
        self.assertNotIn('..', page.parts)
        self.assertTrue((ROOT / 'web' / page).is_file())
        if approvals is None:
            approvals = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
        records = [r for r in approvals if r['model_id'] == entry['id'] and r['status'] == 'approved']
        self.assertTrue(records, entry['id'])
        for record in records:
            definition = record['definition']
            path = ROOT / definition['path']
            self.assertTrue(path.resolve().is_relative_to(ROOT))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), definition['sha256'])
            model = json.loads(path.read_text())
            self.assertEqual(model['id'], entry['id'])
            self.assertEqual(model['formulation']['time_dependence'], 'strain_path' if entry.get('material_laboratory') or entry.get('path_laboratory') or entry.get('implicit_path_laboratory') else 'physical_time')
            if entry.get('material_laboratory'):
                self.assertEqual(entry['material_laboratory'], 'index.html')
                self.assertEqual(json.loads((ROOT / entry['approval_record']).read_text()), record)
            if entry.get('path_laboratory') or entry.get('implicit_path_laboratory'):
                from atlas.agent_review import approval_entry, validate_review
                self.assertEqual(entry.get('path_laboratory') or entry.get('implicit_path_laboratory'), 'index.html')
                validate_review(ROOT / record['review']['path'], for_approval=True)
                self.assertEqual(record, approval_entry(ROOT / record['review']['path']))
                self.assertEqual(model['formulation']['equation_form'], 'incremental_residual' if entry.get('implicit_path_laboratory') else 'path_ode')
            self.assertTrue(record['supporting_files'])
            for evidence in record['supporting_files']:
                if (record.get('review', {}).get('kind') == 'agent-model-review' and
                        hashlib.sha256((ROOT / evidence['path']).read_bytes()).hexdigest() != evidence['sha256']):
                    try:
                        path = checked_receipt(ROOT, entry.get('approval_record') or record['review']['path'], evidence['path'], evidence['sha256'])
                    except ValueError as exc:
                        self.fail(str(exc))
                elif entry.get('material_laboratory'):
                    document = entry['approval_record']
                    self.assertEqual(json.loads((ROOT / document).read_text()), record)
                    path = checked_receipt(ROOT, document, evidence['path'], evidence['sha256'])
                else:
                    path = ROOT / evidence['path']
                self.assertTrue(path.resolve().is_relative_to(ROOT))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), evidence['sha256'])

    def test_timed_catalogue_claim_requires_bound_approval_and_evidence(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        entry = next(e for e in manifest['models'] if e.get('timed_laboratory'))
        records = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
        records = [r for r in records if r['model_id'] == entry['id']]
        with self.assertRaises(AssertionError):
            self.assert_timed_provenance(entry, [])
        for key in ('definition', 'supporting_files'):
            corrupted = copy.deepcopy(records)
            for record in corrupted:
                target = record[key] if key == 'definition' else record[key][0]
                target['sha256'] = '0' * 64
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.assert_timed_provenance(entry, corrupted)

    def test_material_point_route_requires_exact_approval(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        entry = next(e for e in manifest['models'] if e.get('material_laboratory'))
        record = json.loads((ROOT / entry['approval_record']).read_text())
        self.assert_timed_provenance(entry, [record])
        for corrupted in ([], [{**record, 'status': 'candidate'}], [{**record, 'scope': 'forged broader scope'}]):
            with self.assertRaises(AssertionError):
                self.assert_timed_provenance(entry, corrupted)

    def test_controlled_path_route_requires_exact_approval(self):
        entry = next(e for e in json.loads((ROOT / 'catalogue/manifest.json').read_text())['models'] if e.get('path_laboratory'))
        records = [r for r in json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models'] if r['model_id'] == entry['id']]
        self.assert_timed_provenance(entry, records)
        for corrupted in ([], [{**records[0], 'status': 'candidate'}], [{**records[0], 'scope': {'use': 'forged broader scope'}}]):
            with self.assertRaises(AssertionError):
                self.assert_timed_provenance(entry, corrupted)

    def test_implicit_path_route_requires_exact_approval(self):
        entry = next(e for e in json.loads((ROOT / 'catalogue/manifest.json').read_text())['models'] if e.get('implicit_path_laboratory'))
        records = [r for r in json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models'] if r['model_id'] == entry['id']]
        self.assert_timed_provenance(entry, records)
        for corrupted in ([], [{**records[0], 'status': 'candidate'}], [{**records[0], 'scope': {'use': 'forged broader scope'}}]):
            with self.assertRaises(AssertionError):
                self.assert_timed_provenance(entry, corrupted)

    def test_database_keeps_candidate_and_executable_sources(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'atlas.sqlite'
            # Re-export must be idempotent rather than accumulating citations.
            for _ in range(2):
                export_database(path)
                with sqlite3.connect(path) as db:
                    self.assertEqual({r[0] for r in db.execute('SELECT id FROM models')},
                                     {e['id'] for e in manifest['models']} | set(approved_definitions()[0]))
                    for entry in manifest['models']:
                        urls = {r[0] for r in db.execute('SELECT url FROM sources WHERE model_id=?', (entry['id'],))}
                        expected = [s['url'] for s in entry.get('catalogue_sources', []) + entry.get('research_sources', [])]
                        if entry.get('discovery_url'):
                            expected.append(entry['discovery_url'])
                        self.assertTrue(set(expected) <= urls, entry['id'])
                    ordinary = {model['id'] for model in all_models()}
                    approved, approvals = approved_definitions()
                    candidates = {entry['id'] for entry in manifest['models']} - ordinary - set(approved)
                    self.assertTrue(candidates, 'True candidate rows must be tested')
                    for entry in manifest['models']:
                        row = db.execute('SELECT executable,definition_json FROM models WHERE id=?', (entry['id'],)).fetchone()
                        self.assertEqual(row[0], int(entry['id'] in ordinary))
                        if entry['id'] not in ordinary and entry['id'] not in approved:
                            self.assertEqual(row, (0, None), entry['id'])
                        if entry.get('controlled_time_laboratory'):
                            self.assert_controlled_time_provenance(entry, approvals)
                            self.assertEqual(json.loads(row[1]), approved[entry['id']])
                            records = [a for a in approvals if a['model_id'] == entry['id']]
                            self.assertEqual(len(records), 1)
                            approval = records[0]
                            stored = db.execute('SELECT record_json FROM model_approvals WHERE id=?', (approval['id'],)).fetchone()
                            self.assertEqual(json.loads(stored[0]), approval)
                            stored = db.execute('SELECT record_json FROM agent_reviews WHERE id=?', (json.loads((ROOT / approval['review']['path']).read_text())['id'],)).fetchone()
                            self.assertEqual(json.loads(stored[0]), json.loads((ROOT / approval['review']['path']).read_text()))
                    elastic = next(m for m in all_models() if m['id'] == 'linear-elastic')
                    urls = {r[0] for r in db.execute('SELECT url FROM sources WHERE model_id=?', ('linear-elastic',))}
                    self.assertTrue({s['url'] for s in elastic['sources']} <= urls)
                    count = db.execute('SELECT COUNT(*) FROM sources').fetchone()[0]
                    if _:
                        self.assertEqual(count, prior_count)
                    prior_count = count

    def test_controlled_time_route_requires_exact_approved_profile(self):
        entry = next(e for e in json.loads((ROOT / 'catalogue/manifest.json').read_text())['models'] if e.get('controlled_time_laboratory'))
        records = [r for r in json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models'] if r['model_id'] == entry['id']]
        self.assert_controlled_time_provenance(entry, records)
        for corrupted in ([], [{**records[0], 'status': 'candidate'}], [{**records[0], 'scope': {'use': 'forged'}}], [{**records[0], 'definition': {**records[0]['definition'], 'sha256': '0' * 64}}], [{**records[0], 'review': {**records[0]['review'], 'sha256': '0' * 64}}]):
            with self.subTest(approval=corrupted), self.assertRaises((AssertionError, ValueError)):
                self.assert_controlled_time_provenance(entry, corrupted)
        for change in ({'controlled_time_laboratory': 'other.html'}, {'controlled_time_laboratory': None}, {'executable': False}, {'id': 'unknown'}, {'id': 'linear-elastic'}, {'path_laboratory': 'index.html'}):
            with self.subTest(change=change), self.assertRaises((AssertionError, ValueError)):
                self.assert_controlled_time_provenance({**entry, **change}, records)
