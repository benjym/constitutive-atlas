"""Package exact applicability metadata and source documents, without measurements."""
import hashlib
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.applicability import validate_matrix
from atlas.source_replay import strict_json


def bundle(destination, *, root=ROOT):
    root = Path(root)
    content = (root/'catalogue/applicability/kfs-development-v1.json').read_bytes()
    matrix = strict_json(content)
    validate_matrix(matrix, root=root)
    pins = [matrix['dataset'][k] for k in ('allocation', 'reservations')]
    pins += [pin for row in matrix['rows'] for pin in row['evidence']]
    sources = {}
    for pin in pins:
        body = (root/pin['path']).read_bytes()
        if hashlib.sha256(body).hexdigest() != pin['sha256']:
            raise ValueError('Applicability source changed during packaging: ' + pin['path'])
        sources[pin['path']] = body
    # Finish every validation/read before modifying any destination file.
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name, body in sources.items():
        target = destination/'applicability-records'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    (destination/'applicability.json').write_bytes(content)
    return matrix
