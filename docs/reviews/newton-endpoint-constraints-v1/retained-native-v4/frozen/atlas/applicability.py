"""Identity checks for an explicitly incomplete scientific applicability matrix."""
from collections import Counter
import hashlib
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit
from .model import ROOT
from .source_replay import strict_json
from .study_allocation import require, validate_allocation


def validate_matrix(matrix, *, root=ROOT):
    """Check metadata and exact current-definition coverage, never infer eligibility."""
    root = Path(root).resolve()
    def read_pin(record):
        require(isinstance(record, dict) and set(record) == {'path', 'sha256'}, 'exact file binding required')
        name, digest = record['path'], record['sha256']
        require(isinstance(name, str) and name and '\\' not in name, 'relative source path required')
        require(name.startswith(('docs/', 'studies/')), 'only public source/study metadata pins are supported')
        path = PurePosixPath(name)
        require(not path.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')),
                'unsafe source path')
        require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest) is not None,
                'invalid source digest')
        target = (root / name).resolve()
        require(target.is_relative_to(root), 'source path escapes repository')
        content = target.read_bytes()
        require(hashlib.sha256(content).hexdigest() == digest, 'source identity mismatch: ' + name)
        return content

    require(isinstance(matrix, dict) and set(matrix) == {'schema_version', 'kind', 'id',
            'prepared_on', 'independent_review', 'reviewer', 'dataset', 'rows', 'limitations'},
            'unsupported matrix fields')
    require(matrix['schema_version'] == '0.1' and matrix['kind'] == 'model-experiment-applicability-matrix',
            'unsupported matrix kind/version')
    require(isinstance(matrix['id'], str) and re.fullmatch('[a-z][a-z0-9-]*', matrix['id']) is not None,
            'invalid matrix ID')
    require(isinstance(matrix['prepared_on'], str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', matrix['prepared_on']) is not None,
            'explicit matrix date required')
    require(matrix['independent_review'] == 'pending' and matrix['reviewer'] is None,
            'v0.1 cannot certify a scientific decision or assign a reviewer')
    def text_list(value):
        require(isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value),
                'explicit nonempty prerequisites/limitations required')
    text_list(matrix['limitations'])
    dataset = matrix['dataset']
    require(isinstance(dataset, dict) and set(dataset) == {'id', 'material', 'source_url', 'allocation', 'reservations'},
            'exact dataset identity required')
    require(all(isinstance(dataset[k], str) and dataset[k].strip() for k in ('id', 'material', 'source_url')),
            'dataset identity/material/source required')
    url = urlsplit(dataset['source_url'])
    require(url.scheme == 'https' and bool(url.netloc), 'HTTPS dataset source required')
    allocation = strict_json(read_pin(dataset['allocation']))
    reservations = strict_json(read_pin(dataset['reservations']))
    allocation_report = validate_allocation(allocation, reservations, policy_sha256=dataset['reservations']['sha256'])
    current = {}
    for path in sorted((root/'models').glob('*.json')):
        content = path.read_bytes(); model = strict_json(content)
        require(model['id'] not in current, 'duplicate current model ID')
        current[model['id']] = {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(content).hexdigest()}
    require(bool(current), 'current model inventory is empty')
    require(isinstance(matrix['rows'], list) and bool(matrix['rows']), 'matrix rows required')
    seen = set(); counts = Counter()
    for row in matrix['rows']:
        require(isinstance(row, dict) and set(row) == {'model', 'assessment', 'scientific_eligibility',
                'evidence', 'prerequisites', 'limitations'}, 'unsupported matrix row')
        binding = row['model']
        require(isinstance(binding, dict) and set(binding) == {'id', 'path', 'sha256'}, 'exact model binding required')
        mid = binding['id']
        require(isinstance(mid, str) and mid in current and mid not in seen, 'unknown or duplicate model row')
        require({k: binding[k] for k in ('path', 'sha256')} == current[mid], 'current model identity mismatch: ' + mid)
        seen.add(mid)
        status = row['assessment']
        require(status in ('not_assessed', 'conditional_development_evidence'), 'unsupported assessment claim')
        require(row['scientific_eligibility'] == 'undetermined', 'v0.1 eligibility must remain undetermined')
        text_list(row['prerequisites']); text_list(row['limitations'])
        require(isinstance(row['evidence'], list) and bool(row['evidence']), 'source/evidence bindings required')
        for evidence in row['evidence']: read_pin(evidence)
        counts[status] += 1
    require(seen == set(current), 'matrix must cover every current executable definition exactly once')
    tests = set(allocation_report['calibration_union_ids']) | set(allocation_report['evaluation_ids'])
    return {'kind': 'applicability-matrix-identity-check', 'id': matrix['id'], 'passed': True,
            'model_count': len(seen), 'assessment_counts': dict(counts), 'dataset_id': dataset['id'],
            'whole_test_count': len(tests), 'scientific_eligibility': 'undetermined',
            'independent_review': 'pending', 'response_files_read': 0,
            'scope': 'Metadata identity/coverage only; no physical suitability or scientific admission certified.'}


def load_matrix(path, *, root=ROOT):
    content = Path(path).read_bytes()
    report = validate_matrix(strict_json(content), root=root)
    report['matrix_sha256'] = hashlib.sha256(content).hexdigest()
    return report
