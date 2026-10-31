"""Exact historical-byte checks, separate from approved current model revisions."""
import hashlib
from pathlib import Path
from atlas.evidence import checked_receipt


def pinned_source(root, name, expected):
    """Select exact bytes named by a caller's original immutable receipt."""
    root = Path(root)
    path = root / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        path = root / 'catalogue/source-snapshots' / expected / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('historical source bytes differ: ' + name)
    return path


def preserved_model(root, name):
    """Only the documented DP domain revision supersedes a preview's old model."""
    root = Path(root)
    current = root / 'models' / name
    if name != 'drucker-prager.json':
        return current.read_bytes()
    packet = 'catalogue/investigations/dp-dilatancy-domain-v1'
    document = packet + '/manifest.json'
    previous_hash = 'd40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d'
    candidate_hash = 'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877'
    before = checked_receipt(root, document, packet + '/previous-definition.json', previous_hash)
    after = checked_receipt(root, document, packet + '/candidate-definition.json', candidate_hash)
    if current.read_bytes() != after.read_bytes():
        raise ValueError('current DP definition differs from its approved domain revision')
    return before.read_bytes()
