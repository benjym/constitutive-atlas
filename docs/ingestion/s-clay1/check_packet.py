"""Portable metadata/integrity checks only; no constitutive or network execution."""
import hashlib
import json
from pathlib import Path
import re


def check(root=None):
    root = Path(root) if root else Path(__file__).resolve().parent
    manifest = json.loads((root / 'manifest.json').read_text())
    expected = {'README.md', 'source-receipts.json', 'crosswalk.json',
                'check_packet.py', 'check-results.json'}
    assert set(manifest['files']) == expected
    for relative, digest in manifest['files'].items():
        assert Path(relative).name == relative
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    receipts = json.loads((root / 'source-receipts.json').read_text())
    good, wrong = receipts['selected_publication'], receipts['rejected_catalogue_link']
    assert good['doi'] == '10.1139/t02-119'
    assert good['title'] == 'An anisotropic elastoplastic model for soft clays'
    assert good['authors'] == ['Simon J Wheeler', 'Anu Näätänen', 'Minna Karstunen', 'Matti Lojander']
    assert (good['volume'], good['issue'], good['pages']) == ('40', '2', '403-418')
    assert wrong['doi'] == '10.1680/geot.2003.53.1.41'
    assert wrong['authors'] == ['S. J. Wheeler', 'R. S. Sharma', 'M. S. R. Buisson']
    assert 'hydraulic hysteresis' in wrong['title']
    crosswalk = json.loads((root / 'crosswalk.json').read_text())
    assert receipts['original_pdf'] is None and receipts['original_pdf_sha256'] is None
    assert receipts['original_equation_visual_review'] is False
    assert crosswalk['source_complete'] is False
    assert crosswalk['executable'] is False and crosswalk['scientifically_admitted'] is False
    assert crosswalk['equations'] == [] and len(crosswalk['items']) == 10
    assert all(row['original_locator'] is None and row['typed_expression'] is None
               for row in crosswalk['items'])
    files = receipts['local_screening']['files']
    assert len(files) == 20 and len({row['name'] for row in files}) == 20
    assert all(row['first_page_target_match'] is False and row['bytes'] > 0
               and re.fullmatch('[0-9a-f]{64}', row['sha256']) for row in files)
    return {'kind': 'metadata-integrity-only', 'groups_passed': 4,
            'constitutive_checks_run': 0, 'original_equations_verified': False}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2) )
