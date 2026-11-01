"""Saved-input integrity and applicability checks; no material execution/signoff."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def preflight():
    pins = json.loads((HERE / 'pins.json').read_text())
    for name, expected in pins['files'].items():
        path = ROOT / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'pinned input changed: {name}')
    current_path = 'models/barodesy-clay-2017.json'
    current_hash = pins['files'][current_path]
    current = json.loads((ROOT / current_path).read_text())
    research = json.loads((ROOT / 'models/research/barodesy2017/body-zero-spin.json').read_text())
    review = json.loads((ROOT / 'catalogue/reviews/barodesy-clay-2017-source-v1.json').read_text())
    if not (review['model']['definition_sha256'] == current_hash and review['status'] == 'pending' and not review['independent']):
        raise ValueError('pending review/current identity changed; new applicability review required')
    if current['status'] != 'draft' or current['schema_version'] != '0.3':
        raise ValueError('candidate admission/schema changed')
    math_fields = ['parameters', 'derived', 'domain', 'equations']
    for key in math_fields:
        if current[key] != research[key]:
            raise ValueError(f'research/current mathematical difference: {key}')
    state_fields = ['name', 'shape', 'unit', 'scale', 'initial']
    if [[s[k] for k in state_fields] for s in current['state']] != [[s[k] for k in state_fields] for s in research['state']]:
        raise ValueError('research/current state layout or examples differ')
    for version in ['v1', 'v2']:
        base = ROOT / f'catalogue/investigations/barodesy2017-preview-{version}'
        manifest = json.loads((base / 'manifest.json').read_text())
        if manifest[current_path] != current_hash:
            raise ValueError(f'preview-{version} binds a different candidate')
        if hashlib.sha256((base / current_path).read_bytes()).hexdigest() != current_hash:
            raise ValueError(f'preview-{version} frozen model missing or corrupt')
        assessment = json.loads((base / 'assessment.json').read_text())
        if not assessment['pass'] or assessment['scientific_admission'] or assessment['deployment']:
            raise ValueError(f'preview-{version} recorded outcome/scope changed')
    sheet = json.loads((HERE / 'review-sheet.json').read_text())
    if sheet['reviewer'] is not None or sheet['signed_at'] is not None or any(x['decision'] != 'pending' for x in sheet['decisions']):
        raise ValueError('review sheet changed; this unsigned preflight no longer applies')
    return {
        'version': 'barodesy-production-closure-preflight-v1',
        'pass': True,
        'pinned_files_verified': len(pins['files']),
        'current_definition_sha256': current_hash,
        'current_preview_versions_bound': ['v1', 'v2'],
        'equal_research_mathematical_fields': math_fields,
        'equal_research_state_fields': state_fields,
        'review_status': 'pending',
        'scientific_admission': False,
        'compiled_execution': False,
        'historical_reports_regenerated': False,
        'new_source_inspection': False,
    }


if __name__ == '__main__':
    print(json.dumps(preflight(), indent=2) + '\n', end='')
