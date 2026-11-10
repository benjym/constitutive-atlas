"""Reuse passing Pages numerical replays for an identical input set.

build_web.py runs the four integrity checks (including the Wasm descriptors)
before this script. The cache never supplies website files or skips those checks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    'perzyna': ('perzyna', 'perzyna.html'),
    'bingham': ('bingham', 'bingham.html'),
    'sls_laboratory': ('sls', 'sls.html'),
    'kelvin_voigt': ('kelvin-voigt', 'kelvin-voigt.html'),
}
# The checkers read these files outside of the package. Kelvin–Voigt's
# analytical reference is inline. The packaged contracts and Wasm glue have no
# local imports; add any new runtime dependency to the package manifest.
REFERENCES = (
    'docs/ingestion/perzyna-comsol63/interface-v2/POLICY.json',
    'docs/ingestion/perzyna-comsol63/execution-v2/cases.json',
    'docs/ingestion/bingham-comsol63/interface-v3/POLICY.json',
    'docs/ingestion/bingham-comsol63/execution-v1/cases.json',
    'docs/ingestion/sls-comsol63/execution-v1/cases.json',
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def fingerprint(root, package, revision, runtime):
    sources = [
        '.github/workflows/pages.yml', 'tools/build_web.py',
        'tools/pages_numerical_replays.py', *REFERENCES,
        *(f'tools/{prefix}_{stem}_package.mjs'
          for stem in SUITES for prefix in ('check', 'test')),
    ]
    inputs = {name: sha((root / name).read_bytes()) for name in sources}
    for engine, retired_page in SUITES.values():
        directory = f'engine-{engine}'
        identity_name = f'{directory}/identity.json'
        manifest_name = f'{directory}/package-manifest.json'
        identity_bytes = (package / identity_name).read_bytes()
        identity = json.loads(identity_bytes)
        # The provenance stamp changes on UI-only releases. It does not enter a
        # solver request. Validate it for this release before normalizing it.
        if identity.pop('release_revision', None) != revision:
            raise ValueError(f'{identity_name}: wrong release revision')
        manifest = read_json(package / manifest_name)
        if manifest['files'].get(identity_name) != sha(identity_bytes):
            raise ValueError(f'{manifest_name}: identity hash mismatch')
        # Bind actual bytes, not claims from the manifest. The original checker
        # also verifies every manifest hash against the current package.
        manifest['files'][identity_name] = sha(canonical(identity))
        inputs[f'package/{manifest_name}'] = sha(canonical(manifest))
        for name in manifest['files']:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'{manifest_name}: unsafe input path {name}')
            inputs[f'package/{name}'] = (
                manifest['files'][identity_name] if name == identity_name
                else sha((package / name).read_bytes())
            )
        # Presence of this retired page is an integrity failure even on a hit.
        if (package / retired_page).exists():
            raise ValueError(f'Unexpected retired package page: {retired_page}')
    return sha(canonical({'runtime': runtime, 'inputs': inputs}))


def replay(package, receipt, digest, revision):
    try:
        previous = read_json(receipt)
    except (FileNotFoundError, ValueError):
        previous = None
    if (isinstance(previous, dict) and previous.get('fingerprint') == digest
            and previous.get('passed') == list(SUITES)
            and re.fullmatch(r'[0-9a-f]{40}', str(previous.get('revision', '')))):
        print(f"Reusing all four numerical replays from {previous['revision']} ({digest}).")
        return

    receipt.unlink(missing_ok=True)
    print(f'No matching pass for {digest}; running all four numerical replays.', flush=True)
    for stem in SUITES:
        start = time.monotonic()
        print(f'Running {stem} numerical replay.', flush=True)
        subprocess.run(['node', str(ROOT / 'tools' / f'check_{stem}_package.mjs'),
                        str(package)], check=True)
        print(f'{stem} passed in {time.monotonic() - start:.1f}s.', flush=True)

    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_bytes(canonical({
        'fingerprint': digest, 'passed': list(SUITES), 'revision': revision,
    }) + b'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('key', 'replay'))
    parser.add_argument('package', type=Path)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--expected')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.revision):
        parser.error('expected an exact Git revision')
    runtime = subprocess.check_output([
        'node', '-p', 'JSON.stringify([process.platform, process.arch, process.versions])',
    ], text=True).strip()
    digest = fingerprint(ROOT, args.package, args.revision, [runtime, os.environ.get('NODE_OPTIONS')])
    if args.command == 'key':
        print(digest)
    else:
        if not args.receipt or args.expected != digest:
            parser.error('missing receipt path or replay inputs changed after computing the cache key')
        replay(args.package, args.receipt, digest, args.revision)


if __name__ == '__main__':
    main()
