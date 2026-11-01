import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from atlas.dsl import ValidationError
from atlas.model import ROOT
from atlas.research import export_database, load_publications, load_screening, validate_publications


class PublicationTests(unittest.TestCase):
    def test_publication_metadata_resolves_to_pinned_source_objects(self):
        graph = load_publications()
        for node in graph['publications']:
            for evidence in node['evidence']:
                obj = json.loads((ROOT / evidence['path']).read_text())
                if evidence['path'] == 'docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json':
                    self.assertEqual(node['doi'], obj['doi'])
                    # Preserve the graph's original Crossref spelling and the supplied original title separately.
                    self.assertEqual(node['title'], 'Nor-Sand: a simle critical state model for sand')
                    self.assertEqual(obj['title'], 'Nor-Sand: a simple critical state model for sand')
                    self.assertEqual(node['authors'], [obj['author']])
                    self.assertEqual(obj['pdf_pages'], 13)
                    self.assertEqual(obj['pages'], '91–103')
                    self.assertFalse(obj['redistribution_authorized'])
                    self.assertEqual(obj['sha256'], 'fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9')
                    self.assertTrue(evidence['locator'])
                    continue
                for part in evidence['locator'].strip('/').split('/'):

                    obj = obj[int(part)] if isinstance(obj, list) else obj[part]
                self.assertEqual(node['doi'], obj['DOI'].strip().lower())
                self.assertEqual(node['title'], obj['title'][0])
        edges = {(e['source'], e['target'], e['relation']) for e in graph['relations']}
        self.assertIn(('doi:10.31224/osf.io/69pgk', 'doi:10.1007/s11440-020-01105-5', 'is-preprint-of'), edges)
        self.assertIn(('doi:10.1007/s11440-017-0605-6', 'doi:10.1007/s11440-017-0550-4', 'corrects'), edges)
        # Full-text identity remains unproven even when metadata links versions.
        nodes = {n['id']: n for n in graph['publications']}
        for edge in graph['relations']:
            if edge['relation'] == 'is-preprint-of':
                self.assertEqual(nodes[edge['source']]['version_role'], 'preprint')
                self.assertEqual(nodes[edge['target']]['version_role'], 'version-of-record')
                self.assertNotEqual(edge['source'], edge['target'])

    def test_corrupt_graph_is_rejected_before_export(self):
        graph = load_publications()
        mutations = [
            lambda g: g['publications'].append(copy.deepcopy(g['publications'][0])),
            lambda g: g['relations'][0].update(target='doi:10.9999/missing'),
            lambda g: g['relations'][0].update(target=g['relations'][0]['source']),
            lambda g: g['relations'].append(copy.deepcopy(g['relations'][0])),
            lambda g: g['publications'][0].update(model_ids=['missing-model']),
            lambda g: g['publications'][0].update(doi=g['publications'][0]['doi'].upper()),
            lambda g: g['publications'][0]['evidence'][0].update(sha256='0' * 64),
        ]
        # Use a DOI containing alphabetic characters for the normalization case.
        graph['publications'].sort(key=lambda n: not any(c.isalpha() for c in n['doi']))
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                bad = copy.deepcopy(graph)
                mutate(bad)
                with self.assertRaises(ValidationError):
                    validate_publications(bad)

    def test_database_retains_distinct_versions_provenance_and_bindings(self):
        graph = load_publications()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'atlas.sqlite'
            for _ in range(2):
                export_database(path)
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                    rows = db.execute('SELECT id,record_json FROM publications').fetchall()
                    expected_records = {r['publication_id']: r for r in load_screening()}
                    expected_records.update({n['id']: n for n in graph['publications']})
                    self.assertEqual(dict((i, json.loads(r)) for i, r in rows), expected_records)
                    rows = db.execute('SELECT record_json FROM publication_relations').fetchall()
                    self.assertCountEqual([json.loads(row[0]) for row in rows], graph['relations'])
                    rows = db.execute('SELECT publication_id,model_id FROM publication_models').fetchall()
                    expected = [(n['id'], m) for n in graph['publications'] for m in n['model_ids']]
                    self.assertCountEqual(rows, expected)
                    self.assertIn(('doi:10.1016/j.jmps.2024.105789', 'terracotta-2024'), rows)
                    self.assertNotIn(('doi:10.2139/ssrn.4699137', 'terracotta-2024'), rows)
