"""Integrity-only catalogue projection of actual agent reviews and registry entries.

Historical reviews validate in an isolated exact-byte context. This never
relaxes the current-model requirement of the approval API or runs a model.
"""
import hashlib
import json
from pathlib import Path
import tempfile
from .agent_review import approval_entry, validate_review
from .evidence import checked_receipt
from .model import ROOT
from .structure import check


def _file(root, name):
    p = Path(name)
    resolved = (root / p).resolve()
    if p.is_absolute() or '..' in p.parts or not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('Missing or unsafe agent-review export file: ' + name)
    return resolved


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def collect(root, catalogue_ids):
    """Return projections, public original JSON bytes, and explicit omissions.

    Only record/definition/registry JSON is public. Raw evidence artifacts and
    private sources are checked locally and never included in this export.
    """
    root = Path(root).resolve()
    registry_path = 'catalogue/approved-models.json'
    registry_raw = _file(root, registry_path).read_bytes() if (root / registry_path).exists() else None
    registry = json.loads(registry_raw) if registry_raw is not None else {'models': []}
    if not isinstance(registry.get('models'), list):
        raise ValueError('Malformed approval registry')
    rows, originals, omitted = [], {}, []
    for path in sorted((root / 'catalogue/agent-reviews').glob('*.json')):
        if path.name == 'source-archive-map.json':
            continue
        relative = path.relative_to(root).as_posix()
        raw = _file(root, relative).read_bytes()
        record = json.loads(raw)
        check(record, json.loads((ROOT / 'schemas/agent-review.schema.json').read_text()))
        mid = record['model']['id']
        if mid not in catalogue_ids:
            omitted.append(relative)
            continue  # Never invent a family/variant binding.
        mapping_path = path.parent / 'source-archive-map.json'
        mapping = json.loads(_file(root, mapping_path.relative_to(root).as_posix()).read_text()) if mapping_path.exists() else {}
        archived = relative in mapping.get('documents', {})

        def retained(name, expected):
            if archived:
                target = checked_receipt(root, relative, name, expected)
            else:
                target = _file(root, name)
            data = target.read_bytes()
            if _sha(data) != expected:
                raise ValueError('Agent-review export receipt changed: ' + name)
            return data

        model = record['model']
        definition = retained(model['path'], model['sha256'])
        current_path = (root / model['path']).resolve()
        if not current_path.is_relative_to(root):
            raise ValueError('Agent-review model escapes repository')
        current_hash = _sha(current_path.read_bytes()) if current_path.is_file() else None
        # Reuse every semantic review/approval check against the explicitly
        # retained original, without allowing historical bytes to approve the
        # current definition. Nothing in this context is executed.
        with tempfile.TemporaryDirectory(prefix='atlas-review-export-') as temporary:
            context = Path(temporary)
            files = {item['path']: retained(item['path'], item['sha256']) for item in record['artifacts']}
            files[model['path']] = definition
            files[relative] = raw
            for name, data in files.items():
                relative_path = Path(name)
                if relative_path.is_absolute() or '..' in relative_path.parts:
                    raise ValueError('Unsafe agent-review context path')
                target = context / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            validate_review(context / relative, root=context)
            expected_approval = approval_entry(context / relative, root=context) if record['status'] == 'accepted' else None
        registered = [entry for entry in registry['models'] if entry.get('review', {}).get('path') == relative]
        if len(registered) > 1:
            raise ValueError('Ambiguous approval entries for agent review: ' + relative)
        if registered and (expected_approval is None or any(registered[0].get(k) != v for k, v in expected_approval.items())):
            raise ValueError('Approval does not match exact accepted agent review: ' + relative)
        definition_record = 'catalogue/agent-reviews/definitions/' + path.name
        rows.append({
            'catalogue_id': mid, 'id': record['id'], 'record_path': relative,
            'record_sha256': _sha(raw), 'definition_path': model['path'],
            'definition_sha256': model['sha256'], 'definition_record_path': definition_record, 'current_definition_sha256': current_hash,
            'definition_current': current_hash == model['sha256'], 'status': record['status'],
            'reviewer': record['reviewer'], 'created_at': record['created_at'],
            'scope': record['scope'], 'limitations': record['limitations'],
            'blocking_findings': record['blocking_findings'], 'checklist': record['checklist'],
            'registered_approval_id': registered[0]['id'] if registered else None,
        })
        originals[relative] = raw
        # The retained reviewed definition has a distinct per-review URL;
        # never overwrite a current builder-owned definition with old bytes.
        originals[definition_record] = definition
        if registered:
            originals[registry_path] = registry_raw
    return rows, originals, omitted
