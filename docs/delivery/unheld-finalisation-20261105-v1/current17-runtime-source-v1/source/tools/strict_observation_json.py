"""Decode saved binary64 observations without duplicate keys or nonfinite numbers.

Integer -0 is retained as floating negative zero for exact wire comparisons.
Other integer tokens retain their integer type; booleans remain booleans.
This is decoding policy, not validation of a response's schema or physics.
"""
import json
import math


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def _finite(value):
    try:
        valid = math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError('JSON number outside finite binary64 range')
    return value


def _integer(token):
    return -0.0 if token == '-0' else _finite(int(token))


def _constant(token):
    raise ValueError('nonfinite JSON constant: ' + token)


def loads(content):
    """Parse every number/key, including unknown and otherwise unused fields."""
    return json.loads(content, object_pairs_hook=_unique, parse_int=_integer,
                      parse_float=lambda token: _finite(float(token)),
                      parse_constant=_constant)
