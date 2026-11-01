"""Saved-only reference replay: no generation, candidate, author or compiled calls."""
from pathlib import Path
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def verify():
 load=lambda p:json.loads(p.read_text())
 for name in ['source-pins.json','prospective-freeze.json','assessor-pins.json','manifest.json']:
  for path,h in load(P/name)['files'].items():checked_receipt(ROOT,(P/name).relative_to(ROOT),path,h)
 result=module('saved_sanisand_reference_assessor',P/'assess.py').assess(P)
 assert result==load(P/'assessment.json')and result['reference_adequacy_pass']
 algebra=module('saved_sanisand_reference_algebra',P/'algebra_checks.py').verify()
 assert algebra==json.loads(load(P/'algebra-process.json')['stdout'])and algebra['checks']==153
 for n in ['p50-t12','p80-t8','p80-t10','p80-t12']:
  assert load(P/f'generation-{n}-process.json')['returncode']==0
  assert len((P/f'generation-{n}.log').read_text().splitlines())==27
  assert not(P/f'generation-{n}.stderr').read_text()
 for name in ['assessment','corruption-tests','algebra']:assert load(P/(name+'-process.json'))['returncode']==0
 assert 'Ran 8 tests' in load(P/'corruption-tests-process.json')['stderr']
 assert result['candidate_calls']==0 and result['scientific_signature']is None
 return {k:result[k]for k in ['reference_adequacy_pass','cases','samples_per_case','plastic_samples','nonzero_fabric_endpoints','maximum_arithmetic_scaled_difference','maximum_fine_medium_scaled_difference','maximum_scaled_yield_drift','candidate_calls','scientific_signature']}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
