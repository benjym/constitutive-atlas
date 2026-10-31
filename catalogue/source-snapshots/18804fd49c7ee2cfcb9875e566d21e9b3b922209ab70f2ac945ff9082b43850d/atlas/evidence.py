"""Validate numerical evidence separately from model admission and human review."""
import hashlib
import json
from pathlib import Path
from .dsl import ValidationError
from .model import ROOT
from .structure import check


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_record(path, root=ROOT, current=False):
    root = Path(root).resolve()
    record = json.loads(Path(path).read_text())
    schema = {'numerical-evidence':'evidence.schema.json', 'source-review':'review.schema.json'}.get(record.get('kind'))
    if not schema:
        raise ValidationError('Unsupported evidence/review record kind')
    check(record, json.loads((ROOT / 'schemas' / schema).read_text()))
    if record['kind'] == 'source-review':
        if record['status'] != 'pending' and (not record['independent'] or not record.get('reviewer') or not record.get('reviewed_at')):
            raise ValidationError('Completed review requires independent reviewer identity and date')
        if record['status'] == 'pending' and not record['unresolved']:
            raise ValidationError('Pending review must identify unresolved work')
        if record['status'] == 'accepted' and record['unresolved']:
            raise ValidationError('Accepted review cannot have unresolved questions')
        if not (root / record['dossier']).is_file():
            raise ValidationError('Review dossier is missing')
    seen = set()
    for item in record.get('artifacts', []) + (record.get('source_files', []) if current else []):
        target = (root / item['path']).resolve()
        if not target.is_relative_to(root) or target == root or item['path'] in seen:
            raise ValidationError('Artifact paths must be unique files within the repository')
        seen.add(item['path'])
        if not target.is_file() or sha256(target) != item['sha256']:
            raise ValidationError('Evidence artifact missing or changed: ' + item['path'])
    if current:
        model = root / 'models' / (record['model']['id'] + '.json')
        if not model.is_file() or sha256(model) != record['model']['definition_sha256']:
            raise ValidationError('Evidence does not match the current model definition')
    # An envelope establishes integrity and attribution, not scientific validity.
    # The named checker owns report-specific numerical assertions.
    return record
