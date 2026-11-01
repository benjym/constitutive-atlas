"""Integrity checks for provisional source-only formulation reviews.

These checks do not screen publications or independently review constitutive laws.
"""
from pathlib import Path

from analysis.common import ROOT, digest, read_json


def validate_source_reviews(directory=None, root=ROOT):
    root = Path(root)
    directory = Path(directory) if directory is not None else root/'paper/study/source_formulations'
    atlas_ids = {m['id'] for m in read_json(root/'catalogue/manifest.json')['models']}
    records = []
    seen = set()
    for path in sorted(directory.glob('*.json')):
        record = read_json(path)
        model_id = record['model_id']
        if model_id not in atlas_ids or model_id in seen:
            raise ValueError('source review requires a unique known atlas identity')
        seen.add(model_id)
        if record['record_kind'] != 'source_formulation_without_implementation_annotation':
            raise ValueError('source-only review must remain distinct from implementation annotation')
        source = record['source']
        if (not record['publication_id'].startswith('doi:') or
                source['doi_url'] != 'https://doi.org/'+record['publication_id'].removeprefix('doi:')):
            raise ValueError('source review publication DOI mismatch')
        if not source['reviewed_url'] or not source['access_date']:
            raise ValueError('source review lacks access provenance')
        local, checksum = source['local_copy'], source['sha256']
        if (local is None) != (checksum is None):
            raise ValueError('local source path and hash must be supplied together')
        if local is not None:
            relative = Path(local)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('local source must be repository-relative')
            if len(checksum) != 64 or any(c not in '0123456789abcdef' for c in checksum):
                raise ValueError('invalid source SHA256')
            source_path = root/relative
            if source_path.exists() and digest(source_path) != checksum:
                raise ValueError('source bytes differ from reviewed snapshot')
        metadata = source.get('bibliographic_crosscheck')
        if metadata and digest(root/metadata['local_copy']) != metadata['sha256']:
            raise ValueError('bibliographic snapshot differs from reviewed metadata')
        audit = record.get('normalization_audit')
        if audit:
            if not checksum or audit['source_sha256'] != checksum:
                raise ValueError('normalization audit refers to a different source snapshot')
            for audit_path, audit_hash in audit['inputs_sha256'].items():
                if digest(root/audit_path) != audit_hash:
                    raise ValueError('normalization audit input changed; review required')
        if not record['claims'] or any(not c['statement'] or not c['locator'] for c in record['claims']):
            raise ValueError('source claims require evidence locators')
        review = record['review']
        if bool(review['independent_reviewer']) != bool(review['independent_review_date']):
            raise ValueError('independent reviewer and date must be supplied together')
        records.append(record)
    return records
