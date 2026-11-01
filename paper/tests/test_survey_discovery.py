import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.survey_discovery import (audit_searches, discovery_queue, normalize_doi,
                                       validate_citation_followup, validate_full_text_screening,
                                       validate_title_screening)


class BibliographicIdentityTests(unittest.TestCase):
    def test_doi_normalization_preserves_suffix_punctuation(self):
        self.assertEqual(normalize_doi(' https://DOI.org/10.1002/%28SICI%29ABC;2-3 '), '10.1002/(sici)abc;2-3')
        self.assertEqual(normalize_doi('doi: 10.1234/ABC.'), '10.1234/abc.')
        self.assertIsNone(normalize_doi(None))
        self.assertIsNone(normalize_doi('not a DOI'))

    def test_occurrences_and_conflicts_retained_under_same_doi(self):
        queue, counts = discovery_queue([('a', [dict(DOI='10.1234/ABC', title=['Title'])]),
                                       ('b', [dict(DOI='https://doi.org/10.1234/abc', title=['Other title'])])])
        self.assertEqual(len(queue), 1)
        self.assertEqual(counts['returned_occurrences'], 2)
        self.assertEqual(len(queue[0]['metadata_variants']), 2)
        self.assertTrue(queue[0]['metadata_review_needed'])
        self.assertEqual(queue[0]['stage'], 'unscreened')
        self.assertEqual(queue[0]['screening_decisions'], [])

    def test_same_title_different_doi_is_not_automatically_merged(self):
        queue, counts = discovery_queue([('a', [dict(DOI='10.1234/a', title=['Same']),
                                               dict(DOI='10.1234/b', title=['Same'])])])
        self.assertEqual(len(queue), 2)
        self.assertEqual(counts['distinct_normalized_doi_identifiers'], 2)
        self.assertEqual(counts['same_title_cross_identifier_groups'], 1)
        self.assertEqual(queue[0]['same_title_other_publication_ids'], ['doi:10.1234/b'])
        self.assertTrue(queue[0]['metadata_review_needed'])

    def test_no_doi_match_is_provisional_and_incomplete_records_stay_separate(self):
        item = dict(title=['A title'], author=[dict(given='A', family='Researcher')],
                    published={'date-parts': [[2000]]})
        other = copy.deepcopy(item)
        other['title'] = [' A TITLE ']
        queue, counts = discovery_queue([('a', [item, other, dict(title=['Unknown']), dict(title=['Unknown'])])])
        self.assertEqual(len(queue), 3)
        self.assertEqual(counts['possible_no_doi_metadata_groups'], 1)
        self.assertEqual(counts['incomplete_metadata_occurrences'], 2)
        self.assertTrue(all(q['metadata_review_needed'] for q in queue))


class DiscoveryRequestTests(unittest.TestCase):
    def fixture(self, directory, fail=False):
        protocol = read_json(ROOT/'paper/study/survey_protocol.json')
        protocol['bibliographic_pilot']['queries'] = protocol['bibliographic_pilot']['queries'][:1]
        path = directory/'protocol.json'
        write_json(path, protocol)
        spec = importlib.util.spec_from_file_location('fetch_survey', ROOT/'paper/scripts/fetch_survey_discovery.py')
        fetcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetcher)
        raw = b'{"status":"ok", "message-type":"work-list", "message":{"items":[{"DOI":"10.1234/a","title":["Soil law"],"score":2}]}}\n'

        def curl(args, **kwargs):
            if not fail:
                Path(args[args.index('--output')+1]).write_bytes(raw)
                Path(args[args.index('--dump-header')+1]).write_text('HTTP/2 200\n')
            return subprocess.CompletedProcess(args, 6 if fail else 0, '', 'deliberate network failure' if fail else '')

        output = directory/'raw'
        with patch.object(fetcher, 'ROOT', directory), patch.object(fetcher.subprocess, 'run', side_effect=curl):
            if fail:
                with self.assertRaises(RuntimeError):
                    fetcher.fetch(path, output)
                return path, output
            fetcher.fetch(path, output)
        self.assertEqual((output/'soil.json').read_bytes(), raw)
        return path, output

    def test_request_and_original_bytes_are_audited_without_screening(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            protocol, output = self.fixture(directory)
            with patch('analysis.survey_discovery.ROOT', directory):
                report = audit_searches(output/'manifest.json', protocol)
            self.assertEqual(report['counts']['returned_occurrences'], 1)
            self.assertEqual(report['queue'][0]['stage'], 'unscreened')
            self.assertTrue(report['batch_checks'][0]['finite_descending_scores'])

    def test_changed_order_or_original_response_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            protocol, output = self.fixture(directory)
            manifest = read_json(output/'manifest.json')
            manifest['batches'][0]['request_url'] = manifest['batches'][0]['request_url'].replace('sort=score', 'sort=published')
            write_json(output/'manifest.json', manifest)
            with patch('analysis.survey_discovery.ROOT', directory):
                with self.assertRaisesRegex(ValueError, 'ordering'):
                    audit_searches(output/'manifest.json', protocol)
                manifest['batches'][0]['request_url'] = manifest['batches'][0]['request_url'].replace('sort=published', 'sort=score')
                write_json(output/'manifest.json', manifest)
                (output/'soil.json').write_text('{}')
                with self.assertRaisesRegex(ValueError, 'response or headers changed'):
                    audit_searches(output/'manifest.json', protocol)

    def test_network_failure_cannot_become_completed_search(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            protocol, output = self.fixture(directory, fail=True)
            self.assertTrue((output/'failure.json').exists())
            with self.assertRaisesRegex(ValueError, 'completed bounded discovery'):
                audit_searches(output/'manifest.json', protocol)


class ScreeningBoundaryTests(unittest.TestCase):
    def test_title_metadata_cannot_establish_formulation_or_independent_review(self):
        protocol = read_json(ROOT/'paper/study/survey_protocol.json')
        original = read_json(ROOT/'paper/study/survey_screening.json')
        validate_title_screening(original, protocol)
        for key, value in [('decision', 'include_exact_formulation'), ('formulation_ids', ['invented']),
                           ('independent_review_status', 'reviewed')]:
            ledger = copy.deepcopy(original)
            ledger['records'][0][key] = value
            with self.assertRaisesRegex(ValueError, 'cannot establish'):
                validate_title_screening(ledger, protocol)

    def test_wrong_source_occurrence_rejected(self):
        protocol = read_json(ROOT/'paper/study/survey_protocol.json')
        ledger = read_json(ROOT/'paper/study/survey_screening.json')
        ledger['records'] = ledger['records'][:1]
        publication = dict(publication_id=ledger['records'][0]['publication_id'], occurrences=[])
        with self.assertRaisesRegex(ValueError, 'another publication'):
            validate_title_screening(ledger, protocol, [publication])


class FullTextScreeningTests(unittest.TestCase):
    def fixture(self):
        return (read_json(ROOT/'paper/study/survey_full_text_screening.json'),
                read_json(ROOT/'paper/study/survey_protocol.json'))

    def test_supplementary_non_doi_criterion_needs_no_atlas_formulation(self):
        ledger, protocol = self.fixture()
        rows = validate_full_text_screening(ledger, protocol)
        self.assertIsNone(rows[0]['bibliography']['doi'])
        self.assertIsNone(rows[0]['discovery']['crossref_pilot_occurrence'])
        self.assertEqual(rows[0]['formulation_ids'], [])
        self.assertTrue(rows[0]['criterion_ids'])

    def test_criterion_cannot_be_counted_as_a_constitutive_formulation(self):
        ledger, protocol = self.fixture()
        ledger['records'][0]['formulation_ids'] = ['invented-law']
        with self.assertRaisesRegex(ValueError, 'exact-formulation'):
            validate_full_text_screening(ledger, protocol)

    def test_metadata_and_incomplete_text_cannot_support_full_text_decision(self):
        for change in ('metadata', 'pages', 'locator'):
            ledger, protocol = self.fixture()
            row = ledger['records'][0]
            if change == 'metadata':
                row['access_level'] = 'bibliographic_metadata_title_only'
            elif change == 'pages':
                row['source']['text_screened_pdf_pages'] = [3, 4]
            else:
                row['evidence_locator'][0]['pdf_pages'] = [100]
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_full_text_screening(ledger, protocol)

    def test_assisted_decision_cannot_certify_review_or_benchmark_admission(self):
        for field, value in [('independent_review_status', 'reviewed'),
                             ('benchmark_admission', 'admitted')]:
            ledger, protocol = self.fixture()
            ledger['records'][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'cannot certify'):
                validate_full_text_screening(ledger, protocol)

    def test_changed_source_rejected_and_missing_copy_remains_an_access_gap(self):
        ledger, protocol = self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'primary.pdf'
            source.write_bytes(b'original source snapshot')
            row = ledger['records'][0]
            row['source']['local_copy'] = str(source)
            row['source']['sha256'] = digest(source)
            validate_full_text_screening(ledger, protocol)
            source.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError, 'differs from reviewed snapshot'):
                validate_full_text_screening(ledger, protocol)
            source.unlink()
            validate_full_text_screening(ledger, protocol)

    def test_partial_followup_cannot_become_reviewed_or_admitted(self):
        for key, value in [('formulation_ids', ['invented']),
                           ('independent_review_status', 'reviewed'),
                           ('benchmark_admission', 'admitted')]:
            ledger, _ = self.fixture()
            followup = ledger['records'][0]['citation_tracing_followups'][0]
            followup[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_citation_followup(followup)

    def test_followup_archive_must_contain_exact_reviewed_pdf(self):
        import zipfile
        ledger, _ = self.fixture()
        followup = ledger['records'][0]['citation_tracing_followups'][0]
        with tempfile.TemporaryDirectory() as folder:
            source = followup['source']
            pdf, archive = Path(folder)/'source.pdf', Path(folder)/'archive.zip'
            pdf.write_bytes(b'reviewed PDF')
            source['local_copy'], source['archive_path'] = str(pdf), str(archive)
            source['sha256'] = digest(pdf)
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr(source['archive_member'], pdf.read_bytes())
            source['archive_sha256'] = digest(archive)
            validate_citation_followup(followup)
            # Even a re-pinned archive cannot silently supply another PDF.
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr(source['archive_member'], b'another PDF')
            source['archive_sha256'] = digest(archive)
            with self.assertRaisesRegex(ValueError, 'archive member differs'):
                validate_citation_followup(followup)
            archive.write_bytes(b'changed archive')
            with self.assertRaisesRegex(ValueError, 'archive differs'):
                validate_citation_followup(followup)


if __name__ == '__main__':
    unittest.main()
