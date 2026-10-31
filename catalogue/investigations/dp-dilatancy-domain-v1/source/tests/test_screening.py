"""Offline provenance checks; these do not judge scientific relevance."""
import hashlib
import json
from collections import Counter
import unittest

from atlas.model import ROOT
from atlas.structure import check


class ScreeningTests(unittest.TestCase):
    def test_ledger_links_every_discovery_occurrence_exactly_once(self):
        schema = json.loads((ROOT / 'schemas/screening.schema.json').read_text())
        records = [json.loads(line) for line in (ROOT / 'catalogue/screening.jsonl').read_text().splitlines()]
        expected = {}
        for path in sorted((ROOT / 'catalogue/discovery').glob('crossref-*.json')):
            raw = path.read_bytes()
            batch = json.loads(raw)
            for i, item in enumerate(batch['response']['message']['items']):
                key = (str(path.relative_to(ROOT)), f'/response/message/items/{i}')
                expected[key] = (item, hashlib.sha256(raw).hexdigest(), batch['url'])

        seen = set()
        publications = set()
        model_ids = {m['id'] for m in json.loads((ROOT / 'catalogue/manifest.json').read_text())['models']}
        for record in records:
            check(record, schema)
            doi = record['doi']
            self.assertEqual(doi, doi.strip().lower())
            self.assertEqual(record['publication_id'], 'doi:' + doi)
            self.assertEqual(record['url'], 'https://doi.org/' + doi)
            self.assertNotIn(doi, publications)
            publications.add(doi)
            self.assertTrue(set(record['model_ids']) <= model_ids)
            # AI-assisted first-pass decisions cannot sign off their own review.
            if record['reviewer'].startswith('Codex'):
                self.assertEqual(record['independent_review'], 'pending')
            if record['full_text_reviewed']:
                self.assertEqual(record['screening_basis'], 'full-text')
            for evidence in record['evidence']:
                key = (evidence['path'], evidence['locator'])
                self.assertNotIn(key, seen)
                seen.add(key)
                item, digest, url = expected[key]
                self.assertEqual(evidence['sha256'], digest)
                self.assertEqual(evidence['url'], url)
                self.assertEqual(item['DOI'].strip().lower(), doi)
                self.assertEqual(item['title'][0], record['title'])
                self.assertEqual(item.get('container-title', []), record['containers'])
        self.assertEqual(seen, set(expected))

    def test_initial_screening_snapshot_reconciles_without_admitting_models(self):
        records = [json.loads(line) for line in (ROOT / 'catalogue/screening.jsonl').read_text().splitlines()]
        original = [r for r in records if any('crossref-soil-' in e['path'] or 'crossref-rock-' in e['path'] for e in r['evidence'])]
        self.assertEqual(len(original), 34)
        self.assertEqual(sum(len(r['evidence']) for r in original), 50)
        self.assertEqual(Counter(r['decision'] for r in original), {'exclude': 34})
        for record in original:
            self.assertEqual(record['model_ids'], [])
            self.assertFalse(record['full_text_reviewed'])
        snapshot = [r for r in records if r['reviewed_at'] == '2026-10-31']
        self.assertEqual(Counter(r['decision'] for r in snapshot), {'exclude': 34, 'include-for-full-text': 1, 'unresolved': 2})
        by_doi = {r['doi']: r for r in records}
        self.assertEqual(by_doi['10.1002/nag.1610181203']['decision'], 'include-for-full-text')
        # Identical titles with distinct DOIs must survive DOI deduplication.
        a, b = (by_doi['10.1067/mtc.2000.' + suffix] for suffix in ('109245', '109246'))
        self.assertEqual(a['title'], b['title'])
        self.assertNotEqual(a['publication_id'], b['publication_id'])
