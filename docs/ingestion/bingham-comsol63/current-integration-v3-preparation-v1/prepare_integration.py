#!/usr/bin/env python3
"""Prepare three candidate files only. Never install, build, or create a review."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODEL = 'bingham-comsol63-mises-perfect-zero-spin-ode'
MODEL_SHA = '6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850'
PROFILE = 'docs/ingestion/bingham-comsol63/current-profile-v2-preparation-v1/profile.json'
TARGETS = ('catalogue/manifest.json', 'catalogue/approved-models.json', 'web/model-profile-data.mjs')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def profiles(data):
    text = data.decode('utf-8')
    marker = 'export const modelProfiles = '
    if text.count(marker) != 1:
        raise ValueError('Unexpected profile module declaration')
    offset = text.index(marker) + len(marker)
    obj, end = json.JSONDecoder().raw_decode(text[offset:])
    if not isinstance(obj, dict) or text[offset + end:].strip() != ';':
        raise ValueError('Unexpected profile module content')
    return obj, text[:offset], text[offset + end:]

def prepare(root, review_path):
    pins = json.loads((HERE / 'INPUTS.json').read_text())['release_inputs']
    # Explicitly stop on concurrent source/integration changes. A new preparation
    # identity is needed if any pinned input has changed; never update this record.
    for name, expected in pins.items():
        if sha((root / name).read_bytes()) != expected:
            raise ValueError('Preparation input changed: ' + name)
    review_path = review_path.resolve()
    registry_dir = (root / 'catalogue/agent-reviews').resolve()
    if review_path.parent != registry_dir or review_path.suffix != '.json':
        raise ValueError('Review must be a direct canonical agent-reviews JSON file')
    sys.path.insert(0, str(root))
    from atlas.agent_review import approval_entry, validate_review
    review = validate_review(review_path, root=root, for_approval=True)
    if review['model']['id'] != MODEL or review['model']['sha256'] != MODEL_SHA:
        raise ValueError('Review does not bind the exact Bingham candidate')
    approval = approval_entry(review_path, root=root)
    definition = json.loads((root / approval['definition']['path']).read_text())
    if definition != json.loads((root / 'docs/ingestion/bingham-comsol63/source-v1/candidate.json').read_text()):
        raise ValueError('Definition does not equal frozen source candidate')
    manifest = json.loads((root / TARGETS[0]).read_text())
    registry = json.loads((root / TARGETS[1]).read_text())
    old_profiles, prefix, suffix = profiles((root / TARGETS[2]).read_bytes())
    if any(x['id'] == MODEL for x in manifest['models']) or MODEL in old_profiles:
        raise ValueError('Bingham already present; this is a single-addition preparation')
    if any(x['model_id'] == MODEL or x['id'] == approval['id'] for x in registry['models']):
        raise ValueError('Bingham approval or approval identity already present')
    entry = {
        'id': MODEL, 'name': definition['name'], 'family': definition['family'],
        'status': 'reviewed', 'executable': False, 'timed_laboratory': 'index.html',
        'dossier': 'docs/models/bingham-comsol63.md',
        'note': 'COMSOL 6.3 isotropic elastic associative von Mises Bingham law: constant positive yield stress, no hardening. Physical-time strain hold, stress hold and all-six constant strain rate; complete thirteen-component strain and viscoplastic memory. Infinitesimal strain, dry total stress, compression-positive Mandel components, fixed spatial frame and zero spin. Illustrative parameters; no experimental validation, finite-rotation or broad parameter qualification. Exact accepted scope and limitations are retained in the independent review.'
    }
    # The approved definition supplies exactly three database source rows. Do not
    # duplicate them in discovery_url/research_sources/catalogue_sources.
    manifest['models'].append(entry)
    registry['models'].append(approval)
    profile = json.loads((root / PROFILE).read_text())
    original_profile_text = (root / TARGETS[2]).read_text()
    closing = len(original_profile_text) - len(suffix) - 1
    # Append the frozen editorial object without reserializing prior entries.
    addition = ',\n  ' + json.dumps(MODEL) + ': ' + json.dumps(profile, ensure_ascii=False, indent=2).replace('\n', '\n  ') + '\n'
    profile_output = original_profile_text[:closing].rstrip() + addition + original_profile_text[closing:]
    if profiles(profile_output.encode())[0] != {**old_profiles, MODEL: profile}:
        raise ValueError('Profile append changed prior content')
    result = {
        TARGETS[0]: (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode(),
        TARGETS[1]: (json.dumps(registry, ensure_ascii=False, indent=2) + '\n').encode(),
        TARGETS[2]: profile_output.encode()
    }
    return result, approval

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New candidate directory; no installation option')
    args = parser.parse_args()
    result, approval = prepare(ROOT, args.review)
    output = args.output.resolve()
    if output.exists() or args.output.is_symlink():
        raise ValueError('Candidate output must be absent')
    # Reject output beneath any target directory to avoid accidental installation.
    if any(output.is_relative_to(ROOT / folder) for folder in ('web', 'catalogue', 'atlas', 'tools')):
        raise ValueError('Use a separate candidate directory outside shared source directories')
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'kind': 'bingham-integration-candidates-v1', 'installed': False,
               'review': approval['review'], 'inputs': json.loads((HERE/'INPUTS.json').read_text())['release_inputs'],
               'outputs': {name: sha(data) for name, data in result.items()}}
    for name, data in result.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    with (output/'RECEIPT.json').open('x') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
