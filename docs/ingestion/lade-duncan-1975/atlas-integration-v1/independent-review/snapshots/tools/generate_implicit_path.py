"""Regenerate the reviewed versioned generic profile with the normal compiler."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.compiler import generate

MODEL_ID = 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
INPUTS = (
    'models/research/implicit-path/' + MODEL_ID + '.json',
    'tests/fixtures/implicit-path-v1/baseline-v2.json',
    'tests/fixtures/implicit-path-v1/hypoplastic-sand-vw96.json',
    'tests/fixtures/implicit-path-v1/linear-elastic.json',
)
EXPECTED = {
    'models.hpp': 'c00d9b0c8ed038810d5aa19d3c72def4824667696caac48076e3ab62d1c1ef13',
    'models.json': '2919cc4d5699cad7d4e0d8f8c30a7479333a4dfc3b7b185b685c96e64d68b591',
}


def regenerate(destination):
    destination = Path(destination)
    generate(destination, [ROOT / name for name in INPUTS])
    outputs = {name: hashlib.sha256((destination/name).read_bytes()).hexdigest()
               for name in EXPECTED}
    if outputs != EXPECTED:
        raise ValueError('Versioned implicit-path compiler output changed; impact review required')
    return {'ordered_inputs': [{'path': name, 'sha256': hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
                               for name in INPUTS], 'outputs': outputs}


if __name__ == '__main__':
    print(json.dumps(regenerate(sys.argv[1]), indent=2))
