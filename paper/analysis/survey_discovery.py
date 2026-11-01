"""Bibliographic identity and request audit, separate from scientific screening."""
import hashlib
import html
import math
import re
import unicodedata
import zipfile
from urllib.parse import parse_qs, unquote, urlsplit

from .common import ROOT, digest, read_json


def normalize_doi(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    resolver = re.match(r'https?://(?:dx\.)?doi\.org/', value, re.IGNORECASE)
    if resolver:
        value = unquote(value[resolver.end():])
    value = re.sub(r'^doi:\s*', '', value, flags=re.IGNORECASE).strip().casefold()
    if not re.fullmatch(r'10\.\d{4,9}/\S+', value):
        return None
    return value


def normalized_text(value):
    return ' '.join(unicodedata.normalize('NFKC', html.unescape(value)).casefold().split())


def bibliographic_fields(item):
    titles = item.get('title', [])
    if not isinstance(titles, list) or any(not isinstance(t, str) for t in titles):
        raise ValueError('unsupported bibliographic title metadata')
    authors = [' '.join(part for part in (a.get('given', ''), a.get('family', '')) if part)
               or a.get('name', '') for a in item.get('author', [])]
    year = None
    for field in ('published', 'issued', 'published-online', 'published-print'):
        parts = item.get(field, {}).get('date-parts', [])
        if parts and parts[0] and isinstance(parts[0][0], int):
            year = parts[0][0]
            break
    return dict(titles=titles, authors=authors, year=year, publication_type=item.get('type'))


def publication_key(item, occurrence_id):
    doi = normalize_doi(item.get('DOI', ''))
    if doi:
        return 'doi:'+doi, 'normalized_doi', doi
    fields = bibliographic_fields(item)
    if fields['titles'] and fields['authors'] and all(fields['authors']) and fields['year']:
        signature = repr((tuple(normalized_text(t) for t in fields['titles']),
                          tuple(normalized_text(a) for a in fields['authors']), fields['year']))
        return 'possible-metadata-match:'+hashlib.sha256(signature.encode()).hexdigest()[:24], 'possible_metadata_duplicate_not_confirmed', None
    return 'occurrence:'+occurrence_id, 'incomplete_metadata_not_merged', None


def discovery_queue(batches):
    groups = {}
    occurrences = 0
    for batch_id, items in batches:
        for index, item in enumerate(items):
            occurrence = f'{batch_id}:{index}'
            key, identity, doi = publication_key(item, occurrence)
            fields = bibliographic_fields(item)
            if key not in groups:
                groups[key] = dict(publication_id=key, identity_basis=identity, normalized_doi=doi,
                                   stage='unscreened', screening_decisions=[], metadata_variants=[], occurrences=[])
            group = groups[key]
            if fields not in group['metadata_variants']:
                group['metadata_variants'].append(fields)
            group['occurrences'].append(dict(batch_id=batch_id, item_index=index,
                                              supplied_doi=item.get('DOI'), score=item.get('score')))
            occurrences += 1
    queue = list(groups.values())
    titles_to_ids = {}
    for group in queue:
        for variant in group['metadata_variants']:
            for title in variant['titles']:
                normalized = normalized_text(title)
                if normalized:
                    titles_to_ids.setdefault(normalized, set()).add(group['publication_id'])
    for group in queue:
        related = set()
        for variant in group['metadata_variants']:
            for title in variant['titles']:
                related.update(titles_to_ids.get(normalized_text(title), set()))
        related.discard(group['publication_id'])
        group['same_title_other_publication_ids'] = sorted(related)
        group['metadata_review_needed'] = bool(related) or len(group['metadata_variants']) > 1 or group['identity_basis'] != 'normalized_doi'
    return queue, dict(returned_occurrences=occurrences,
        distinct_normalized_doi_identifiers=sum(g['identity_basis'] == 'normalized_doi' for g in queue),
        possible_no_doi_metadata_groups=sum(g['identity_basis'] == 'possible_metadata_duplicate_not_confirmed' for g in queue),
        incomplete_metadata_occurrences=sum(g['identity_basis'] == 'incomplete_metadata_not_merged' for g in queue),
        repeated_occurrences_within_groups=occurrences-len(queue),
        same_title_cross_identifier_groups=sum(len(ids) > 1 for ids in titles_to_ids.values()),
        metadata_groups_requiring_review=sum(g['metadata_review_needed'] for g in queue))


def audit_searches(manifest_path, protocol_path):
    manifest, protocol = read_json(manifest_path), read_json(protocol_path)
    if (manifest['protocol_id'] != protocol['id'] or manifest['protocol_sha256'] != digest(protocol_path)
            or manifest['status'] != 'completed_bounded_development_discovery_not_survey_completion'):
        raise ValueError('completed bounded discovery with matching protocol required')
    search = protocol['bibliographic_pilot']
    queries = {q['id']: q for q in search['queries']}
    if len(queries) != len(search['queries']):
        raise ValueError('duplicate declared query IDs')
    if len(manifest['batches']) != len(queries) or {b['id'] for b in manifest['batches']} != set(queries):
        raise ValueError('missing or duplicate search batch')
    directories = {str((ROOT/b['raw_path']).parent) for b in manifest['batches']}
    if len(directories) != 1:
        raise ValueError('bounded discovery must retain one original source directory')
    from pathlib import Path
    source_directory = Path(next(iter(directories)))
    if (digest(source_directory/'protocol.json') != manifest['protocol_sha256'] or
            digest(source_directory/'fetch_script.py') != manifest['fetch_script_sha256']):
        raise ValueError('archived discovery protocol or fetch code changed')
    batches, checks = [], []
    for batch in manifest['batches']:
        query = queries[batch['id']]
        parts = urlsplit(batch['request_url'])
        params = parse_qs(parts.query, keep_blank_values=True)
        expected = {k: [str(v)] for k, v in dict(search['parameters'], **{'query.bibliographic': query['query']}).items()}
        if (parts.scheme+'://'+parts.netloc+parts.path != search['endpoint'] or params != expected
                or batch['query'] != query['query'] or batch['screening_status'] != 'unscreened'):
            raise ValueError('request does not match declared query, ordering or cutoff')
        raw, headers = ROOT/batch['raw_path'], ROOT/batch['headers_path']
        if digest(raw) != batch['raw_sha256'] or digest(headers) != batch['headers_sha256']:
            raise ValueError('raw discovery response or headers changed')
        response = read_json(raw)
        if response.get('status') != 'ok' or response.get('message-type') != 'work-list':
            raise ValueError('unexpected discovery response')
        items = response['message']['items']
        if len(items) != batch['returned_records'] or len(items) > search['parameters']['rows']:
            raise ValueError('discovery response count mismatch')
        scores = [item.get('score') for item in items]
        finite = all(isinstance(s, (int, float)) and math.isfinite(s) for s in scores)
        checks.append(dict(id=batch['id'], returned_records=len(items),
            finite_descending_scores=finite and all(a >= b for a, b in zip(scores, scores[1:])),
            first_titles=[item.get('title', []) for item in items[:3]], screening_status='unscreened'))
        batches.append((batch['id'], items))
    queue, counts = discovery_queue(batches)
    return dict(paper_record_version=1, status='audited_bounded_discovery_not_scientific_screening',
                manifest_sha256=digest(manifest_path), protocol_sha256=digest(protocol_path),
                analysis_sha256=digest(__file__), counts=counts, batch_checks=checks, queue=queue,
                limits=['DOI groups and possible metadata matches are not constitutive formulation counts.',
                        'Scores and first titles diagnose retrieval ordering, not relevance admission.',
                        'No record has been scientifically screened by this script.',
                        'One page per theme and incomplete supplementary routes do not establish survey completeness.'])


def validate_title_screening(ledger, protocol, publications=None, batches=None):
    if (ledger['status'] != 'assisted_title_screening_pilot_not_final_survey'
            or ledger['protocol_id'] != protocol['id']):
        raise ValueError('unsupported screening pilot status')
    rows = ledger['records']
    if len({r['publication_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate publication in pilot title screening')
    required = set(protocol['screening']['required_record_fields'])
    by_id = {p['publication_id']: p for p in publications} if publications is not None else None
    by_batch = {b['id']: b for b in batches} if batches is not None else None
    for row in rows:
        if required-set(row) or row['stage'] != 'title_abstract':
            raise ValueError('incomplete screening evidence or unsupported pilot stage')
        if (row['decision'] not in protocol['screening']['title_abstract_decisions']
                or row['access_level'] != 'bibliographic_metadata_title_only'
                or row['independent_review_status'] != 'pending' or row['formulation_ids']):
            raise ValueError('title metadata cannot establish independent review or formulation inclusion')
        if by_id is not None and row['publication_id'] not in by_id:
            raise ValueError('screened publication absent from audited discovery')
        if not all(row[key] for key in ('reason', 'evidence_locator', 'reviewer', 'review_date', 'unresolved')):
            raise ValueError('screening record lacks reason, source, reviewer or open questions')
        for locator in row['evidence_locator']:
            if by_id is not None and (locator['batch_id'], locator['item_index']) not in {
                    (o['batch_id'], o['item_index']) for o in by_id[row['publication_id']]['occurrences']}:
                raise ValueError('screening evidence locator points to another publication')
            if by_batch is not None:
                source = by_batch[locator['batch_id']]
                if locator['raw_path'] != source['raw_path'] or locator['raw_sha256'] != source['raw_sha256']:
                    raise ValueError('screening source identity differs from pinned discovery')
    return rows


def validate_citation_followup(record):
    """Retain a partial cited-source review without admitting a formulation."""
    if record.get('formulation_ids'):
        raise ValueError('citation follow-up cannot admit a formulation')
    if record.get('status') == 'citation_only_not_full_text_reviewed':
        if record.get('source') or record.get('evidence_locator'):
            raise ValueError('primary-source evidence needs explicit partial-review status')
        return
    if (record.get('status') != 'partial_primary_source_review_not_formulation_admission'
            or record.get('independent_review_status') != 'pending'
            or record.get('benchmark_admission') != 'not_admitted'):
        raise ValueError('partial citation review cannot certify review or admission')
    bibliography = record['resolved_bibliography']
    doi = bibliography['doi']
    if (normalize_doi(doi) != doi or record['resolved_publication_id'] != 'doi:'+doi
            or not all(bibliography.get(k) for k in ('title', 'authors', 'year', 'primary_locator'))):
        raise ValueError('citation follow-up needs consistent source-located publication identity')
    if not all(record.get(k) for k in ('review_scope', 'reviewer', 'review_date', 'unresolved', 'evidence_locator')):
        raise ValueError('partial citation review lacks scope or evidence')
    source = record['source']
    if (not all(source.get(k) for k in ('id', 'url', 'discovery_url', 'discovery_locator',
                                       'local_copy', 'access_date', 'reuse'))
            or not re.fullmatch(r'[0-9a-f]{64}', source.get('sha256', ''))):
        raise ValueError('partial citation review needs a pinned primary source')
    total = source['pdf_page_count']
    if type(total) is not int or total < 1:
        raise ValueError('invalid citation-source page count')
    pages = set(range(1, total+1))
    if not set(source['visually_checked_pdf_pages']) <= pages:
        raise ValueError('citation-source visual check outside source')
    for locator in record['evidence_locator']:
        if (locator['source_id'] != source['id'] or not locator.get('locator')
                or not locator.get('observation') or not locator.get('pdf_pages')
                or not set(locator['pdf_pages']) <= pages):
            raise ValueError('citation-source evidence points outside source')
    path = ROOT/source['local_copy']
    if path.exists() and digest(path) != source['sha256']:
        raise ValueError('citation source differs from reviewed snapshot')
    if 'archive_path' in source:
        if (not re.fullmatch(r'[0-9a-f]{64}', source.get('archive_sha256', ''))
                or not source.get('archive_member')):
            raise ValueError('citation source requires pinned archive and member')
        archive = ROOT/source['archive_path']
        if archive.exists():
            if digest(archive) != source['archive_sha256']:
                raise ValueError('citation-source archive differs from reviewed snapshot')
            with zipfile.ZipFile(archive) as bundle:
                if (source['archive_member'] not in bundle.namelist()
                        or hashlib.sha256(bundle.read(source['archive_member'])).hexdigest() != source['sha256']):
                    raise ValueError('citation-source archive member differs from reviewed PDF')


def validate_full_text_screening(ledger, protocol):
    """Check assisted source decisions, not scientific correctness or admission.

    This development ledger uses pinned primary PDFs. A missing local copy is an
    access gap; changed bytes require a new source review. Bibliographic identity
    may be citation-based and never requires an invented atlas model or DOI.
    """
    if (ledger.get('status') != 'assisted_full_text_screening_development_not_final_survey'
            or ledger.get('protocol_id') != protocol['id']):
        raise ValueError('unsupported full-text screening development status')
    rows = ledger['records']
    if len({r['publication_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate publication in full-text screening')
    required = set(protocol['screening']['required_record_fields'])
    for row in rows:
        if required-set(row) or row['stage'] != 'full_text':
            raise ValueError('incomplete full-text screening evidence')
        if (row['decision'] not in protocol['screening']['full_text_decisions']
                or row['independent_review_status'] != 'pending'
                or row.get('benchmark_admission') != 'not_admitted'):
            raise ValueError('assisted full-text screening cannot certify review or benchmark admission')
        if not all(row[key] for key in ('reason', 'evidence_locator', 'reviewer', 'review_date', 'unresolved')):
            raise ValueError('full-text decision lacks evidence or review context')
        included = row['decision'] == 'include_exact_formulation'
        if included != bool(row['formulation_ids']):
            raise ValueError('only an exact-formulation decision can propose formulation IDs')
        criterion = row['decision'] == 'criterion_without_complete_constitutive_law'
        if criterion != bool(row.get('criterion_ids')):
            raise ValueError('criterion decision requires separate criterion identity')
        bibliography, discovery = row['bibliography'], row['discovery']
        if not all(bibliography.get(k) for k in ('title', 'authors', 'year', 'locator')):
            raise ValueError('full-text publication needs a source-located citation')
        doi = bibliography.get('doi')
        if doi is not None:
            if normalize_doi(doi) != doi or row['publication_id'] != 'doi:'+doi:
                raise ValueError('publication identity differs from normalized DOI')
        elif (not row['publication_id'].startswith('citation:')
              or row.get('identity_basis') != 'source_cover_citation_no_verified_doi'):
            raise ValueError('unverified DOI requires explicit provisional citation identity')
        if not all(discovery.get(k) for k in ('route', 'url', 'locator', 'access_date')):
            raise ValueError('full-text source lacks discovery route')
        source = row['source']
        if row['access_level'] != 'full_text_primary_pdf':
            raise ValueError('metadata cannot support this full-text PDF screening ledger')
        if (not all(source.get(k) for k in ('id', 'url', 'local_copy', 'access_date', 'reuse'))
                or not re.fullmatch(r'[0-9a-f]{64}', source.get('sha256', ''))):
            raise ValueError('full-text primary source requires a pinned snapshot')
        total = source['pdf_page_count']
        if type(total) is not int or total < 1:
            raise ValueError('invalid source page count')
        pages = set(range(1, total+1))
        if (source['text_screened_pdf_pages'] != sorted(pages)
                or not set(source['visually_checked_pdf_pages']) <= pages):
            raise ValueError('full-text decision requires complete declared text screening')
        for locator in row['evidence_locator']:
            if (locator['source_id'] != source['id'] or not locator.get('locator')
                    or not locator.get('observation') or not locator.get('pdf_pages')
                    or not set(locator['pdf_pages']) <= pages):
                raise ValueError('full-text evidence points outside its source')
        path = ROOT/source['local_copy']
        if path.exists() and digest(path) != source['sha256']:
            raise ValueError('full-text source differs from reviewed snapshot')
        for followup in row.get('citation_tracing_followups', []):
            validate_citation_followup(followup)
    return rows
