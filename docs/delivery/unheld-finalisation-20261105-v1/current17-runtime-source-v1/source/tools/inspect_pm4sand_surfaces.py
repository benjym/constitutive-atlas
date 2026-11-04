"""Evaluate a source fragment through the existing DSL; never run a material solver.

This research helper is not a constitutive update or a supported model API.
"""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas.dsl import Sym, Type, ValidationError, dimensions, evaluate, infer, parse
from atlas.model import ROOT


def load_fragment():
    path = ROOT / 'catalogue/source-audits/pm4sand3d-1.0-surfaces.json'
    fragment = json.loads(path.read_text())
    audit = json.loads((ROOT / 'catalogue/source-audits/pm4sand-manuals-2026-10-31.json').read_text())
    manual = next(m for m in audit['manuals'] if m['model_id'] == fragment['model_id'])
    if (fragment['source']['sha256'], fragment['source']['url']) != (manual['sha256'], manual['url']):
        raise ValidationError('fragment does not match the pinned manual')
    symbols = {name: Type(v['shape'], dimensions(v['unit'])) for name, v in fragment['inputs'].items()}
    for term in fragment['terms']:
        expected = Type(term['shape'], dimensions(term['unit']))
        if term['name'] in symbols or infer(parse(term['expression']), symbols) != expected:
            raise ValidationError('duplicate or incorrectly typed source term: ' + term['name'])
        symbols[term['name']] = expected
    return fragment


def evaluate_fragment(fragment, *, r, alpha, c, m):
    """Evaluate only within the declared audit domain, without altering inputs."""
    tensors = (r, alpha)
    if any(not isinstance(v, Sym) or len(v.v) != 6 for v in tensors):
        raise ValidationError('r and alpha require six Mandel components')
    if not all(math.isfinite(v) for t in tensors for v in t.v) or not all(math.isfinite(v) for v in (c, m)):
        raise ValidationError('source fragment inputs must be finite')
    domain = fragment['audit_domain']
    if not domain['c_min'] <= c <= domain['c_max'] or m <= 0:
        raise ValidationError('parameters outside the declared audit domain')
    for tensor in tensors:
        scale = max(1., max(abs(v) for v in tensor.v))
        if abs(sum(tensor.v[:3])) > domain['trace_relative_tolerance'] * scale:
            raise ValidationError('source fragment requires deviatoric tensors')
    if all(a == b for a, b in zip(r.v, alpha.v)):
        raise ValidationError('zero direction has no selected source policy')
    env = dict(r=r, alpha=alpha, c=c, m=m)
    try:
        for term in fragment['terms']:
            env[term['name']] = evaluate(parse(term['expression']), env)
            value = env[term['name']]
            components = value.v if isinstance(value, Sym) else (value,)
            if not all(math.isfinite(v) for v in components):
                raise ValueError('nonfinite result')
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValidationError('fragment cannot evaluate this direction without regularization') from exc
    return {t['name']: env[t['name']] for t in fragment['terms']}


def main():
    fragment = load_fragment()
    zero = Sym((0.,) * 6)
    for name, components in [('compression', (2., -1., -1., 0., 0., 0.)),
                             ('extension', (-2., 1., 1., 0., 0., 0.)),
                             ('simple-shear', (0., 0., 0., 1., 0., 0.))]:
        result = evaluate_fragment(fragment, r=Sym(components), alpha=zero, c=.71, m=.01)
        print(json.dumps(dict(direction=name, cos3theta=result['cos3theta'], g=result['g'])))


if __name__ == '__main__':
    main()
