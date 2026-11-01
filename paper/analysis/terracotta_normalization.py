"""Paper-only normalization audit of the source-pinned Figure 1 equations.

This is a parameter/state reparameterization, not a new constitutive law or
initialization adapter. It applies only to positive meso-temperature scaling.
"""
import math


def rescale(parameters, state, factor):
    if not math.isfinite(factor) or factor <= 0:
        raise ValueError('positive finite meso-temperature scale required')
    parameters, state = dict(parameters), dict(state)
    parameters['alpha'] *= factor
    parameters['gamma'] *= factor
    parameters['eta'] /= factor
    parameters['Gamma'] *= factor**2
    state['Tm'] *= factor
    return parameters, state


def invariant_coefficients(parameters):
    root = math.sqrt(parameters['Gamma'])
    return {'A': parameters['alpha']/root, 'C': parameters['gamma']/root,
            'H': parameters['eta']*root}
