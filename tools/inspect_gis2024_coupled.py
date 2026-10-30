"""Typed instantaneous14-state composition of the selected HP and GIS fragments.

No defaults, state integration, hidden preparation, oracle calls or admission.
"""
import math
from atlas.dsl import Sym, ValidationError, parse
from atlas.history import _evaluate
from tools import inspect_gis2024_hp_host as hp
from tools import inspect_gis2024_rates as gis

HP_PARAMETERS=frozenset({'phi','hs','ei0','ec0','ed0','n','alpha','beta'})
GIS_PARAMETERS=frozenset({'R','m_R','m_T','beta_R','chi_R','gamma_chi','chi_0','chi_max','C_Omega','gamma_Omega'})


def coupled_rates(state,de,parameters):
    """Evaluate compression-positive directional derivatives, without advancing.

    state: exact sigma:Sym,e:real,h:Sym,Omega:real; de:Sym; explicit18 parameters.
    Named tensor rates are Sym. derivative is the14-component list ordered
    sigma6,e,h6,Omega. At zero de the directional k/q/suppression are None.
    """
    if not isinstance(state,dict) or set(state)!={'sigma','e','h','Omega'}:
        raise ValidationError('exact sigma/e/h/Omega state fields required')
    if not isinstance(parameters,dict) or set(parameters)!=HP_PARAMETERS|GIS_PARAMETERS:
        raise ValidationError('exact18 selected HP/GIS material parameters required')
    # Copy and validate every scalar/component, including GIS parameters, before
    # evaluating either fragment; neither helper receives caller-owned tensors.
    p={name:gis.real(value) for name,value in parameters.items()}
    sigma=gis.vector(state['sigma']);h=gis.vector(state['h']);d=gis.vector(de)
    e=gis.real(state['e']);Omega=gis.real(state['Omega'])
    if math.sqrt(sum(x*x for x in h.v))>p['R']:
        raise ValidationError('full pairing memory outside strict radius; no projection')
    host=hp.host(hp.load_fragment(),sigma=sigma,e=e,**{name:p[name] for name in HP_PARAMETERS})
    rate=gis.rates(gis.load_fragment(),E=host['E'],de=d,h=h,Omega=Omega,
                   **{name:host[name] for name in ('m','C','S','f')},
                   **{name:p[name] for name in GIS_PARAMETERS})
    if rate['suppression'] is not None and rate['suppression']<=0:
        raise ValidationError('positive suppression underflow in selected HP/GIS pairing')
    try:
        e_rhs=gis.real(_evaluate(parse('-(1+e)*trace(de)'),{'e':e,'de':d}))
    except (ArithmeticError,ValueError,TypeError) as exc:
        raise ValidationError('coupled void-ratio arithmetic failure: '+str(exc)) from exc
    sigma_rhs=gis.vector(rate['sigma_rhs']);h_rhs=gis.vector(rate['h_rhs'])
    Omega_rhs=gis.real(rate['Omega_rhs'])
    diagnostics={name:rate[name] for name in ('rho','chi','gamma','k','q','suppression')}
    diagnostics.update(fdAstar=host['env']['fdAstar'],S=host['S'])
    return dict(sigma_rhs=sigma_rhs,e_rhs=e_rhs,h_rhs=h_rhs,Omega_rhs=Omega_rhs,
                derivative=list(sigma_rhs.v)+[e_rhs]+list(h_rhs.v)+[Omega_rhs],
                diagnostics=diagnostics)
