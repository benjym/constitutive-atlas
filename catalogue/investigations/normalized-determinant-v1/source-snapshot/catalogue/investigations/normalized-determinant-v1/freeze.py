"""Freeze independent literal references and a cache-free executable closure."""
import copy,hashlib,json,shutil,sys,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REFERENCE=ROOT/'docs/reviews/normalized-determinant-reference-v1'
REVIEW=ROOT/'docs/reviews/normalized-determinant-core-v1'
ALLOWED={'.py','.hpp','.cpp','.md','.json','.txt','.mjs','.tsv'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(p):return p.suffix in ALLOWED and not any(x.startswith('.')or x=='__pycache__'for x in p.parts)
def selected(base):return {p for p in base.rglob('*')if p.is_file()and allowed(p.relative_to(base))}
def protocol():
 compact=json.loads((REFERENCE/'cases.json').read_text());fixtures=copy.deepcopy(compact['cases']);supplementary=[]
 for c in fixtures:
  if c['expectation'].get('reason')=='final-derivative-overflow'and c['primal_expectation']['ok']:
   new=copy.deepcopy(c);new.update(id='late-overflow/'+c['id'],seeds=[list(reversed(row))for row in c['seeds']],origin={'reference_case_id':c['id'],'transformation':'reverse all38seed columns; same independent overflow direction evaluated last'})
   new['expectation']={'ok':False,'reason':'final-derivative-overflow'};supplementary.append(new)
 fixtures+=supplementary;control=next(c for c in fixtures if c['expectation']['ok']);cases=[]
 assert fixtures[0]['id']==control['id'],'first fixture must be valid recovery control'
 for case in fixtures:
  cases.append(copy.deepcopy(case))
  if not case['expectation']['ok']:
   recovery=copy.deepcopy(control);recovery.update(id='recovery/'+case['id'],recovery_of=control['id'],after_rejection=case['id']);cases.append(recovery)
 return {'version':'normalized-determinant-primitive-protocol-v1','unique_reference_cases':len(compact['cases']),'supplementary_permuted_cases':len(supplementary),'rejection_recovery_pairs':sum(not c['expectation']['ok']for c in fixtures),'ordered_calls':len(cases),'reference_cases_sha256':sha(REFERENCE/'cases.json'),'cases':cases,'acceptance':'Exact certified bits for primal and all38derivative columns; rejected outputs unchanged; complete backend parity; no tolerance','scope':'Numerical primitive only; no DSL/model admission'}
def request_text(p):return ''.join(c['id']+'\t'+','.join(c['values'])+'\t'+','.join(v for row in c['seeds']for v in row)+'\n'for c in p['cases'])
def sources():
 paths=selected(REFERENCE)|selected(REVIEW)
 paths.update(ROOT/p for p in ('docs/NORMALIZED_DETERMINANT.md','atlas/__init__.py','atlas/numerics/__init__.py','atlas/numerics/determinant.py','atlas/numerics/normalized_determinant.py','tests/test_normalized_determinant.py'))
 paths.update(p for p in (ROOT/'cpp/include/atlas').rglob('*.hpp')if allowed(p.relative_to(ROOT)))
 paths.update(HERE/p for p in ('README.md','driver.cpp','CMakeLists.txt','freeze.py','run_build.py','collect.py','collect_wasm.mjs','assess.py','verify_study.py','replay.py','protocol.json','requests.tsv','coordinator-reference-replay.json'))
 assert all(allowed(p.relative_to(ROOT))for p in paths)
 return sorted(paths)
def main():
 assert not (HERE/'prospective-freeze.json').exists();assert not (HERE/'source-snapshot').exists()
 p=protocol();(HERE/'protocol.json').write_text(json.dumps(p,indent=2,allow_nan=False)+'\n');(HERE/'requests.tsv').write_text(request_text(p))
 pins={str(p.relative_to(ROOT)):sha(p)for p in sources()}
 for name,pin in pins.items():
  dst=HERE/'source-snapshot'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst);assert sha(dst)==pin
 (HERE/'prospective-freeze.json').write_text(json.dumps({'version':'normalized-determinant-primitive-freeze-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled_observations_at_freeze':False,'files':pins,'cache_or_bytecode_included':False,'gate':'Exact certified bits and unchanged rejection output; no tolerance changes'},indent=2)+'\n')
 print('frozen',len(pins),'source files,',len(p['cases']),'ordered calls')
if __name__=='__main__':main()
