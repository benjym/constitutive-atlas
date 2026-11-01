"""Independent saved-output assessor. No Atlas, DSL, integration or author imports."""
import argparse
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FREEZE = ROOT / 'docs/reviews/sanisand-v03-research-freeze-v1'
REFERENCE = ROOT / 'docs/references/sanisand-project-monotonic-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def require(test, message):
    if not test:
        raise ValueError(message)


def csv(text):
    return [float(x) for x in text.split(',')]


def context():
    # The execution freeze pins these manifests transitively before any build.
    for path in [FREEZE / 'manifest.json', REFERENCE / 'manifest.json']:
        for name, expected in load(path)['files'].items():
            target = path.parent / name if path.parent == FREEZE else ROOT / name
            require(sha(target) == expected, 'input pin: ' + name)
    model = load(FREEZE / 'model.json')
    return {'policy': load(FREEZE / 'policy.json'),
            'requests': load(FREEZE / 'trajectory-requests.json.gz'),
            'probes': load(FREEZE / 'negative-probes.json'),
            'references': {c['id']: c for c in load(REFERENCE / 'reference-p80-t12.json.gz')['cases']},
            'catalogue_hash': hashlib.sha256(json.dumps([model], sort_keys=True, separators=(',', ':')).encode()).hexdigest()}


def vector(values, size, label):
    require(isinstance(values, list) and len(values) == size, label + ' length')
    require(all(type(x) in (int, float) and math.isfinite(x) for x in values), label + ' finite numeric')
    return values


def scaled(a, b, pressure):
    require(len(a) == len(b) == 25, 'persistent layout')
    return max(abs(float(x) - float(y)) / (pressure if j < 6 else 1.0) for j, (x, y) in enumerate(zip(a, b)))


def diagnostic(value):
    require(isinstance(value, dict), 'diagnostics object')
    for key in ['iterations', 'substeps', 'rejected']:
        require(type(value.get(key)) is int and value[key] >= 0, 'diagnostic ' + key)
    fractions = value.get('increment_fractions')
    require(isinstance(fractions, list) and all(type(x) in (float, int) and math.isfinite(x) and x > 0 for x in fractions), 'increment fractions')
    if 'error' in value:
        require(value['error'] is None or type(value['error']) in (float, int) and math.isfinite(value['error']) and value['error'] >= 0, 'diagnostic error')


def inspect_path(request, response, ctx):
    """Check every saved point, with independent reference checks at all 18 samples."""
    args = request['args']; gate = ctx['policy']['trajectory']
    require(response.get('ok') is True, 'trajectory unsuccessful: ' + str(response.get('message')))
    require(response.get('model') == args[0] and response.get('catalogue_hash') == ctx['catalogue_hash'], 'model/catalogue identity')
    require(response.get('api_version') == 'experimental-recorded-replay-0.2', 'API version')
    require(response.get('failed_knot') == -1, 'failed knot')
    require(response.get('stress') == {'source':'state', 'name':'sigma', 'measure':'cauchy', 'scope':'effective', 'tensor_representation':'mandel', 'sign':'compression_positive'}, 'stress metadata')
    for key, offset in [('parameters',1), ('initial',2), ('initial_strain',3), ('controls_wire',4), ('knots_wire',5)]:
        require(response.get(key) == csv(args[offset]), 'echoed input ' + key)
    material = dict(zip(['residual_tolerance', 'rate_tolerance', 'max_iterations', 'max_depth', 'max_substeps', 'max_backtracks'], csv(args[6])))
    material.update(version='incremental-settings-0.1', norm='scaled_component_max')
    control = dict(zip(['control_tolerance','max_iterations','max_backtracks','max_material_trials','finite_difference_step'], csv(args[7])))
    require(response.get('integration_settings') == material, 'material policy')
    require(response.get('control_settings') == control, 'recorded policy')
    require('restart_settings' not in response, 'unexpected restart policy')
    points = response.get('points'); require(isinstance(points, list) and len(points) == request['knots_count'], 'incomplete point history')
    require(points[0]['state'] == csv(args[2]), 'initial state changed')
    pressure = sum(csv(args[2])[:3]) / 3
    flat = csv(args[5]); knots = [flat[i:i+7] for i in range(0, len(flat), 7)]
    m = csv(args[1])[7]; p_at = csv(args[1])[-1]
    max_yield = 0.0; max_trace = 0.0; max_strain = 0.0; max_control = 0.0
    with localcontext() as arithmetic:
        arithmetic.prec = 50
        for index, (point, knot) in enumerate(zip(points, knots)):
            state = vector(point.get('state'), 26, 'state'); strain = vector(point.get('strain'), 6, 'strain')
            require(point.get('coordinate') == knot[0], 'coordinate/order')
            require(type(point.get('control_error')) in (int, float) and math.isfinite(point['control_error']) and point['control_error'] >= 0, 'control error numeric')
            max_control = max(max_control, point['control_error'])
            max_strain = max(max_strain, max(abs(x-y) for x,y in zip(strain, knot[1:])))
            require(state[25] >= 0, 'negative temporary multiplier')
            require(state[19:25] == [0.0]*6, 'fixed anchor changed')
            require(state[6] > 0 and 1 - csv(args[1])[9]*state[6] > 0, 'void ratio domain')
            # Decimal over literal binary64 state avoids cancellation in the yield audit.
            z = [Decimal.from_float(float(x)) for x in state]
            p = sum(z[:3]) / 3; require(p > 0, 'nonpositive pressure')
            eta = [z[i]/p - (1 if i < 3 else 0) - z[i+7] for i in range(6)]
            excess = p * (sum(x*x for x in eta).sqrt() - (Decimal(2)/3).sqrt()*Decimal.from_float(m)) / Decimal.from_float(p_at)
            max_yield = max(max_yield, float(max(excess, Decimal(0))))
            max_trace = max(max_trace, *(abs(float(sum(z[o:o+3]))) for o in [7,13,19]))
            diagnostic(point.get('diagnostics'))
    require(max_yield <= float(gate['maximum_positive_yield_excess_over_p_at']), 'positive yield excess')
    require(max_trace <= float(gate['history_trace_absolute']), 'history trace')
    require(max_strain <= float(gate['strain_control_absolute']), 'strain control')
    require(max_control <= float(gate['recorded_control_error_max']), 'recorded control error')
    require(response.get('state') == points[-1]['state'] and response.get('strain') == points[-1]['strain'], 'endpoint mismatch')
    for key in ['material_trials','finite_difference_probes','attempted_substeps']:
        require(type(response.get(key)) is int and response[key] >= 0, 'aggregate diagnostic ' + key)
    samples = ctx['references'][request['case']]['samples']
    errors = [scaled(points[i]['state'][:25], s['state'], pressure) for i,s in zip(request['sample_indices'], samples)]
    require(len(errors) == 18, 'reference sample layout')
    require(errors[1] <= float(gate['exact_first_yield_scaled_state_error']), 'first-yield accuracy')
    if request['plastic_steps'] == 1024:
        require(max(errors) <= float(gate['fine_maximum_scaled_state_error']), 'fine trajectory accuracy')
    return {'maximum_scaled_state_error': max(errors), 'first_yield_scaled_error': errors[1],
            'maximum_yield_excess_over_p_at': max_yield, 'maximum_trace': max_trace,
            'maximum_strain_control_error': max_strain, 'maximum_recorded_control_error': max_control,
            'points_checked': len(points), 'reference_components_checked': 18*25}


def inspect_probes(records, ctx):
    failures=[]; checked=0
    for probe in ctx['probes']['probes']:
        for r, expected_ok in [(probe,False), (dict(ctx['probes']['recover_after_each'], id='recovery/' + probe['id']),True)]:
            try:
                response = records[r['id']]
                require(response.get('ok') is expected_ok, 'probe result')
                if expected_ok or r['full_rollback']:
                    require(vector(response.get('state'),26,'probe state') == csv(r['args'][2]), 'full incoming state preservation')
                checked += 1
            except (ValueError, KeyError, TypeError) as exc:
                failures.append({'id':r['id'],'gate':str(exc)})
    return checked, failures


def assess_records(records, ctx):
    """records is an exact id->response mapping; missing/extra outputs never disappear."""
    expected = {r['id'] for r in ctx['requests']}
    probes = ctx['probes']['probes']
    expected |= {p['id'] for p in probes} | {'recovery/'+p['id'] for p in probes}
    transaction_ids = {'transaction/'+x for x in ['A','B','A-repeat','zero','restart-A']}
    expected |= transaction_ids
    failures = [{'id':x,'gate':'unexpected response'} for x in sorted(set(records)-expected)]
    failures += [{'id':x,'gate':'missing response'} for x in sorted(expected-set(records))]
    rows = {}; by_case = {}
    for request in ctx['requests']:
        try:
            row = inspect_path(request, records[request['id']], ctx)
            rows[request['id']] = row
            by_case.setdefault(request['case'], {})[request['plastic_steps']] = row['maximum_scaled_state_error']
        except (ValueError, KeyError, TypeError, ArithmeticError) as exc:
            failures.append({'id':request['id'],'gate':str(exc)})
    refinement=[]; gate=ctx['policy']['trajectory']
    for case in sorted({r['case'] for r in ctx['requests']}):
        errors = by_case.get(case,{})
        if set(errors) != {256,512,1024}:
            failures.append({'id':case,'gate':'refinement unavailable: failed or missing trajectory'});continue
        for coarse,fine in [(256,512),(512,1024)]:
            ratio = errors[fine]/errors[coarse] if errors[coarse] else None
            required = errors[coarse] > float(gate['refinement_ratio_not_required_below'])
            refinement.append({'case':case,'coarse':coarse,'fine':fine,'ratio':ratio,'required':required})
            if required and (ratio is None or ratio > float(gate['first_order_refinement_ratio_max'])):
                failures.append({'id':case,'gate':'refinement ratio','coarse':coarse,'fine':fine,'ratio':ratio})
    probe_count, probe_failures = inspect_probes(records,ctx); failures.extend(probe_failures)
    try:
        parent_response = records['compression-e0.735-p100000/N1024']
        require(parent_response.get('ok') is True and len(parent_response['points']) == 1026,'transaction parent unavailable')
        parent = parent_response['points'][513]['state']
        a,b,again,zero,restart = [records['transaction/'+key] for key in ['A','B','A-repeat','zero','restart-A']]
        for name,response in [('A',a),('A-repeat',again),('zero',zero),('restart-A',restart)]:
            require(response.get('ok') is True,name+' unsuccessful')
            vector(response.get('state'),26,name+' state')
        require(b.get('ok') is False and b.get('state') == parent,'transaction full rollback')
        require(a['state'] == again['state'] == restart['state'],'transaction retry/restart mismatch')
        require(scaled(zero['state'][:25],parent[:25],sum(parent[:3])/3) <= 1e-8,'zero persistent drift')
        require(zero['state'][25] == 0,'zero temporary field reset')
        transaction_pass=True
    except (ValueError,KeyError,IndexError,TypeError) as exc:
        failures.append({'id':'transactions','gate':str(exc)});transaction_pass=False
    return {'research_qualification_pass':not failures,'successful_trajectory_checks':len(rows),
            'expected_trajectories':81,'probe_checks_passed':probe_count,'transactions_pass':transaction_pass,
            'rows':rows,'refinement':refinement,'failures':failures,'scientific_signature':None}


def read_records(directory):
    index=load(directory/'index.json'); records={}; receipts={}
    require(index.get('status') == 'completed', 'incomplete execution index')
    build = directory / 'build-receipt.json'
    require(sha(build) == index['build_receipt_sha256'], 'build receipt pin')
    for item in index['records']:
        path=directory/item['file'];require(sha(path)==item['sha256'],'response receipt pin')
        receipt=load(path); require(item['id']==receipt['request']['id'],'receipt id mismatch')
        require(item['id'] not in records,'duplicate receipt id')
        # Process exceptions/invalid JSON remain represented as failed outputs.
        response=receipt.get('response')
        if not isinstance(response,dict):response={'ok':False,'message':'process/JSON failure: '+str(receipt.get('exception'))}
        records[item['id']]=response; receipts[item['id']]=receipt
    ctx = context()
    expected = {r['id']: r for r in ctx['requests']}
    for probe in ctx['probes']['probes']:
        expected[probe['id']] = probe
        recovery = dict(ctx['probes']['recover_after_each'], id='recovery/'+probe['id'])
        expected[recovery['id']] = recovery
    parent_response = records.get('compression-e0.735-p100000/N1024', {})
    if parent_response.get('ok') is True and len(parent_response.get('points', [])) == 1026:
        parent = parent_response['points'][513]['state']
        base = ctx['probes']['recover_after_each']['args']; parent_csv = ','.join(repr(float(x)) for x in parent)
        trials = list(ctx['probes']['dependent_transactions']['trials']) + [{'id':'restart-A', 'strain':'1e-5,-5e-6,-5e-6,0,0,0'}]
        for trial in trials:
            args = [base[0],base[1],parent_csv,trial['strain']]
            if 'settings' in trial: args.append(trial['settings'])
            r = {'id':'transaction/'+trial['id'], 'function':'atlas_integrate_with_settings' if len(args)==5 else 'atlas_integrate', 'types':['string']*len(args), 'args':args}
            expected[r['id']] = r
    for name, receipt in receipts.items():
        require(receipt['request'] == expected.get(name), 'actual request differs from freeze: '+name)
        response = receipt.get('response', {})
        require(json.loads(receipt['stdout']) == response, 'parsed/raw response mismatch')
        expected_code = 0 if index['backend']=='wasm' or response.get('ok') is True else 1
        require(receipt['returncode'] == expected_code, 'process return code')
    return records


def assess_parity(a,b,ctx):
    worst=0.;checked=0
    for r in ctx['requests']:
        x=a.get(r['id'],{});y=b.get(r['id'],{})
        require(x.get('ok') is True and y.get('ok') is True,'parity requires successful full histories')
        require(len(x['points'])==len(y['points'])==r['knots_count'],'parity history length')
        p=sum(csv(r['args'][2])[:3])/3
        for l,h in zip(x['points'],y['points']):
            require(l['coordinate']==h['coordinate'],'parity coordinate')
            worst=max(worst,scaled(vector(l['state'],26,'native state')[:25],vector(h['state'],26,'wasm state')[:25],p));checked+=25
    require(worst<=float(ctx['policy']['parity']['maximum_scaled_persistent_difference']),'backend parity')
    return {'pass':True,'persistent_components':checked,'maximum_scaled_difference':worst}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);parser.add_argument('--other',type=Path);o=parser.parse_args()
    ctx=context(); records=read_records(o.directory); result=assess_records(records,ctx)
    if o.other:
        try:result['parity']=assess_parity(records,read_records(o.other),ctx)
        except (ValueError,KeyError,TypeError) as exc:result['parity']={'pass':False,'failure':str(exc)};result['research_qualification_pass']=False
    print(json.dumps(result,indent=2,allow_nan=False))
    raise SystemExit(0 if result['research_qualification_pass'] else 1)
