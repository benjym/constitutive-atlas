"""Scalar normalization diagnostic, not an HCA implementation.

Author manuscript equations (9), (14), (18), (37); other factors in (7)
remain identical. No stress integration, polarization or amplitude extraction.
"""
import math


def reference_scale(parameters):
    reference = parameters['e_ref']
    difference = parameters['C_e'] - reference
    if not math.isfinite(reference) or reference <= -1 or difference == 0:
        raise ValueError('finite e_ref > -1 distinct from C_e required')
    return (1 + reference) / difference**2


def change_void_reference(parameters, history, new_reference):
    transformed = dict(parameters, e_ref=new_reference)
    factor = reference_scale(parameters) / reference_scale(transformed)
    transformed['C_N1'] *= factor
    return transformed, factor * history


def amplitude_factor(parameters, amplitude):
    if not math.isfinite(amplitude) or amplitude < 0:
        raise ValueError('nonnegative finite strain amplitude required')
    # Preserve the source's literal cap; do not silently reparameterize it.
    return (amplitude / parameters['epsilon_ampl_ref'])**2 if amplitude <= 1e-3 else 100.0


def rates(parameters, history, amplitude, void_ratio):
    product = amplitude_factor(parameters, amplitude) * parameters['C_N1']
    history_rate = 0.0 if product == 0 else product * parameters['C_N2'] * math.exp(-history/product)
    total_rate = history_rate + product * parameters['C_N3']
    void_factor = reference_scale(parameters) * (parameters['C_e'] - void_ratio)**2 / (1 + void_ratio)
    return {'history_rate': history_rate, 'total_history_rate': total_rate,
            'void_factor': void_factor, 'accumulation_kernel': total_rate * void_factor}


def history_increment(parameters, history, amplitude, cycles):
    product = amplitude_factor(parameters, amplitude) * parameters['C_N1']
    if product == 0:
        return 0.0
    return product * math.log1p(parameters['C_N2'] * cycles * math.exp(-history/product))
