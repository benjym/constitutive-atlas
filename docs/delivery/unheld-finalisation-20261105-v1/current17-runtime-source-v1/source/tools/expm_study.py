"""Replay and assess checked expm values, full Mandel Jacobians and contexts.

Tolerances are operator-wide normwise budgets, not relative componentwise or
positive-definiteness certificates. No scientific model admission is implied.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.symmetric_expm import VERSION as OPERATOR_VERSION
from tools.reference_symmetric_expm import oracle, cases, digest

VERSION = 'checked-symmetric-expm-study-v1'
REFERENCE = ROOT / 'catalogue/investigations/symmetric-expm-reference-v1/reference.json'
VALUE_BUDGET = 2e-13
JACOBIAN_BUDGET = 1e-12
CONTEXTS = frozenset('''common_engine_accepted_partition_recurrence common_engine_failed_replay_rollback compiled_derivative_failure derivative_only_overflow_rejected_preserves derived_good_success eager_derived_check_only_failure eager_unused_derived_failure history_active_failure_rollback history_inactive_unsupported_skipped history_valid_output history_valid_recovery_parent_isolation initial_check_active_fails initial_check_inactive last_derivative_nan_rejected_preserves lazy_unsupported_arm_selected_fails lazy_unsupported_arm_skipped masked_domain_failure observable_bad_fails observable_inactive_skipped observable_only_skips_bad_equation primitive_alias_failure_preserves primitive_alias_success reset_full_integration_rollback reset_guard_masked_failure reset_value_active_failure reset_value_inactive_skipped sticky_flag_not_restored time_check_only_skips_equation time_equation_selected_fails'''.split())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))


def vector(value, size):
    require(type(value) is list and len(value) == size, 'numeric vector shape')
    require(all(type(x) in (int, float) and math.isfinite(x) for x in value), 'finite real vector required')
    return value


def matrix(value):
    require(type(value) is list and len(value) == 6, 'Jacobian row count')
    return [vector(row, 6) for row in value]


def scaled_error(actual, expected):
    return math.hypot(*(a-b for a,b in zip(actual, expected))) / max(1., math.hypot(*expected))


def catalogue():
    from atlas.model import load
    models = [load(p) for p in sorted((ROOT/'tests/fixtures/expm').glob('*.json'))]
    require(len(models) == 9, 'nine isolated model fixtures required')
    # Compiler uses this canonical model-list encoding for the runtime hash.
    return models, hashlib.sha256(json.dumps(models, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def reference():
    ref = read(REFERENCE)
    require(ref['script_sha256'] == sha(ROOT/'tools/reference_symmetric_expm.py'), 'reference script changed')
    require([(c['id'], c['input']) for c in ref['cases']] == [(c['id'], c['input']) for c in cases()], 'reference corpus identity')
    return ref


def invalid_requests():
    result = [('above-support', [math.nextafter(64., math.inf),0,0,0,0,0]), ('large-norm', [60.,60.,0,0,0,0])]
    rows = [{'id': name, 'csv': ','.join(map(str, a)), 'input': a, 'parseable': True} for name,a in result]
    for token in ('nan', 'inf', '-inf'):
        for i in range(6):
            a=['0']*6;a[i]=token
            rows.append({'id': f'{token}-component-{i}', 'csv': ','.join(a), 'parseable': False})
    rows.extend({'id': name, 'csv': text, 'parseable': False} for name,text in [('short','0,0,0,0,0'),('long','0,0,0,0,0,0,0'),('text','true,0,0,0,0,0')])
    return rows


def validate_response(response, a, model_hash, success=True):
    require(type(response) is dict, 'object response')
    require(response.get('operator_version') == OPERATOR_VERSION, 'runtime operator identity')
    require(response.get('catalogue_hash') == model_hash, 'runtime catalogue identity')
    require(vector(response.get('input'),6) == a, 'runtime input echo')
    require(type(response.get('mode')) is int and response['mode'] == 0, 'probe mode')
    require(response.get('ok') is success, 'response success state')
    contexts = response.get('contexts')
    require(type(contexts) is dict and set(contexts) == CONTEXTS and all(x is True for x in contexts.values()), 'context coverage/failure')
    for key in ('primitive_ok', 'schema_ok'):
        require(response.get(key) is success, key)
    for prefix in ('', 'schema_'):
        if success:
            vector(response.get(prefix+'values'),6);matrix(response.get(prefix+'jacobian'))
        else:
            require(response.get(prefix+'values',1) is None and response.get(prefix+'jacobian',1) is None, 'failed result must not expose values')


def assess(report, fresh=True):
    require(report.get('version') == VERSION and report.get('backend') in ('native','wasm'), 'study protocol')
    require(report.get('operator_version') == OPERATOR_VERSION, 'study operator identity')
    require(report.get('budgets') == {'value':VALUE_BUDGET, 'jacobian':JACOBIAN_BUDGET}, 'predeclared budgets')
    ref = reference(); models, model_hash = catalogue()
    require(report.get('reference_sha256') == sha(REFERENCE), 'reference binding')
    require(report.get('catalogue_hash') == model_hash, 'fixture catalogue binding')
    records = report.get('records')
    require(type(records) is list and len(records) == len(ref['cases']), 'complete corpus required')
    maxima = {'value':0., 'jacobian':0., 'schema_value':0., 'schema_jacobian':0.}
    for row, c in zip(records, ref['cases']):
        vector(row['request']['input'],6)
        require(row.get('id') == c['id'] and row.get('request') == {'csv':','.join(map(repr,c['input'])), 'input':c['input'], 'mode':0}, 'case request binding')
        require(type(row['request']['mode']) is int, 'integer request mode')
        r = row['response'];validate_response(r,c['input'],model_hash)
        target = oracle(c['input'],160) if fresh else c['oracle']
        expected = [float(v) for v in target['value']]
        expected_j = [float(v) for line in target['jacobian'] for v in line]
        require(expected == c['oracle']['value'] and expected_j == [v for line in c['oracle']['jacobian'] for v in line], 'fresh oracle replay disagrees with archive')
        for prefix in ('','schema_'):
            e = scaled_error(r[prefix+'values'], expected)
            j = scaled_error([v for line in r[prefix+'jacobian'] for v in line],expected_j)
            require(e <= VALUE_BUDGET and j <= JACOBIAN_BUDGET, 'numerical budget: '+c['id'])
            maxima[prefix+'value'] = max(maxima[prefix+'value'],e)
            maxima[prefix+'jacobian'] = max(maxima[prefix+'jacobian'],j)
    invalid = report.get('invalid_records')
    requests = invalid_requests()
    require(type(invalid) is list and len(invalid) == len(requests), 'complete invalid-input coverage')
    control = records[0]['response']
    for row, request in zip(invalid, requests):
        require(type(row['request'].get('parseable')) is bool, 'boolean parser contract')
        if request['parseable']:
            vector(row['request']['input'],6)
        require(row.get('request') == request, 'invalid request binding')
        r = row['response']
        if request['parseable']:
            validate_response(r,request['input'],model_hash,False)
        else:
            require(type(r) is dict and set(r) == {'ok','error'} and r.get('ok') is False and r.get('error') == 'invalid probe input or missing isolated fixtures', 'parser rejection')
        if report['backend'] == 'wasm':
            validate_response(row.get('recovery'),ref['cases'][0]['input'],model_hash)
            require(row.get('recovery') == control, 'persistent module recovery')
    return {'cases':len(records), 'contexts_per_call':len(CONTEXTS), 'invalid_cases':len(invalid), 'maximum_scaled_errors':maxima, 'fresh_decimal_precision':160 if fresh else None}



def verify_parity(wasm, native, native_path):
    # Standalone callers receive the same completeness/type checks as the CLI.
    assess(wasm, fresh=False)
    assess(native, fresh=False)
    require(wasm['backend'] == 'wasm' and native['backend'] == 'native', 'parity backends')
    require(wasm.get('native_report_sha256') == sha(native_path), 'native transcript binding')
    maximum = 0.
    for a,b in zip(wasm['records'], native['records']):
        require(a['id'] == b['id'] and a['request'] == b['request'], 'parity request identity')
        for key in ('values','schema_values','jacobian','schema_jacobian'):
            left,right=a['response'][key],b['response'][key]
            if 'jacobian' in key:
                left=[v for line in left for v in line];right=[v for line in right for v in line]
            maximum=max(maximum,scaled_error(left,right))
    require(maximum <= 2e-13, 'native/Wasm parity budget')
    require(type(wasm.get('maximum_scaled_native_parity')) in (int,float) and math.isclose(wasm['maximum_scaled_native_parity'], maximum, rel_tol=1e-12, abs_tol=1e-30), 'parity summary disagreement')
    return maximum


def run_native(binary):
    models, model_hash = catalogue()
    descriptor = json.loads(subprocess.check_output([str(binary),'--describe'],text=True,timeout=30))
    require(descriptor['models'] == models and descriptor['sha256'] == model_hash, 'native runtime descriptor')
    def call(csv):
        result = subprocess.run([str(binary),csv,'0'],capture_output=True,text=True,timeout=30)
        response = json.loads(result.stdout)
        require(result.returncode == (0 if response.get('ok') is True else 1), 'native exit status')
        return response
    records=[]
    for c in reference()['cases']:
        request={'csv':','.join(map(repr,c['input'])),'input':c['input'],'mode':0}
        records.append({'id':c['id'],'request':request,'response':call(request['csv'])})
    invalid=[{'request':r,'response':call(r['csv'])} for r in invalid_requests()]
    report={'version':VERSION,'backend':'native','operator_version':OPERATOR_VERSION,'catalogue_hash':model_hash,'reference_sha256':sha(REFERENCE),'budgets':{'value':VALUE_BUDGET,'jacobian':JACOBIAN_BUDGET},'binary_sha256':sha(binary),'records':records,'invalid_records':invalid}
    report['assessment']=assess(report)
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path)
    parser.add_argument('--verify',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--native-report',type=Path)
    args=parser.parse_args()
    require(bool(args.binary) != bool(args.verify), 'choose --binary or --verify')
    if args.binary:
        report=run_native(args.binary.resolve())
        require(args.output is not None, '--output required')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print(json.dumps(report['assessment']))
    else:
        report=read(args.verify); assessment=assess(report)
        if args.native_report:
            native=read(args.native_report);assess(native)
            assessment['maximum_scaled_native_parity']=verify_parity(report,native,args.native_report)
        print(json.dumps(assessment))
