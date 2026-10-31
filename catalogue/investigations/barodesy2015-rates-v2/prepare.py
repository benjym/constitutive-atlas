"""Prospective corpus assembly from frozen source-v2 independent reference.

This is transport/policy assembly only; constitutive equations live in the
source packet's declarative definition and independent Cartesian oracle.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/'docs/ingestion/barodesy-sand/rate-study-v2'
HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def csv(values):
    assert all(type(x) in (int,float) and math.isfinite(x) for x in values)
    return ','.join(str(float(x)) for x in values)


def prepare():
    model=read(HERE/'model.json');inputs=read(PACKET/'inputs.json')
    policy=read(PACKET/'protocol.json');reference=read(PACKET/'reference.json')
    expected={r['id']:r['oracle120']['values'] for r in reference['records']}
    order=policy['next_compiled_matrix']['parameter_order']
    def args(c):return [model['id'],csv([c['parameters'][n] for n in order]),csv(c['state']),csv(c['loading'])]
    rows=[]
    for case in inputs['valid']+inputs['additional_operational_valid']:
        values=expected[case['id']];p=case['parameters']
        if not any(case['loading']):budgets=[0.]*7
        else:
            natural=(p['c4']+p['c5']*math.hypot(*case['state'][:6]))*math.hypot(*case['loading'])/(case['state'][6]-p['emin'])
            scale=max(natural,math.hypot(*values[:6]))
            budgets=[2e-12*scale]*6+[4*math.ulp(values[6]) if values[6] else 0.]
        assert all(math.isfinite(x) for x in budgets)
        rows.append({'id':'valid:'+case['id'],'args':args(case),'expectation':{'ok':True,'values':values,'absolute_budgets':budgets,'parity_budgets':[2*b for b in budgets]}})
    control=copy.deepcopy(rows[0])
    invalids={c['id']:c for c in inputs['invalid']+inputs['additional_operational_invalid']}
    for name in policy['next_compiled_matrix']['numeric_invalid_ids']:
        rows.append({'id':'reject:'+name,'args':args(invalids[name]),'expectation':{'ok':False}})
        recovery=copy.deepcopy(control);recovery.update(id='recover:'+name,recovery_of=control['id']);rows.append(recovery)
    assert len(rows)==70 and len(expected)==38
    # Pin every source used for definition validation, code generation, C++
    # compilation and collection/assessment. Mutable coordination docs excluded.
    sources=set(PACKET/p['path'] for p in read(PACKET/'manifest.json')['files'])
    sources.add(PACKET/'manifest.json');sources.add(HERE/'prepare.py')
    sources.update(HERE/p for p in ('model.json','README.md','run_build.py'))
    for pattern in ('atlas/*.py','schemas/*.json','cpp/include/atlas/*.hpp'):
        sources.update(ROOT.glob(pattern))
    sources.update(ROOT/p for p in ('cmake/research/CMakeLists.txt','tests/research_rate_driver.cpp',
        'tools/research_rate_observations_v2.py','tools/collect_research_rates_wasm_v2.mjs','tools/research_rate_parity_v2.py'))
    pins={str(p.relative_to(ROOT)):sha(p) for p in sorted(sources)}
    return {'version':'research-instantaneous-rate-protocol-0.2','study':'barodesy2015-rates-v2',
            'model_file':str((HERE/'model.json').relative_to(ROOT)),
            'model_definition':model,'files':pins,'cases':rows,
            'policy':{'source_reference':'rate-study-v2/reference.json independent120digit Cartesian source rates; exact rational void channel',
             'stress_accuracy':'Each component <=2e-12 times max(natural stress scale, reference stress-rate norm); exactly zero on zero load.',
             'void_accuracy':'Exactly zero for zero reference; otherwise4ULP of exact-Fraction rounded reference.',
             'parity':'Twice each independent absolute budget, fixed prospectively by triangle bound.',
             'scope':'38valid +16 numeric rejection/recovery pairs +descriptor =71rows/backend;4Python-only named/type cases excluded; no finite integration, AD, or admission.',
             'failure_policy':'Retain all raw output and failed gates; do not remove cancellation case or relax budget after observation.'}}

if __name__=='__main__':
    path=HERE/'protocol.json';blob=json.dumps(prepare(),indent=2,allow_nan=False)+'\n'
    if '--check' in sys.argv:assert path.read_text()==blob,'prospective corpus changed'
    else:
        assert not path.exists(),'fresh protocol required';path.write_text(blob)
