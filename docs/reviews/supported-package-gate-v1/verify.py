from pathlib import Path
import json,hashlib,gzip
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
for rel,h in read(P/'manifest.json')['files'].items():assert sha(P/rel)==h,rel
for rel,h in read(P/'prospective.json')['files'].items():assert sha(ROOT/rel)==h,rel
actual=json.loads(gzip.decompress((P/'actual.json.gz').read_bytes()))
policy=read(ROOT/'catalogue/laboratory-package-policy.json')
assert actual['status']=='passed' and actual['policy_sha256']==sha(ROOT/'catalogue/laboratory-package-policy.json')
assert len(actual['ordinary'])==12 and len(actual['named'])==1
assert sum(x['result']['ok']for x in actual['ordinary'])==11
assert all(x['result']['ok']for x in actual['named'])
assert {x['id']for x in actual['ordinary']}==set(policy['models'])
for mid,h in policy['models'].items():assert sha(ROOT/'models'/f'{mid}.json')==h
for e in policy['declared_failures']:
 assert sha(ROOT/e['evidence']['path'])==e['evidence']['sha256']
 row=next(x for x in actual['ordinary']if x['id']==e['model'])
 assert row['specification']==e['ordinary_specification'] and row['result']['ok'] is False
 assert row['result']['message']==e['message'] and len(row['result']['points'])==e['committed_points']
 assert row['result']['points'][0]['state']==row['specification']['initial']
assert 'tests 46'in(P/'combined.stdout').read_text() and 'fail 0'in(P/'combined.stdout').read_text()
assert not(P/'actual.stderr').read_text()
print('PASS: supported-input policy,46tests,12ordinary/1named replies; strict checker/workflow unchanged')
