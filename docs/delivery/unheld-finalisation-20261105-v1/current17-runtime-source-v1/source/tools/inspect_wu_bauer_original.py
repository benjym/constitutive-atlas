"""Research-only source algebra. No canonical sign map or stress integrator."""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas.dsl import Sym, Type, ValidationError, dimensions, evaluate, infer, parse
from atlas.model import ROOT


def load_fragment():
    fragment = json.loads((ROOT / 'catalogue/source-audits/wu-bauer-1994-original.json').read_text())
    receipt = json.loads((ROOT / 'catalogue/source-audits/original-papers-2026-10-31.json').read_text())
    source = next(r for r in receipt['records'] if r['id'] == 'wu-bauer-1994')
    if any(fragment['source'][key] != source[key] for key in ('url', 'sha256', 'local_filename')):
        raise ValidationError('source fragment does not match original-paper receipt')
    symbols = {name: Type(v['shape'], dimensions(v['unit'])) for name, v in fragment['inputs'].items()}
    for term in fragment['terms']:
        expected = Type(term['shape'], dimensions(term['unit']))
        if term['name'] in symbols or infer(parse(term['expression']), symbols) != expected:
            raise ValidationError('duplicate or incorrectly typed term: ' + term['name'])
        symbols[term['name']] = expected
    return fragment


def evaluate_fragment(fragment, *, stress, stretching, coefficients):
    """Evaluate printed Eq.(21), without assigning physical sign conventions."""
    if any(not isinstance(v, Sym) or len(v.v) != 6 for v in (stress, stretching)):
        raise ValidationError('stress and stretching require six Mandel components')
    if len(coefficients) != 4 or not all(math.isfinite(v) for v in (*stress.v, *stretching.v, *coefficients)):
        raise ValidationError('source inputs must be finite with four coefficients')
    if sum(stress.v[:3]) == 0:
        raise ValidationError('zero stress trace is undefined in the source law')
    env = dict(stress=stress, stretching=stretching, **dict(zip(('c1','c2','c3','c4'),coefficients)))
    try:
        for term in fragment['terms']:
            value = evaluate(parse(term['expression']), env)
            if not all(math.isfinite(v) for v in (value.v if isinstance(value, Sym) else (value,))):
                raise ValueError('nonfinite result')
            env[term['name']] = value
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValidationError('source algebra cannot evaluate without regularization') from exc
    return {t['name']: env[t['name']] for t in fragment['terms']}


def printed_calibration_ratios(vi, vf, rf):
    """Literal Eqs.(27),(28), p.842: exposes conflict, not a parameter converter."""
    di, df = math.sqrt(1+2*vi*vi), math.sqrt(1+2*vf*vf)
    denominator = df*(1-2*vi)*(rf*rf-4)+di*(2*vf-rf)*(rf-4)
    return ((9*df*vi*(rf*rf-4)+di*(2+rf)**2*(1+4*vf))/denominator,
            (9*vi*(2*vf-rf)*(rf-4)-(1-2*vi)*(rf+2)**2*(1+4*vf))/denominator)


if __name__ == '__main__':
    fragment = load_fragment()
    for record in fragment['published_parameter_sets']:
        result = evaluate_fragment(fragment, stress=Sym((100000.,)*3+(0.,)*3),
                                   stretching=Sym((-1.,0.,0.,0.,0.,0.)),
                                   coefficients=record['coefficients'])
        print(json.dumps({'parameter_set':record['id'], 'source_objective_rate_Pa_per_s':result['objective_rate'].v}))
