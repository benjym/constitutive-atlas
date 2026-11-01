"""Canonical gzip transport for two immutable reference replay subprocesses.

Python 3.12's gzip.compress(mtime=0) delegates its OS header byte to zlib;
Python 3.14 writes the portable 255 byte. Preserve the complete original byte
comparison by canonicalizing only that header byte. All deflate bytes, payload,
mtime, CRC and length remain exact. No numerical values or budgets change.
"""
from pathlib import Path
import subprocess as _subprocess
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    ROOT / 'docs/reviews/tresca-pressure-split-v1/transform_full_precision.py',
    ROOT / 'docs/reviews/tresca-rounded-reference-v1/generate.py',
}

def canonical(data):
    if len(data) < 18 or data[:9] != bytes.fromhex('1f8b08000000000002') or data[9] not in (3, 255):
        raise ValueError('unexpected reference gzip framing')
    return data[:9] + b'\xff' + data[10:]

def run(args, **kwargs):
    registered = len(args) >= 3 and args[1] == '-B' and Path(args[2]).resolve() in SCRIPTS
    result = _subprocess.run(args, **kwargs)
    if registered and result.returncode == 0 and '--output' in args:
        path = Path(args[args.index('--output') + 1])
        path.write_bytes(canonical(path.read_bytes()))
    return result

subprocess = SimpleNamespace(run=run)
