"""Geometry/transaction specification only; not a constitutive material solver."""
from copy import deepcopy
from math import isfinite, sqrt

PROFILE = 'atlas-corrected-four-contour-parent-v1'
ZERO_COMPONENT = 1e-12
MIN_RADIUS = 1e-15


def norm(v):
    return sqrt(sum(x*x for x in v))


def vector(v):
    if len(v) != 3 or any(not isfinite(x) for x in v):
        raise ValueError('three finite local deviatoric coordinates required')
    return list(v)


def prepare():
    return {'profile': PROFILE, 'x': [0., 0., 0.],
            'anchor': [0., 0., 0.], 'gamma': 0.,
            'contours': [{'center': [0., 0., 0.], 'radius': 0.}]}


def validate(s):
    if s['profile'] != PROFILE:
        raise ValueError('incompatible lifecycle profile')
    vector(s['x']); vector(s['anchor'])
    if not isfinite(s['gamma']) or s['gamma'] < 0:
        raise ValueError('invalid degradation distance')
    if not 1 <= len(s['contours']) <= 4:
        raise ValueError('one to four contours required')
    if s['contours'][0]['center'] != [0., 0., 0.]:
        raise ValueError('primary contour center must remain at the origin')
    for c in s['contours']:
        vector(c['center'])
        if not isfinite(c['radius']) or c['radius'] < 0:
            raise ValueError('invalid contour radius')
    distance = norm([a-b for a,b in zip(s['x'],s['contours'][-1]['center'])])
    if abs(distance-s['gamma']) > 1e-13*max(1.,distance):
        raise ValueError('inconsistent endpoint/degradation distance')


def trial(committed, increment, *, creation_permitted=True):
    """One parent-endpoint proposal, always read from the committed snapshot.

    Caller owns all-point commit, coupled stiffness convergence and failure gate.
    The explicit source-style component rounding applies before accumulation.
    No phase index, material solver or plastic history is implemented here.
    """
    validate(committed)
    if not isinstance(creation_permitted, bool):
        raise ValueError('creation permission must be a Boolean')
    dx = [0. if abs(a) < ZERO_COMPONENT else a for a in vector(increment)]
    s = deepcopy(committed)
    if not any(dx):
        return s, 'hold'
    x = [a+b for a,b in zip(committed['x'],dx)]
    s['x'] = x
    cs = s['contours']
    # The first reached outer contour wins, matching the outer-to-inner listing.
    for k,c in enumerate(cs[:-1]):
        d = norm([a-b for a,b in zip(x,c['center'])])
        if d >= c['radius'] and d > MIN_RADIUS:
            s['contours'] = cs[:k+1]
            c['radius'] = d
            s['anchor'] = ([0.,0.,0.] if k == 0 else
                           [2*b-a for a,b in zip(x,c['center'])])
            s['gamma'] = d
            validate(s)
            return s, 'erase-inner'
    c = cs[-1]
    d = norm([a-b for a,b in zip(x,c['center'])])
    if d >= c['radius'] and d > MIN_RADIUS:
        if len(cs) > 1:
            c['center'] = [(a+b)/2 for a,b in zip(x,s['anchor'])]
        d = norm([a-b for a,b in zip(x,c['center'])])
        c['radius'] = d
        event = 'grow-active'
    elif (d < c['radius'] and c['radius'] > MIN_RADIUS
          and creation_permitted and len(cs) < 4):
        s['anchor'] = list(committed['x'])
        center = [(a+b)/2 for a,b in zip(x,s['anchor'])]
        d = norm([a-b for a,b in zip(x,center)])
        cs.append({'center': center, 'radius': d})
        event = 'create'
    else:
        event = ('depth-saturated' if creation_permitted and len(cs) == 4
                 and d < c['radius'] else 'inside-active')
    s['gamma'] = d
    validate(s)
    return s, event
