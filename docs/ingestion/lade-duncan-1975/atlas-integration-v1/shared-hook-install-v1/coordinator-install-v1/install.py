"""Coordinator-only guarded installation. Default is preflight; --apply mutates.

No build, generation, artifact execution or scientific decision is performed.
Failures retain the incremental logs, staged files and any completed operations;
there is no automatic rollback or whole-install atomicity claim.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
A = 'docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
V3 = A + 'shared-hook-install-v1/revision-v3/'
F = 'docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/'
PINS = {
    'SOURCE_FREEZE.json': '7349ea545f53bc8cf0183c5ba58366da5abe0fc4d0b132857e91d9b4b394836f',
    'PLAN.json': '518b24f180c1f24a7d70f27b31df889307a2cf298e302c9a196d1e8d336f35a9',
    'APPLY_WHITELIST.json': 'c0ab26f7dbbf3fa09daac6b9880474a44a931d23dc495e07228e9a62ef6f3ebd',
    'CHECK_RESULTS.json': '4c290725b3c6c7821323bf54b9eaa974f1e05e7c87f434e9e4d2ac71cefd6166',
}
REVIEWS = {
    'wiring': (A + 'hooks-proposed-v1/rebased-v5/independent-review/review-receipt.json',
               '6a96ee7b4bcf4cd0cce3892b5d123b30f6033fbd84fd2515117b5f17bbd53104', '/root/lade_interface_review'),
    'dossier': (F + 'dossier-status-review/review-receipt-v2.json',
                '1da85c5986ea124b14dcb7f3c15e67acd67908fac2c29dbadca3e3ee0c751796', '/root/lade_source_review'),
    'status': (F + 'project-status-review/review-receipt.json',
               'b1c92ed922a2cc51fa81b117e5fd41772391d5aa689c43fa36f868527d102bad', '/root/lade_source_review'),
}
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt


def digest(data):
    return hashlib.sha256(data).hexdigest()


def target(name, mutation=False):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or p.as_posix() != name or name == '.':
        raise ValueError('Unsafe repository path: ' + str(name))
    result = ROOT / p
    if not result.resolve().is_relative_to(ROOT):
        raise ValueError('Path escapes repository: ' + name)
    if mutation:
        for component in [result, *result.parents]:
            if component == ROOT:
                break
            if component.is_symlink():
                raise ValueError('Refusing symlink mutation path: ' + str(component))
            if component != result and component.exists() and not component.is_dir():
                raise ValueError('Non-directory parent: ' + str(component))
    return result


def pinned(name, expected):
    data = target(name).read_bytes()
    if digest(data) != expected:
        raise ValueError('Changed input: ' + name)
    return data


def prior(name, expected):
    p = target(name, mutation=True)
    if expected is None:
        if p.exists() or p.is_symlink():
            raise ValueError('Creation destination already exists: ' + name)
    elif not p.is_file() or digest(p.read_bytes()) != expected:
        raise ValueError('Prior destination differs: ' + name)


def accepted(name, expected, reviewer, required):
    record = json.loads(pinned(name, expected))
    if record.get('status') != 'accepted' or record.get('reviewer_run') != reviewer:
        raise ValueError('Missing exact separate accepted review: ' + name)
    if record.get('blocking_findings') or record.get('findings'):
        raise ValueError('Review still has findings: ' + name)
    files = record.get('files', {})
    if any(files.get(path) != pin for path, pin in required.items()):
        raise ValueError('Review does not bind exact proposed bytes: ' + name)
    return record


def preflight(review_name, review_sha):
    docs = {name: json.loads(pinned(V3 + name, pin)) for name, pin in PINS.items()}
    freeze, plan = docs['SOURCE_FREEZE.json'], docs['PLAN.json']
    whitelist, results = docs['APPLY_WHITELIST.json'], docs['CHECK_RESULTS.json']
    if len(freeze['files']) != 799:
        raise ValueError('Unexpected frozen file count')
    for row in freeze['files']:
        pinned(row['original_path'], row['old_sha256'])
    live = json.loads(target(V3 + 'SOURCE_PINS.json').read_bytes())['files']
    if len(live) != 17490:
        raise ValueError('Unexpected live pin count')
    for row in live:
        pinned(row['original_path'], row['old_sha256'])
    accepted(review_name, review_sha, '/root/lade_source_review',
             {V3 + name: pin for name, pin in PINS.items() if name != 'CHECK_RESULTS.json'})
    reviews = {key: accepted(*value, {}) for key, value in REVIEWS.items()}
    if not plan['passed'] or plan['issues'] or plan['failed']:
        raise ValueError('Frozen preservation plan not passed')
    if len(whitelist['writes']) != 92 or len(plan['replacements']) != 11:
        raise ValueError('Unexpected operation count')
    maps = {r['original_path']: r for r in plan['maps']}
    archives = {r['canonical_archive']: r for r in plan['archives']}
    operations = []
    for row in whitelist['writes']:
        name, kind = row['original_path'], row['operation']
        if kind == 'create_canonical_snapshot':
            proof = archives[name]
            if row['old_sha256'] is not None or proof['already_present']:
                raise ValueError('Invalid new snapshot operation')
            candidate = V3 + proof['snapshot']
            expected = proof['old_sha256']
        elif kind in ('create_new_map', 'replace_existing_map'):
            proof = maps[name]
            if row['old_sha256'] != proof['old_sha256']:
                raise ValueError('Map prior mismatch')
            candidate, expected = V3 + proof['candidate'], proof['new_sha256']
        else:
            raise ValueError('Unexpected metadata operation: ' + kind)
        if row['new_sha256'] != expected:
            raise ValueError('Whitelist/candidate hash mismatch')
        data = pinned(candidate, expected)
        prior(name, row['old_sha256'])
        operations.append(dict(row, candidate=candidate, data=data))
    for row in plan['replacements']:
        name, candidate, expected = row['original_path'], row['future_copy'], row['new_sha256']
        if not candidate or not expected:
            raise ValueError('Unspecified source replacement')
        group = 'status' if name in ('docs/STATUS.md', 'ROADMAP.md') else 'dossier' if name.startswith('docs/models/') else 'wiring'
        if reviews[group]['files'].get(candidate) != expected:
            raise ValueError('Source future not covered by accepted review: ' + name)
        data = pinned(candidate, expected)
        prior(name, row['old_sha256'])
        operations.append(dict(original_path=name, old_sha256=row['old_sha256'],
                               new_sha256=expected, operation='replace_source', candidate=candidate, data=data))
    if len({r['original_path'] for r in operations}) != 103:
        raise ValueError('Duplicate operation destination')
    for row in plan['archives']:
        pinned(V3 + row['snapshot'], row['old_sha256'])
        if row['already_present']:
            pinned(row['canonical_archive'], row['old_sha256'])
    passing = [r for r in results['checks'] if r['outcome'] == 'passed']
    diagnostics = results['preexisting_peer_failures']
    if len(passing) != 43760 or len(diagnostics) != 78:
        raise ValueError('Unexpected frozen postcheck scope')
    operations.sort(key=lambda r: 0 if r['operation'] == 'create_canonical_snapshot' else 2 if r['operation'] == 'replace_source' else 1)
    return operations, passing, diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', required=True, help='Repository-relative separate accepted v3 review receipt')
    parser.add_argument('--review-sha256', required=True)
    parser.add_argument('--output', required=True, help='New run directory beneath this coordinator-install-v1 directory')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='Perform guarded metadata then eleven source replacements')
    mode.add_argument('--preflight-only', action='store_true', help='Validate every guard; production writes remain disabled (the default)')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if not output.is_relative_to(HERE) or output == HERE or output.exists():
        raise ValueError('Output must be a new child of the helper directory')
    output.mkdir(parents=True, exist_ok=False)
    state = dict(status='preflighting', apply=args.apply, review=args.review,
                 review_sha256=args.review_sha256, operations=[], completed_bindings=0,
                 qualification_scope='No generation, runtime/E5 postvalidator, artifact execution or browser qualification performed')
    def persist():
        temporary = output / ('state-' + uuid.uuid4().hex + '.tmp')
        with temporary.open('x') as stream:
            json.dump(state, stream, indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(temporary, output / 'STATE.json')
    def event(kind, **values):
        with (output / 'operations.jsonl').open('a') as stream:
            stream.write(json.dumps(dict(event=kind, **values)) + '\n');stream.flush();os.fsync(stream.fileno())
    persist()
    try:
        operations, passing, diagnostics = preflight(args.review, args.review_sha256)
        state.update(status='preflight-passed', planned_operations=len(operations),
                     frozen_files=799, live_pins=17490, preexisting_diagnostics=diagnostics)
        event('all_preflight_guards_passed', operations=len(operations));persist()
        if not args.apply:
            print(json.dumps(dict(status='preflight-passed', production_writes=0, output=str(output))));return
        for row in operations:
            state['current_operation'] = {k: v for k, v in row.items() if k != 'data'}
            persist()
            name, data = row['original_path'], row['data']
            p = target(name, mutation=True)
            # All payloads were frozen before the first production write.
            prior(name, row['old_sha256'])
            missing = []
            parent = p.parent
            while not parent.exists():
                missing.append(parent);parent = parent.parent
            for directory in reversed(missing):
                target(directory.relative_to(ROOT).as_posix(), mutation=True)
                directory.mkdir(exist_ok=False)
                event('created_parent_directory', original_path=directory.relative_to(ROOT).as_posix())
            event('operation_started', **{k: v for k, v in row.items() if k != 'data'})
            if row['old_sha256'] is None:
                prior(name, None)
                fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o644)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(data);stream.flush();os.fsync(stream.fileno())
            else:
                stage = p.with_name('.' + p.name + '.lade-install-' + uuid.uuid4().hex)
                event('replacement_stage', original_path=name, retained_stage=stage.relative_to(ROOT).as_posix())
                with stage.open('xb') as stream:
                    stream.write(data);stream.flush();os.fsync(stream.fileno())
                prior(name, row['old_sha256'])  # immediately before atomic file replacement
                os.replace(stage, p)
            pinned(name, row['new_sha256'])
            state['operations'].append({k: v for k, v in row.items() if k != 'data'})
            state.pop('current_operation', None)
            event('operation_verified', original_path=name, new_sha256=row['new_sha256']);persist()
        state['status'] = 'postchecking';persist()
        with (output / 'binding-checks.jsonl').open('x') as stream:
            for index, row in enumerate(passing):
                state['current_binding'] = {k: row[k] for k in ('document', 'original_path', 'old_sha256')}
                try:
                    checked_receipt(ROOT, row['document'], row['original_path'], row['old_sha256'])
                except BaseException as error:
                    stream.write(json.dumps(dict(state['current_binding'], outcome='failed', error=str(error))) + '\n')
                    stream.flush();os.fsync(stream.fileno());raise
                state.pop('current_binding', None)
                stream.write(json.dumps(row) + '\n')
                state['completed_bindings'] = index + 1
                if (index + 1) % 100 == 0:
                    stream.flush();os.fsync(stream.fileno());persist()
            stream.flush();os.fsync(stream.fileno())
        state['status'] = 'passed';persist()
        with (output / 'INSTALLED.json').open('x') as stream:
            json.dump(state, stream, indent=2);stream.write('\n')
        event('installation_and_binding_postcheck_passed', operations=103, passing_bindings=43760, retained_preexisting_diagnostics=78)
        print(json.dumps(dict(status='passed', output=str(output), operations=103, passing_bindings=43760)))
    except BaseException as error:
        state.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
        event('failed', error=state['error']);persist()
        with (output / 'FAILED.json').open('x') as stream:
            json.dump(state, stream, indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        raise


if __name__ == '__main__':
    main()
