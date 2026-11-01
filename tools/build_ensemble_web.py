"""Package one pinned experiment for conditional replay, preserving radial controls."""
import gzip
import hashlib
import json
from pathlib import Path

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
    return manifest

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    bundle(parser.parse_args().output)
