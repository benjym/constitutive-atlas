#!/usr/bin/env python3
"""Source-only identity and equality proof. Does not call the solver."""
import argparse,ast,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent;ROOT=D.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(output):
 old=json.loads((P/'ordinary-regression-policy-v2.json').read_text());new=json.loads((P/'ordinary-regression-v6/policy.json').read_text());changes=[k for k in old if old[k]!=new[k]];assert changes==['identity','source_freeze_sha256'];assert set(old)==set(new);assert len(new['cases'])==16
 previous=(P/'ordinary-regression-v5/run.py').read_text();expected=previous.replace("D.parent/'ordinary-regression-policy-v2.json'","D/'policy.json'").replace("D.parent/'source-freeze-v2.json'","D.parent/'runtime-rebind-v1/source-freeze.json'").replace("'identity': 'md1997-ordinary-regression-v5'","'identity': 'md1997-ordinary-regression-v6'");actual=(P/'ordinary-regression-v6/run.py').read_text();assert actual==expected;ast.parse(actual)
 source=json.loads((D/'source-freeze.json').read_text());prior=json.loads((P/'source-freeze-v2.json').read_text());before=prior['source_files'];after=source['source_files'];assert len(after)==578;changed=[n for n in before if before[n]!=after.get(n)];added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after));assert changed==['cpp/include/atlas/solver.hpp'];assert added==['cmake/predictor-constraint/CMakeLists.txt','tests/fixtures/predictor-constraint/projection.json'];assert not removed
 assert sha(D/'source-freeze.json')==new['source_freeze_sha256']=='126d9bc3a221b6e0098c769eee267306d5be3d03f2b02725c824a6063243aa44'
 for n,h in after.items():assert sha(Path(source['source_directory'])/n)==h
 for c in old['cases']:assert sha(Path(source['source_directory'])/'models'/(c['model']+'.json'))==c['definition_sha256']
 # Exact historic manifests are authoritative; check all listed bytes rather than
 # regenerating new expected hashes for their dependencies.
 frozen=[]
 for rel in ['ordinary-regression-v5/manifest.json','execution-v3/manifest.json','parity-v6/manifest.json']:
  f=P/rel
  for n,h in json.loads(f.read_text()).items():assert sha(f.parent/n)==h,(rel,n)
  frozen.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f)})
 for script in [D/'preflight.py',D/'run_md.py',D/'check_rebind.py']:ast.parse(script.read_text())
 r={'status':'passed-source-only-identity-rebind','compiled_calls':False,'ordinary_case_count':len(old['cases']),'ordinary_cases_exactly_unchanged':old['cases']==new['cases'],'ordinary_numeric_gates_exactly_unchanged':old['gates']==new['gates'],'ordinary_policy_only_changed_fields':changes,'ordinary_runner_only_three_identity_path_replacements':True,'corrected_source_files_verified':len(after),'source_changed':changed,'source_added':added,'source_removed':removed,'unchanged_historical_manifests_verified':frozen,'no_new_outcome_exceptions':True,'full_compiled_acceptance':'not observed; parent/reviewer required'}
 Path(output).write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);main(p.parse_args().output)
