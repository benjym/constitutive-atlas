"""Read-only source/corpus/transport checks; writes only owned check reports."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
from decimal import Decimal
import json,hashlib,ast
import assess_saved as A
D=Path(__file__).resolve().parent;read=A.read;sha=A.sha
f=read(D/'source-freeze.json');S=Path(f['directory']);files=f['files'];assert len(files)==594
assert {str(p.relative_to(S)):sha(p)for p in S.rglob('*')if p.is_file()}==files
for n,h in read(D/'inputs.json').items():assert sha(n)==h,n
q=read(D/'requests.json');r=read(D/'reference.json');assert q['model_sha256']==sha(S/'models/manzari-dafalias-1997-constant-m-be-v1.json')=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'
assert r['request_sha256']==sha(D/'requests.json')and r['evaluator_sha256']==sha(D/'decimal_dsl.py')and r['policy_sha256']==sha(D/'POLICY.md')and r['generator_sha256']==sha(D/'generate.py')
assert len(q['endpoints'])==56 and len({(e['column'],e['level'],e['sign'])for e in q['endpoints']})==56
for e in q['endpoints']:
 col=e['column'];level=e['level'];h=(5e-11 if 7<=col<=9 else 1e-6)/(2**level);assert float.fromhex(e['step_hex'])==h
 assert [float.fromhex(x)for x in e['direction_hex']]==[float(j==col)for j in range(14)]
for prec in ['80','120']:assert len(r['data'][prec]['residuals'])==56 and len(r['data'][prec]['secants'])==28 and all(len(row)==14 for rows in r['data'][prec].values()for row in rows)
assert read(D/'synthetic-results.json')['passed']is True and read(D/'assessor-test-results.json')['passed']is True
for p in D.glob('*.py'):ast.parse(p.read_text())
for p in [D/'decimal_dsl.py',D/'generate.py',D/'assess_saved.py']:
 tree=ast.parse(p.read_text())
 for n in ast.walk(tree):
  if isinstance(n,(ast.Import,ast.ImportFrom)):
   name=n.module if isinstance(n,ast.ImportFrom)else n.names[0].name
   assert not(name or'').startswith('atlas')
  assert not(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in ['eval','exec'])
M=D/'synthetic-transport'
for typ,process in [('direct','process.json'),('ctest','ctest-process.json')]:
 result=A.assess(D/'requests.json',D/'reference.json',M/process,M/'binding.json',sha(M/'binding.json'));assert result['passed']is True and result['purpose']=='synthetic-test-only'and result['comparisons']==588 and len(result['results'])==588
 (D/('synthetic-'+typ+'-assessment.json')).write_text(json.dumps(result,indent=2)+'\n')
result=dict(identity='native-decimal-reference-phase1-source-checks-v1',passed=True,source_files=594,source_unchanged=True,synthetic_evaluator_checks=read(D/'synthetic-results.json')['checks'],synthetic_assessor_cases=read(D/'assessor-test-results.json')['cases'],endpoints=56,secants=28,rows=14,columns=14,levels=2,reference_stability=r['precision_max_scaled_difference'],saved_mock_comparisons_per_provenance=588,actual_native_ad_observations=0,builds=0,compiled_calls=0,independent_review_required=True)
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
