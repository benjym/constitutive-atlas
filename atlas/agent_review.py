"""Independent agent review is the project model-approval gate.

Legacy human-signature records are historical evidence, not a prerequisite.
Integrity validation cannot prove a reviewer did the scientific work: the
identified separate agent must actually inspect sources and evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
from .dsl import ValidationError
from .evidence import checked_receipt
from .model import ROOT
from .structure import check

CHECKLIST = frozenset((
    'source_provenance', 'equation_fidelity', 'conventions_dimensions',
    'initialization_domain', 'integration_transactions',
    'independent_numerical_evidence', 'backend_delivery',
    'applicability_claims', 'reproducibility_rights',
))


def _file(root, name):
    relative = Path(name)
    path = (root / relative).resolve()
    if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root) or not path.is_file():
        raise ValidationError('Review artifact must be an existing file within repository: ' + name)
    return path


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_review(path, root=ROOT, for_approval=False):
    root = Path(root).resolve()
    record = json.loads(Path(path).read_text())
    check(record, json.loads((ROOT / 'schemas/agent-review.schema.json').read_text()))
    reviewer = record['reviewer']
    if reviewer['run_id'] in record['author_run_ids']:
        raise ValidationError('Review must be performed by a separate agent run from the model authors')
    entries = record['checklist']
    if {row['id'] for row in entries} != CHECKLIST or len({row['id'] for row in entries}) != len(entries):
        raise ValidationError('Every checklist item must appear exactly once')
    artifacts = {}
    # A changing policy/dossier may have an explicitly archived original. Only
    # a document pinned by that sidecar can use it; unrelated/new reviews still
    # require their exact live artifacts. The model below always stays current.
    document = Path(path).resolve()
    archived_context = None
    if document.is_relative_to(root):
        sidecar = document.parent / 'source-archive-map.json'
        if sidecar.exists():
            try:
                mapping = json.loads(sidecar.read_text())
                relative = document.relative_to(root).as_posix()
                if relative in mapping.get('documents', {}):
                    archived_context = relative
            except (OSError, ValueError, TypeError, AttributeError) as exc:
                raise ValidationError('Invalid review artifact archive map') from exc
    for item in record['artifacts']:
        name = item['path']
        if name in artifacts:
            raise ValidationError('Duplicate review artifact: ' + name)
        if archived_context is not None:
            try:
                artifacts[name] = checked_receipt(root, archived_context, name, item['sha256'])
            except (OSError, ValueError, TypeError, KeyError) as exc:
                raise ValidationError('Review artifact missing or changed: ' + name) from exc
        else:
            artifacts[name] = _file(root, name)
        if _hash(artifacts[name]) != item['sha256']:
            raise ValidationError('Review artifact missing or changed: ' + name)
    for row in entries:
        for reference in row['evidence']:
            if reference.split('#', 1)[0] not in artifacts:
                raise ValidationError('Checklist evidence must name a hashed artifact: ' + reference)
    model = record['model']
    model_path = _file(root, model['path'])
    if not model_path.is_relative_to(root / 'models') or _hash(model_path) != model['sha256']:
        raise ValidationError('Review does not match exact current model bytes')
    if json.loads(model_path.read_text()).get('id') != model['id']:
        raise ValidationError('Review model ID does not match definition')
    if record['status'] == 'accepted':
        if any(row['outcome'] == 'not-applicable' and row['id'] != 'backend_delivery' for row in entries):
            raise ValidationError('Core source and numerical checks cannot be marked not-applicable')
        if record['blocking_findings'] or any(row['outcome'] not in ('pass', 'not-applicable') for row in entries):
            raise ValidationError('Approval requires completed checklist and no unresolved blocking findings')
    if for_approval and record['status'] != 'accepted':
        raise ValidationError('Only an accepted independent agent review permits approval')
    return record


def approval_entry(path, root=ROOT):
    """Return a registry entry for the exact reviewed scope; never mutate models."""
    root = Path(root).resolve()
    path = Path(path).resolve()
    if not path.is_relative_to(root):
        raise ValidationError('Approval review must be stored within the repository')
    record = validate_review(path, root, for_approval=True)
    return {
        'id': record['id'] + '-approval', 'model_id': record['model']['id'],
        'status': 'approved', 'approved_on': record['created_at'],
        'approval_authority': {'kind': 'independent-agent-review', 'policy': 'agent-checklist-v1',
                               'identity': record['reviewer']},
        'definition': {'path': record['model']['path'], 'sha256': record['model']['sha256']},
        'scope': {'use': record['scope']},
        'review': {'kind': 'agent-model-review', 'path': path.relative_to(root).as_posix(), 'sha256': _hash(path)},
        'limitations': record['limitations'], 'supporting_files': record['artifacts'],
        'experimental_validation': 'not_assessed', 'deployment_authorized': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('--for-approval', action='store_true')
    parser.add_argument('--approval-output', type=Path, help='Write a new registry entry; existing files are never overwritten')
    args = parser.parse_args()
    record = validate_review(args.record, for_approval=args.for_approval or bool(args.approval_output))
    if args.approval_output:
        entry = approval_entry(args.record)
        with args.approval_output.open('x') as output:
            output.write(json.dumps(entry, indent=2) + '\n')
    print(record['id'] + ': ' + record['status'] + '; independent agent checklist verified')


if __name__ == '__main__':main()
