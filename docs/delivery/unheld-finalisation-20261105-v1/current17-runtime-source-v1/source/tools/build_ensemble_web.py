"""Package compatible curated replay tests without changing public-data admission."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = 'OPARA-TXCD-100'
SOURCE_SHA = '49681ae77388fb0f3f081cbebfd263cb328b9bc678ed5a376a19e6c4dba82b35'
MEMBER_SHA = '787d207c982beedf99e96b054899ba8069e4261f80fba024fdbc3549745b27cd'

def bundle(destination, root=ROOT):
    root, destination = Path(root), Path(destination)
    entry = next(e for e in json.loads((root/'data/curated/index.json').read_text())['records'] if e['id'] == EXPERIMENT)
    raw = (root/'data/curated'/entry['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError('Ensemble curated experiment hash mismatch')
    source = json.loads(gzip.decompress(raw))
    provenance = source['provenance']
    if (source['id'] != EXPERIMENT or source['protocol'] != 'drained-triaxial' or
        len(source['rows']) != entry['rows'] or len(source['rows']) != 1438 or
        provenance['archive_sha256'] != SOURCE_SHA or provenance['member_sha256'] != MEMBER_SHA or
        provenance['license'] != 'CC-BY-4.0'):
        raise ValueError('Ensemble source identity mismatch')
    keys = ['axial_strain', 'radial_effective_stress', 'q', 'volumetric_strain']
    record = dict(version='atlas-ensemble-experiment-0.1', id=source['id'],
                  material=source['material'], protocol=source['protocol'],
                  conventions=source['conventions'], initial=source['initial'],
                  provenance=provenance, warnings=source['warnings'],
                  source_asset_sha256=entry['sha256'],
                  rows=[{key: row[key] for key in keys} for row in source['rows']])
    content = (json.dumps(record, separators=(',', ':'), ensure_ascii=False, allow_nan=False)+'\n').encode()
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'ensemble-experiment.json').write_bytes(content)
    manifest = dict(version='atlas-ensemble-asset-0.1', path='ensemble-experiment.json',
                    sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content))
    (destination/'ensemble-index.json').write_text(json.dumps(manifest, indent=2)+'\n')
    # The normal public experiment catalogue remains the selector authority.
    # Only records with explicit effective-stress initialization and complete
    # triaxial channels receive replay assets. Source-only records stay browsable.
    tests = [dict(id=EXPERIMENT, **{k: manifest[k] for k in ('path', 'sha256', 'size_bytes')})]
    test_dir = destination/'ensemble-tests'
    test_dir.mkdir(exist_ok=True)
    index = json.loads((root/'data/curated/index.json').read_text())
    for item in index['records']:
        if item['kind'] != 'experiment' or item['id'] == EXPERIMENT:
            continue
        compressed = (root/'data/curated'/item['path']).read_bytes()
        if hashlib.sha256(compressed).hexdigest() != item['sha256']:
            raise ValueError('Curated replay source hash mismatch')
        candidate = json.loads(gzip.decompress(compressed))
        initial = candidate.get('initial', {})
        if (candidate.get('protocol') not in ('drained-triaxial', 'undrained-triaxial')
                or len(initial.get('effective_stress', [])) != 6
                or not isinstance(initial.get('void_ratio'), (float, int))
                or not 2 <= len(candidate['rows']) <= 5001):
            continue
        required = ['axial_strain', 'radial_effective_stress', 'q', 'volumetric_strain']
        if candidate['protocol'] == 'undrained-triaxial':
            required += ['cell_pressure', 'pore_pressure', 'p']
        if not all(all(key in row for key in required) for row in candidate['rows']):
            continue
        if candidate['provenance'].get('license') != 'CC-BY-4.0':
            raise ValueError('Replay asset requires established public redistribution rights')
        channels = required + ['elapsed_time']
        replay = dict(version='atlas-ensemble-experiment-0.2',
                      **{k: candidate[k] for k in ('id', 'material', 'protocol', 'conventions', 'initial', 'provenance', 'warnings')},
                      source_asset_sha256=item['sha256'],
                      rows=[{k: row[k] for k in channels if k in row} for row in candidate['rows']])
        encoded = (json.dumps(replay, separators=(',', ':'), ensure_ascii=False, allow_nan=False)+'\n').encode()
        relative = 'ensemble-tests/'+item['id']+'.json'
        (destination/relative).write_bytes(encoded)
        tests.append(dict(id=item['id'], path=relative, sha256=hashlib.sha256(encoded).hexdigest(), size_bytes=len(encoded)))
    (destination/'ensemble-tests.json').write_text(json.dumps(dict(version='atlas-ensemble-tests-0.1', tests=tests), indent=2)+'\n')
    # Keep the pinned library and MIT attribution local to the packaged site.
    vendor = destination/'vendor'
    vendor.mkdir(exist_ok=True)
    notice = json.loads((root/'web/vendor/plotly-NOTICE.json').read_text())
    for name, receipt in notice['files'].items():
        content = (root/'web/vendor'/name).read_bytes()
        if hashlib.sha256(content).hexdigest() != receipt['sha256'] or len(content) != receipt['size_bytes']:
            raise ValueError('Plotly dependency differs from its pinned receipt')
        (vendor/name).write_bytes(content)
    shutil.copyfile(root/'web/vendor/plotly-NOTICE.json',vendor/'plotly-NOTICE.json')
    return manifest

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    bundle(parser.parse_args().output)
