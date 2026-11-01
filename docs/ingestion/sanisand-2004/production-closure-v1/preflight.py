"""Read-only closure checks and independent Decimal elastic-entry identities.

No Atlas imports, model evaluator, source downloads, compiler or binary calls.
This is a packet preflight, not a candidate/backend acceptance assessor.
"""
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name):
    return json.loads((HERE / name).read_text())


def entries(grid, precision):
    rows = []
    with localcontext() as context:
        context.prec = precision
        d = Decimal
        for ev in grid['void_ratios']:
            e = d(ev)
            for pv in grid['pressures_pa']:
                p, pat = d(pv), d(grid['p_at'])
                G = d(grid['G0']) * pat * (d('2.97') - e)**2 / (1+e) * (p/pat).sqrt()
                b0 = d(grid['G0']) * d(grid['h0']) * (1-d(grid['ch'])*e) / (p/pat).sqrt()
                psi = e - d(grid['e0']) + d(grid['lambda_c']) * (d(grid['xi'])*(p/pat).ln()).exp()
                # For unit deviatoric triaxial normal, cos(3theta)=+/-1;
                # rational original Lode function gives g=1 or c.
                for direction in grid['directions']:
                    g = d(1) if direction == 'compression' else d(grid['c'])
                    b_dot_n = (d(2)/3).sqrt() * (g*d(grid['M'])*(-d(grid['nb'])*psi).exp()-d(grid['m']))
                    Hbar = d(2)/3*p*b0*b_dot_n
                    axial = p*d(grid['m'])/(3*G)
                    if direction == 'extension':
                        axial = -axial
                    # Independently recover cone norm from elastic stress:
                    # de=(axial,-axial/2,-axial/2), |dev(sigma)|=2G|de|.
                    elastic_norm = 2*G*(axial**2+2*(axial/2)**2).sqrt()
                    cone_radius = (d(2)/3).sqrt()*p*d(grid['m'])
                    defect = abs(elastic_norm-cone_radius)/cone_radius
                    assert defect < d(10)**(-precision+5)
                    assert b0 > 0 and Hbar > 0
                    rows.append({'e': ev, 'p_pa': pv, 'direction': direction,
                                 'G_pa': str(G), 'axial_yield_strain': str(axial),
                                 'b0': str(b0), 'Hbar_pa': str(Hbar),
                                 'relative_cone_identity_defect': str(defect)})
    return rows


def main():
    inventory = load('inputs.json')
    for item in inventory['files']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    decisions = load('decisions.json')
    assert decisions['signature'] is None and decisions['reviewer'] is None
    assert [x['id'] for x in decisions['decisions']] == [f'D{i:02}' for i in range(1,9)]
    assert all(x['status'] == 'unapproved' and x['reviewer'] is None for x in decisions['decisions'])
    plan = load('reference-plan.json')
    assert plan['status'] == 'prospective_not_yet_frozen'
    assert plan['candidate_observations_in_this_task'] is False
    assert len({f['id'] for f in plan['families']}) == 8
    assert all(f['inputs'] and f['oracle'] and f['coverage'] and f['gate'] for f in plan['families'])
    for path in ['models/research/sanisand-2004-fixed-memory-be.json',
                 'models/research/sanisand-2004-parent-reset-be.json']:
        record = json.loads((ROOT/path).read_text())
        assert record['schema_version'] == '0.1'  # Historical records remain unchanged.
        assert sum(6 if field['shape'] == 'sym' else 1 for field in record['state']) == 26
    schema = json.loads((ROOT/'schemas/model-v0.3.schema.json').read_text())
    residual = next(profile for profile in schema['oneOf']
                    if profile['properties'].get('formulation', {}).get('properties', {}).get('equation_form', {}).get('const') == 'incremental_residual')
    assert 'increment_reset' in residual['properties']
    assert 'initialization' in residual['required']
    assert plan['schema_target']['required_persistent_state'] == ['sigma','e','alpha','fabric','alpha_in']
    low, high = entries(plan['first_yield_grid'],80), entries(plan['first_yield_grid'],120)
    assert len(low) == len(high) == 18
    with localcontext() as context:
        context.prec = 120
        worst = Decimal(0)
        for left, right in zip(low, high):
            for field in ['G_pa','axial_yield_strain','b0','Hbar_pa']:
                a,b = Decimal(left[field]), Decimal(right[field])
                error = abs(a-b)/max(abs(a),abs(b))
                worst = max(worst,error)
                assert error < Decimal('1e-60')
    result = {'id':'ADMIT-sanisand-closure-v1-preflight','date':'2026-11-01',
              'scope':'Read-only exact-input and unsigned-plan checks; independent Decimal initial-yield algebra only',
              'pinned_inputs_verified':len(inventory['files']),
              'unsigned_decisions_verified':8,'prospective_reference_families_verified':8,
              'historical_research_records_unchanged':2,'state_components':26,
              'new_schema_target':'0.3 incremental_residual; increment_reset structurally available',
              'decimal_precisions':[80,120], 'first_yield_cases':len(high),
              'max_relative_precision_difference':str(worst),
              'arithmetic_adequacy_gate':'1e-60 relative; preflight arithmetic only, not a backend tolerance',
              'cases':high,'status':'pass',
              'limitations':['No full plastic reference constructed','No candidate, native, Wasm or browser observations',
                             'No scientific source/event decision or independent admission signed',
                             'Numerical backend acceptance budgets remain to be frozen before candidate execution']}
    (HERE/'preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'},indent=2))


if __name__ == '__main__':
    main()
